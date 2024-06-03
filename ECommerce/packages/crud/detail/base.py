from collections import OrderedDict
import copy
import requests

from rest_framework import serializers

from zango.core.api import get_api_response
from zango.core.utils import get_datetime_str_in_tenant_timezone
from zango.core.utils import get_package_url

from ..mixin import CrudRequestMixin
from ..table.column import ModelCol, SelectCol, StringCol, NumericCol
from ..table.serializers import StringRelatedMeta


class BaseDetail(CrudRequestMixin):
    title = None

    def __init__(self, request=None, **kwargs):
        self.request = request
        self.crud_view_instance = kwargs.get("crud_view_instance", None)
        self.table_obj = kwargs.get("table_obj", None)
        self.field_names = []
        self._fields = []

        if hasattr(self, "Meta") and hasattr(self.Meta, "fields"):
            self.initialize_fields()

    def initialize_fields(self):
        explicit_cols = (
            []
        )  # user defined columns consist of ModelCol and StringCol (custom field)
        explicit_col_names = []  # user defined column names
        not_allowed_col_names = []  # not allowed column names

        # Walk through the MRO to get attributes from both parent and child classes
        detail_class_attrs = OrderedDict()
        for cls in reversed(self.__class__.mro()):
            # Use dir() to get all attributes of the class
            class_attributes = [
                attr for attr in cls.__dict__ if not attr.startswith("__")
            ]

            # Use getattr() to get the values of the attributes
            attribute_values = {attr: getattr(cls, attr) for attr in class_attributes}

            # Update the dictionary with the values
            detail_class_attrs.update(attribute_values)

        # Constructing fields
        for attr_name, attr_value in detail_class_attrs.items():
            try:
                # Updating the field name
                if attr_value.__class__ == ModelCol:
                    attr_value.update_model_field(
                        self.table_obj.model._meta.get_field(attr_name)
                    )
                elif attr_value.__class__ == StringCol:
                    attr_value.update_model_name(attr_name)

                # Check if the field is allowed based on the user role
                if attr_value.__class__ in [ModelCol, StringCol]:
                    if (not attr_value.user_roles) or (
                        attr_value.user_roles
                        and self.table_obj.user_role.name in attr_value.user_roles
                    ):
                        explicit_cols.append((attr_name, attr_value))
                        explicit_col_names.append(attr_name)
                    else:
                        not_allowed_col_names.append(attr_name)

            except Exception as e:
                print(e)

        # By default, the list of fields is obtained from the Meta class of the table_obj.
        # If the detail view class specifies its own list of fields in its Meta class,
        # then that list will be used instead of the table_obj's fields.
        fields_names = copy.deepcopy(self.table_obj.Meta.fields)
        if hasattr(self, "Meta"):
            detail_view_fields = getattr(self.Meta, "fields", [])
            if detail_view_fields:
                fields_names = copy.deepcopy(detail_view_fields)

        self.field_names = fields_names

        if fields_names == "__all__":
            for f in self.table_obj.model._meta.fields:
                if (
                    f.name not in explicit_col_names
                    and f.name not in not_allowed_col_names
                ):
                    col = ModelCol()
                    col.update_model_field(f)
                    explicit_cols.append((f.name, col))
        else:
            self._fields = fields_names
            for f in self._fields:
                if f not in explicit_col_names and f not in not_allowed_col_names:
                    col = ModelCol()
                    field = self.table_obj.model._meta.get_field(f)
                    col.update_model_field(field)
                    explicit_cols.append((f, col))

        self._fields = explicit_cols

    def add_field(self, field_name, field):
        """
        This method is used to dynamically add a field to the detail view.

        :param field_name: The name of the field to be added
        :param field: The field object to be added
        """

        if field.__class__ == ModelCol:
            field.update_model_field(self.table_obj.model._meta.get_field(field_name))
            self._fields.append((field_name, field))
            if hasattr(self, "Meta") and hasattr(self.Meta, "fields"):
                if isinstance(self.field_names, list):
                    self.field_names.append(field_name)

        elif field.__class__ == StringCol:
            field.update_model_name(field_name)
            self._fields.append((field_name, field))

    def get_object_pk(self):
        return self.request.GET.get("pk")

    def get_object(self, pk):
        table_queryset = self.table_obj.get_table_data_queryset()
        obj = table_queryset.get(pk=pk)
        return obj

    def get_title(self, obj, object_data):
        if not self.title:
            return str(obj)

        return object_data.get(self.title, str(obj))

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

    def get_auditlog_details(self, obj):
        field_dict = {
            "created_at": {
                "display_name": "Created At",
                "value": get_datetime_str_in_tenant_timezone(
                    obj.created_at, self.request.tenant
                ),
            },
            "created_by": {
                "display_name": "Created By",
                "value": obj.created_by.name if obj.created_by else "System",
            },
            "modified_by": {
                "display_name": "Modified By",
                "value": obj.modified_by.name if obj.modified_by else "NA",
            },
            "modified_at": {
                "display_name": "Modified At",
                "value": (
                    get_datetime_str_in_tenant_timezone(
                        obj.modified_at, self.request.tenant
                    )
                    if obj.modified_by and obj.modified_at
                    else "NA"
                ),
            },
        }

        return field_dict

    def get_general_details(self, obj, object_data):
        field_details = {}
        if hasattr(self, "Meta") and hasattr(self.Meta, "fields"):
            table_metadata = self.get_table_metadata()
        else:
            table_metadata = self.table_obj.get_table_metadata()

        columns = table_metadata["columns"]
        for column in columns:
            field_name = column["name"]
            if field_name in object_data:
                field_dict = {}
                field_dict.update(column)
                field_dict["value"] = object_data[field_name]
                field_details[field_name] = field_dict

        auditlog_details = self.get_auditlog_details(obj)
        field_details.update(auditlog_details)

        general_deatails = {"fields": field_details}

        return general_deatails

    def get_workflow_details(self, obj):
        workflow_obj = self.get_workflow_object(obj)
        if not workflow_obj:
            return {}

        workflow_details = {}
        current_status, current_status_meta = workflow_obj.get_current_status(
            serialized=True
        )
        if current_status:
            workflow_details["current_status"] = current_status
            workflow_details["current_status_meta"] = current_status_meta

        next_transitions = workflow_obj.get_next_transitions(serialized=True)
        workflow_details["next_transitions"] = next_transitions

        workflow_transactions = workflow_obj.get_workflow_transactions()
        workflow_details["workflow_transactions"] = workflow_transactions

        workflow_details["tag_details"] = workflow_obj.get_tags_details()

        return workflow_details

    def get_table_metadata(self):
        columns = [
            f[1].get_col_metadata(self.request, col_index)
            for col_index, f in enumerate(self._fields)
        ]
        metadata = {
            "columns": columns,
        }
        return metadata

    def get_columns(self):
        columns = self.get_table_metadata()["columns"]
        return [c["name"] for c in columns]

    def post_process_data(self, data):
        result = []
        columns = self.get_columns()
        for row in data:
            obj, serialized = row["obj"], row["serialized"]
            new_row = {}
            for col in columns:
                col_getval = getattr(self, f"{col}_getval", None)
                if col_getval:
                    new_row[col] = col_getval(obj)
                else:
                    if col in serialized:
                        new_row[col] = serialized[col]

                new_row[col] = new_row[col] if new_row[col] is not None else "NA"

            new_row["pk"] = obj.pk

            result.append(new_row)
        return result

    def get_serializer(self):
        class Meta:
            model = self.table_obj.model
            if hasattr(self, "Meta") and hasattr(self.Meta, "fields"):
                fields = self.field_names
            else:
                if self.table_obj.Meta.fields == "__all__":
                    fields = [f.name for f in self.table_obj.model._meta.fields]
                else:
                    fields = self.table_obj.Meta.fields
            fields = list(
                set(fields + ["created_at", "modified_at", "created_by", "modified_by"])
            )

        serializer_name = f"{self.table_obj.model.__class__.__name__}Serializer"
        serializer_class = StringRelatedMeta(
            serializer_name,
            (serializers.ModelSerializer,),
            {"Meta": Meta, "metadata": self.get_table_metadata()},
        )
        return serializer_class

    def is_activity_timeline_visible(self, obj):
        """
        Check if the activity timeline is visible for the detail view.

        This function can be overridden in subclasses to customize the visibility
        of the activity timeline based on specific conditions or business logic.

        By default, the activity timeline is visible.

        Args:
            obj: Corresponding model instance

        Returns:
            bool: True if the activity timeline should be visible, False otherwise.
        """

        show_activity_timeline = True
        meta_class = getattr(self, "Meta", None)
        if meta_class:
            show_activity_timeline = getattr(meta_class, "show_activity_timeline", True)

        return show_activity_timeline

    def get_detail_view_config(self, obj):
        config_dict = {}
        config_dict["show_activity_timeline"] = self.is_activity_timeline_visible(obj)

        return config_dict

    def call_enabled(self):
        try:
            resp = requests.get(
                get_package_url(
                    self.request,
                    "telephony/orm/api/?action=get_config",
                    "communication",
                )
            )
            if resp.status_code != 200:
                return False
            return True
        except Exception:
            return False

    def get_telephony_contact(self, obj):
        """
        Override this method and return the phone number to be used in the call
        """
        return ""

    def fetch_item_details(self):
        pk = self.get_object_pk()

        obj = self.get_object(pk=pk)

        detail_view_fields = getattr(self, "field_names", [])
        if detail_view_fields:
            serializer = self.get_serializer()

            serialized_data = serializer(obj).data
            raw_data = [{"obj": obj, "serialized": serialized_data}]
            object_data = self.post_process_data(raw_data)[0]
        else:
            serializer = self.table_obj.get_serializer()
            serialized_data = serializer(obj).data
            raw_data = [{"obj": obj, "serialized": serialized_data}]
            object_data = self.table_obj.post_process_data(raw_data)[0]

        object_data.pop("row_actions", None)

        item_details = {"pk": pk}
        item_details["title"] = self.get_title(obj, object_data)
        item_details["general_details"] = self.get_general_details(obj, object_data)
        item_details["workflow_details"] = self.get_workflow_details(obj)
        item_details["configurations"] = self.get_detail_view_config(obj)
        item_details["telephony_details"] = {}
        if self.call_enabled():
            item_details["telephony_details"][
                "phone_number"
            ] = self.get_telephony_contact(obj)
            item_details["telephony_details"]["call_enabled"] = True
        return item_details

    def get_context_data(self, context, **kwargs):
        """
        This method can be overridden for providing additional context data for the detail view.

        Parameters:
            context (dict): The context provided by the CRUD View.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: The updated context dictionary.
        """

        return context

    def get(self, request, *args, **kwargs):
        action = self.get_request_action(request)

        if action == "render_to_string" and self.crud_view_instance:
            context = self.crud_view_instance.get_context_data(**kwargs)

        if action == "fetch_item_details":
            data = self.fetch_item_details()
            return get_api_response(success=True, response_content=data, status=200)
