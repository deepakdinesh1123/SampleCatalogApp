from __future__ import annotations

import copy
import json
from collections import OrderedDict


from django.db.models import Q
from django.db import models
from django.http import JsonResponse
from rest_framework import serializers

from zango.core.utils import get_current_role
from zango.apps.dynamic_models.fields import ZForeignKey, ZOneToOneField
from zango.core.tasks import zango_task_executor
from zango.core.api import get_api_response

from .serializers import StringRelatedMeta
from .column import ModelCol, StringCol, NumericCol, SelectCol, field_map
from .utils import process_date_range, process_datetime_range_with_timezone
from ..mixin import CrudRequestMixin


class ModelTable(CrudRequestMixin):
    """
    Supports table creation for a model. The model is specified in the Meta class.
    The fields of the model are specified in the fields attribute. For including all
    the fields of the model use __all__.
    Custom fields can also be specified directly as class attributes as Column Object.
    """

    pagination = 10
    fields = []
    custom_fields = []
    row_actions_edit_form = None
    row_actions_edit_roles = []
    row_actions_description = "Edit"

    def __init__(self, request=None, **kwargs):
        current_user_role = get_current_role()
        self.user_role = current_user_role or kwargs.get("user_role")
        self.request = request
        self.crud_view_instance = kwargs.get("crud_view_instance")
        self.model = getattr(
            self.Meta,
            "model",
            (
                self.crud_view_instance.model
                if self.crud_view_instance and hasattr(self.crud_view_instance, "model")
                else None
            ),
        )
        self.serializer_class = getattr(self.Meta, "serializer_class", None)
        self.native_fields = [f.name for f in self.model._meta.fields]
        self.table_actions = getattr(self, "table_actions", [])
        self.row_actions = getattr(
            self,
            "row_actions",
            [
                {
                    "name": "Edit",
                    "key": "edit",
                    "description": self.row_actions_description,
                    "type": "form",
                    "form": self.row_actions_edit_form,
                    "roles": self.row_actions_edit_roles,
                }
            ],
        )
        explicit_cols = []
        explicit_col_names = []
        not_allowed_col_names = []

        # Walk through the MRO to get attributes from both parent and child classes
        table_class_attrs = OrderedDict()
        for cls in reversed(self.__class__.mro()):
            # Use dir() to get all attributes of the class
            class_attributes = [
                attr for attr in cls.__dict__ if not attr.startswith("__")
            ]

            # Use getattr() to get the values of the attributes
            attribute_values = {attr: getattr(cls, attr) for attr in class_attributes}

            # Update the dictionary with the values
            table_class_attrs.update(attribute_values)

        for attr_name, attr_value in table_class_attrs.items():
            try:
                if attr_value.__class__ == ModelCol:
                    attr_value.update_model_field(self.model._meta.get_field(attr_name))
                elif attr_value.__class__ in [StringCol, NumericCol, SelectCol]:
                    attr_value.update_model_name(attr_name)
                    choices_method = getattr(self, f"{attr_name}_get_choices", None)
                    col_properties_to_update = {
                        "choices": {"choices_method": choices_method}
                    }
                    attr_value.update_properties(request, col_properties_to_update)

                if attr_value.__class__ in [ModelCol, StringCol, NumericCol, SelectCol]:
                    if (not attr_value.user_roles) or (
                        attr_value.user_roles
                        and self.user_role.name in attr_value.user_roles
                    ):
                        explicit_cols.append((attr_name, attr_value))
                        explicit_col_names.append(attr_name)
                    else:
                        not_allowed_col_names.append(attr_name)

            except Exception as e:
                print(e)
        if self.Meta.fields == "__all__":
            for f in self.model._meta.fields:
                if (
                    f.name not in explicit_col_names
                    and f.name not in not_allowed_col_names
                ):
                    col = ModelCol()
                    col.update_model_field(f)
                    explicit_cols.append((f.name, col))
        else:
            self._fields = self.Meta.fields
            for f in self._fields:
                if f not in explicit_col_names and f not in not_allowed_col_names:
                    col = ModelCol()
                    field = self.model._meta.get_field(f)
                    col.update_model_field(field)
                    explicit_cols.append((f, col))
        self._fields = explicit_cols
        self.actions_metadata = self.get_actions_metadata()
        self.table_metadata = self.get_table_metadata()

    def can_include_row_action(self, request, row, obj):
        roles = row.get("roles", [])
        can_perform = True
        if hasattr(self, f"can_perform_row_action_{row['key']}"):
            can_perform_method = getattr(self, f"can_perform_row_action_{row['key']}")
            can_perform = can_perform_method(request, obj)

        if ((not roles) or (roles and self.user_role.name in roles)) and can_perform:
            return True
        return False

    def get_row_actions(self, request, obj):
        row_actions_list = []
        row_actions_dict = copy.deepcopy(self.row_actions)
        for row in row_actions_dict:
            if self.can_include_row_action(request, row, obj):
                if row["type"] == "form":
                    row.pop("form", None)
                row_actions_list.append(row)

        return row_actions_list

    def get_actions_metadata(self):
        actions = {"table": []}

        for action in self.table_actions:
            roles = action.get("roles", [])
            if (not roles) or (roles and self.user_role.name in roles):
                actions["table"].append(action)
        return actions

    def get_table_metadata(self) -> list[dict]:
        """
        Returns the metadata of the table to help build the table UI,
        excluding the data rows.

        Args:
            self (Table): The current instance of the Table class.
        Returns:
            metadata (list[dict]): A list of dictionaries representing the metadata
                of the table.
        """
        row_selector = getattr(self.Meta, "row_selector", {})
        row_selector_enabled = row_selector.get("enabled", False)
        card_primary_fields = getattr(self.Meta, "card_primary_fields", [])

        columns = [
            f[1].get_col_metadata(
                self.request, col_index + 1 if row_selector_enabled else col_index
            )
            for col_index, f in enumerate(self._fields)
        ]
        metadata = {
            "pagination": self.pagination,
            "columns": columns,
            "row_selector": row_selector,
            "actions": self.actions_metadata,
            "card_primary_fields": card_primary_fields,
            # "actions": self.get_actions_metadata()
        }
        return metadata

    def get_serializer(self):
        if self.serializer_class:
            return self.serializer_class

        class Meta:
            model = self.model
            if self.Meta.fields == "__all__":
                fields = [f.name for f in self.model._meta.fields]
            else:
                fields = self.Meta.fields
            fields = list(
                set(fields + ["created_at", "modified_at", "created_by", "modified_by"])
            )

        serializer_name = f"{self.model.__class__.__name__}Serializer"
        serializer_class = StringRelatedMeta(
            serializer_name,
            (serializers.ModelSerializer,),
            {"Meta": Meta, "metadata": self.get_table_metadata()},
        )
        return serializer_class

    def get_workflow_object(self, obj):
        workflow_class = getattr(self.crud_view_instance, "workflow", None)
        if workflow_class:
            workflow_object = workflow_class(
                request=self.request,
                object_instance=obj,
                crud_view_instance=self.crud_view_instance,
            )
            return workflow_object

        return None

    def get_workflow_current_status(self, workflow_obj):
        current_status, current_status_meta = workflow_obj.get_current_status(
            serialized=True
        )
        if current_status:
            return current_status_meta

        return {}

    def post_process_data(self, data):
        result = []
        columns = self.get_columns()
        i = 0
        for row in data:
            obj, serialized = row["obj"], row["serialized"]
            workflow_obj = self.get_workflow_object(obj)
            new_row = {}
            for col in columns:
                col_getval = getattr(self, f"{col}_getval", None)
                if col_getval:
                    new_row[col] = col_getval(obj)
                else:
                    new_row[col] = serialized[col]

                new_row[col] = new_row[col] if new_row[col] is not None else "NA"

            new_row["pk"] = obj.pk
            new_row["row_actions"] = self.get_row_actions(self.request, obj)
            new_row["field_title"] = str(obj)
            if workflow_obj:
                new_row["workflow_status"] = self.get_workflow_current_status(
                    workflow_obj
                )
            result.append(new_row)
        return result

    def get_columns(self):
        columns = self.get_table_metadata()["columns"]
        return [c["name"] for c in columns]

    def get_searchable_columns(self):
        columns = self.get_table_metadata()["columns"]
        searchable_cols = [c["name"] for c in columns if c["searchable"]]
        return searchable_cols

    def get_col_search_query(self, col, col_metadata, search_query, rel_obj_attr):
        col_type = field_map[col_metadata["type"].__name__]["type"]
        if col_type == "string":
            if rel_obj_attr is not None:
                return Q(**{f"{col}__{rel_obj_attr}__iexact": search_query})
            return Q(**{f"{col}__iexact": search_query})

        elif col_type == "date":
            try:
                date_query = json.loads(search_query)
                date_range = process_date_range(date_query["start"], date_query["end"])
                return Q(**{f"{col}__range": date_range})
            except:
                return Q()

        elif col_type == "datetime":
            try:
                date_query = json.loads(search_query)
                date_range = process_datetime_range_with_timezone(
                    date_query["start"], date_query["end"]
                )
                return Q(**{f"{col}__range": date_range})
            except:
                return Q()

        return Q()

    def get_col_q_obj(self, col_metadata, col, query_value, rel_obj_attr=None):
        custom_search_fn = getattr(self, f"{col}_Q_obj", None)
        col_search = col_metadata.get("search_query")
        search_query = col_metadata.get("search_query") or query_value
        if not search_query:
            return Q()

        if custom_search_fn:
            return custom_search_fn(search_query)
        else:
            if col in self.native_fields:
                # query_op = "iexact" if col_search else "icontains"
                if col_search:
                    return self.get_col_search_query(
                        col, col_metadata, search_query, rel_obj_attr
                    )

                if rel_obj_attr is not None:
                    return Q(**{f"{col}__{rel_obj_attr}__icontains": search_query})

                return Q(**{f"{col}__icontains": search_query})
            else:
                return (
                    Q()
                )  # for custom fields search will only work if custom search is implemented

    def search_across_all_fields(self, objects, query_value):
        """
        Returns a queryset of the model where any of its fields contains the query_value.
        """
        for field in objects.model._meta.fields:
            for column in self.table_metadata["columns"]:
                if field.name == column["name"]:
                    column["type"] = type(field)
        q_objects = Q()  # Initialize the Q object
        col_search_q_objects = Q()

        for col in self.table_metadata["columns"]:
            if col.get("searchable", False):
                col_type = col["type"]
                col_name = col["name"]
                related_attr = col.get("related_object_attribute")
                col_search = col.get("search_query")
                if col_type in [
                    ZOneToOneField,
                    ZForeignKey,
                    models.ForeignKey,
                    models.OneToOneField,
                ]:
                    if related_attr:
                        col_q_obj = self.get_col_q_obj(
                            col, f"{col_name}", query_value, rel_obj_attr=related_attr
                        )
                    else:
                        col_q_obj = self.get_col_q_obj(
                            col, col_name, query_value, rel_obj_attr="id"
                        )
                else:
                    col_q_obj = self.get_col_q_obj(col, col_name, query_value)

                if col_search:
                    col_search_q_objects &= col_q_obj
                else:
                    q_objects |= col_q_obj

        filter_q_object = q_objects & col_search_q_objects
        return objects.filter(filter_q_object)

    def get_sorted_objects(self, objects, sort_col, sort_type):
        columns = self.get_columns()
        custom_sort_fn = getattr(self, f"{sort_col}_get_sorted_objects", None)
        if custom_sort_fn:
            return custom_sort_fn(objects, sort_type)
        else:
            if sort_type == "asc":
                sort = f"-{sort_col}"
            else:
                sort = f"{sort_col}"
            return objects.order_by(sort)

    def get_table_data_queryset(self):
        """
        Get the queryset for the table data.

        This method can be overridden to provide a custom queryset for the table data.

        Returns:
            QuerySet: The queryset containing objects from the model.
        """
        objects = self.model.objects.all()
        return objects

    def get_data(self, request) -> list[dict]:
        objects = self.get_table_data_queryset()
        objects = self.search_across_all_fields(
            objects, request.GET.get("search[value]")
        )
        # Sorting the Objects
        sort_by_col = request.GET.get("order[0][column]", None)
        if sort_by_col:
            sort_type = request.GET.get("order[0][dir]")
            col_index = int(sort_by_col)
            row_selector = getattr(self.Meta, "row_selector", {})
            row_selector_enabled = row_selector.get("enabled", False)
            sort_col_index = col_index - 1 if row_selector_enabled else col_index
            sort_col = self.get_columns()[sort_col_index]
            objects = self.get_sorted_objects(objects, sort_col, sort_type)
            return objects
        if not objects.query.order_by:
            objects = objects.order_by("-modified_at")
        return objects

    def perform_row_action(self, request):
        action_key = request.GET.get("action_key")
        action_dict = [a for a in self.row_actions if a["key"] == action_key]
        if not action_dict:
            success = False
            response = {"message": "No action found"}
            return success, response

        action_dict = action_dict[0]
        obj_pk = request.POST.get("pk")
        obj = self.model.objects.get(pk=obj_pk)

        # TODO: Handle if process function doesn't exists
        perform_row_action_method = getattr(
            self, f"process_row_action_{action_dict['key']}"
        )
        return perform_row_action_method(request, obj)

    def get_datatables_parameters(self):
        """
        Retrieves the pagination and draw parameter of the datatable from the given request.

        Args:
            request (HttpRequest): The request object containing the query parameters.

        Returns:
            draw (int): The draw counter for the datatables plugin.
            start (int): The starting index for the data to be fetched.
            length (int): The number of records to be fetched.
        """
        draw = int(self.request.GET.get("draw", 0))
        start = int(self.request.GET.get("start", 0))
        length = int(self.request.GET.get("length", 10))
        return draw, start, length

    def get_table_data(self):
        all_objects = self.get_data(self.request)
        draw, start, length = self.get_datatables_parameters()
        objects = all_objects[start : start + length]
        serializer = self.get_serializer()
        serializer_instance = serializer(objects, many=True)
        data = serializer_instance.data
        result = []
        i = 0
        for d in data:
            result.append({"obj": objects[i], "serialized": d})
            i += 1
        data = self.post_process_data(result)

        return {
            "draw": draw,
            "recordsTotal": all_objects.count(),
            "recordsFiltered": all_objects.count(),
            "data": data,
        }

    def get_context_data(self, context, **kwargs):
        """
        This method can be overridden for providing additional context data for the table view.

        Parameters:
            context (dict): The context provided by the CRUD View.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The updated context dictionary.
        """

        return context

    def initiate_export(self, request):
        try:
            request_data = {
                "path": request.path,
                "user_id": request.user.id if request.user else None,
                "user_role_id": self.user_role.id if self.user_role else None,
                "params": request.GET,
            }
            export_metadata = {
                "request_data": request_data,
                "tenant_name": request.tenant.name,
            }

            # TODO: Change this to API
            from ....packages.frame.downloads.models import ExportJob

            current_user_role = get_current_role()
            export_job_obj = ExportJob.objects.create(
                user=(
                    request.user if current_user_role.name != "AnonymousUsers" else None
                ),
                export_type="xlsx",
                export_metadata=export_metadata,
            )
            task_res = zango_task_executor.delay(
                request.tenant.name,
                "packages.crud.downloads.tasks.export_table",
                request_data,
                export_job_obj.id,
            )
            export_job_obj.celery_task_id = task_res.id
            export_job_obj.save()
            return True, export_job_obj.celery_task_id
        except Exception as e:
            return False, str(e)

    def get(self, request, *args, **kwargs):
        action = self.get_request_action(request)

        if action == "get_table_data":
            data = self.get_table_data()
            return JsonResponse(data)

        elif action == "export_table":
            success, result = self.initiate_export(request)
            if success:
                return get_api_response(
                    success=success,
                    response_content={
                        "task_id": result,
                        "message": "Download initiated successfully",
                    },
                    status=200,
                )

            return get_api_response(
                success=success,
                response_content={
                    "message": "Unable to initiate download. Please try again later.",
                },
                status=400,
            )
