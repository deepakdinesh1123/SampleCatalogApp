import json
from typing import Any, Dict

from django.views.generic import TemplateView
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache


from zango.core.api import get_api_response
from ...packages.frame.decorator import add_frame_context
from .mixin import CrudRequestMixin
from .forms import BaseForm


@method_decorator(never_cache, name="dispatch")
class BaseCrudView(TemplateView, CrudRequestMixin):
    table_template = "crud/table.html"
    detail_template = "crud/detail.html"

    def get_request_view(self):
        """
        Returns the value of the 'view' parameter from the GET request.

        :param self: The current instance of the class.
        :return: The value of the 'view' parameter from the GET request.
        """
        view = self.request.GET.get("view", None)
        return view

    def get_template_names(self):
        view = self.get_request_view()
        if view == "table":
            return [self.table_template]

        elif view == "detail":
            return [self.detail_template]
        return [self.table_template]

    def get_table_obj(self):
        return self.table(request=self.request, crud_view_instance=self)

    def get_detail_obj(self, table_obj):
        if hasattr(table_obj.Meta, "detail_class"):
            detail_class = table_obj.Meta.detail_class

            return detail_class(
                request=self.request, crud_view_instance=self, table_obj=table_obj
            )

        from .detail.base import BaseDetail

        return BaseDetail(
            request=self.request, crud_view_instance=self, table_obj=table_obj
        )

    def get_workflow_obj(self, **kwargs):
        workflow_class = getattr(self, "workflow", None)
        if workflow_class:
            workflow_object = workflow_class(
                request=self.request,
                crud_view_instance=self,
                object_instance=kwargs.get("object_instance", None),
            )
            return workflow_object

        return None

    def get_row_actions(self, table_obj):
        return table_obj.row_actions

    def get_form(self, data=None, files=None, instance=None):
        action_type = self.request.GET.get("action_type")
        if action_type == "row":
            pk = self.request.GET.get("pk")
            action_key = self.request.GET.get("action_key")

            table_obj = self.get_table_obj()

            row_actions = self.get_row_actions(table_obj)

            row_action = [r for r in row_actions if r["key"] == action_key]

            if not row_action:
                raise ImproperlyConfigured(
                    "No row action found or action is not allowed"
                )

            row_action = row_action[0]

            action_form = row_action.get("form")
            if not action_form:
                raise ImproperlyConfigured("Form is not configured for this action")

            if not instance:
                model = action_form.Meta.model
                instance = model.objects.get(pk=pk)

            can_perform_action = table_obj.can_include_row_action(
                self.request, row_action, instance
            )
            if not can_perform_action:
                raise PermissionDenied(f"Can not perform action {row_action['name']}")
            return action_form(
                data=data, files=files, instance=instance, crud_view_instance=self
            )

        return self.form(data=data, files=files, crud_view_instance=self)

    def get_form_errors(self, form):
        form_errors = json.loads(form.errors.as_json())
        res = {}
        for field_name, errors in form_errors.items():
            res[field_name] = {"__errors": [error["message"] for error in errors]}
        return res

    def get_row_model_obj(self):
        pk = self.request.GET.get("pk")
        form = self.get_form()
        model = form.Meta.model
        obj = model.objects.get(pk=pk)
        return obj

    @add_frame_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.request.GET.get("action_type"):
            return context

        table_obj = self.get_table_obj()

        context["page_title"] = self.page_title
        context["table_metadata"] = json.dumps(table_obj.get_table_metadata())

        context["add_btn_title"] = self.add_btn_title or "Add New"
        context["has_add_perm"] = self.display_add_button_check(self.request)
        context["has_export_perm"] = (
            self.display_download_button_check(self.request)
            if hasattr(self, "display_download_button_check")
            else False
        )

        # Get table view context
        table_view_context = table_obj.get_context_data(context, **kwargs)
        context.update(table_view_context)

        # Get Detail View Context
        view = self.get_request_view()
        if view == "detail":
            detail_object = self.get_detail_obj(table_obj)
            detail_view_context = detail_object.get_context_data(context, **kwargs)
            context.update(detail_view_context)

        return context

    def get(self, request, *args, **kwargs):
        view = request.GET.get("view", None)
        action = self.get_request_action(request)

        if action == "render":
            return super().get(request, *args, **kwargs)

        if action == "get_table_metadata":
            table_metadata = self.get_table_obj().get_table_metadata()
            return get_api_response(
                success=True,
                response_content={"table_metadata": table_metadata},
                status=200,
            )

        if action == "render_to_string":
            template_names = self.get_template_names()
            if template_names:
                template_name = template_names[0]
                template_string = render_to_string(
                    template_name,
                    context=self.get_context_data(**kwargs),
                    request=request,
                )
                return get_api_response(
                    success=True,
                    response_content={"template_string": template_string},
                    status=200,
                )
            return get_api_response(
                success=False,
                response={"message": "No template found"},
                status=400,
            )

        if view == "table":
            table_obj = self.get_table_obj()
            return table_obj.get(request, *args, **kwargs)

        elif view == "detail":
            table_obj = self.get_table_obj()
            detail_obj = self.get_detail_obj(table_obj)
            return detail_obj.get(request, *args, **kwargs)

        elif view == "workflow":
            workflow_obj = self.get_workflow_obj()
            if workflow_obj:
                return workflow_obj.get(request, *args, **kwargs)
            return get_api_response(
                success=False,
                response={"message": "No workflow found"},
                status=400,
            )

        action = request.GET.get("action")
        if action == "initialize_form":
            form = self.get_form()
            json_schema, ui_schema = form.convert_model_form_to_json_schema()

            return JsonResponse(
                {
                    "success": True,
                    "response": {
                        "is_multistep": False,
                        "form": {"json_schema": json_schema, "ui_schema": ui_schema},
                    },
                }
            )

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = request.GET.get("view", None)

        if view == "workflow":
            workflow_obj = self.get_workflow_obj()
            if workflow_obj:
                return workflow_obj.post(request, *args, **kwargs)
            return get_api_response(
                success=False,
                response={"message": "No workflow found"},
                status=400,
            )
        elif view == "detail":
            table_obj = self.get_table_obj()
            detail_obj = self.get_detail_obj(table_obj)

            return detail_obj.post(request, *args, **kwargs)

        # Existing CRUD Code TODO: Refactor
        form_type = request.GET.get("form_type")

        if form_type == "create_form":
            form = self.get_form(data=request.POST, files=request.FILES)

            form_action = request.GET.get("form_action")

            if form_action == "sync_form":
                json_schema, ui_schema = form.convert_model_form_to_json_schema()

                return get_api_response(
                    success=True,
                    response_content={
                        "is_multistep": False,
                        "form": {
                            "json_schema": json_schema,
                            "ui_schema": ui_schema,
                            "form_data": request.POST.dict(),
                        },
                    },
                    status=200,
                )

            if form_action == "fetch_autcomplete_options":
                field_name = request.GET.get("field_name")
                search_query = request.GET.get("search_query")

                autocomplete_options_method = getattr(
                    form, f"get_{field_name}_autocomplete_options", None
                )
                autocomplete_options = []
                if autocomplete_options_method:
                    autocomplete_options = autocomplete_options_method(
                        request, search_query, request.POST
                    )

                return get_api_response(
                    success=True,
                    response_content={"autocomplete_options": autocomplete_options},
                    status=200,
                )

            if form.is_valid():
                object_instance = form.save()
                workflow_obj = self.get_workflow_obj(object_instance=object_instance)
                if workflow_obj:
                    workflow_obj.execute_transition(workflow_obj.Meta.on_create_status)
                return get_api_response(
                    success=True, response_content={"message": "Form Saved"}, status=200
                )
            else:
                form_errors = form.get_serialized_form_errors()
                return get_api_response(
                    success=False, response_content={"errors": form_errors}, status=400
                )

        action_type = request.GET.get("action_type")
        if action_type == "row":
            if form_type == "row_action_form":
                obj = self.get_row_model_obj()
                form = self.get_form(
                    data=request.POST, files=request.FILES, instance=obj
                )
                form_action = request.GET.get("form_action")

                if form_action == "sync_form":
                    json_schema, ui_schema = form.convert_model_form_to_json_schema()

                    return get_api_response(
                        success=True,
                        response_content={
                            "is_multistep": False,
                            "form": {
                                "json_schema": json_schema,
                                "ui_schema": ui_schema,
                                "form_data": request.POST.dict(),
                            },
                        },
                        status=200,
                    )

                if form.is_valid():
                    form.save()
                    return get_api_response(
                        success=True,
                        response_content={"message": "Form Saved"},
                        status=200,
                    )
                else:
                    form_errors = self.get_form_errors(form)
                    return get_api_response(
                        success=False,
                        response_content={"errors": form_errors},
                        status=400,
                    )

            else:
                table = self.table()
                success, response_content = table.perform_row_action(request)
                status_code = 200 if success else 400

                return get_api_response(success, response_content, status=status_code)


class BaseFormOnlyView(TemplateView, CrudRequestMixin):
    form_template = "crud/standalone_form.html"

    def get_request_view(self):
        """
        Returns the value of the 'view' parameter from the GET request.

        :param self: The current instance of the class.
        :return: The value of the 'view' parameter from the GET request.
        """
        view = self.request.GET.get("view", None)
        return view

    def get_template_names(self):
        return [self.form_template]

    def get_workflow_obj(self, **kwargs):
        workflow_class = getattr(self, "workflow", None)
        if workflow_class:
            workflow_object = workflow_class(
                request=self.request,
                crud_view_instance=self,
                object_instance=kwargs.get("object_instance", None),
            )
            return workflow_object

        return None

    def get_form(self, data=None, files=None, instance=None):
        kwargs = {"data": data, "files": files, "crud_view_instance": self}

        if issubclass(self.form, BaseForm):
            kwargs["instance"] = instance

        return self.form(**kwargs)

    def get_form_errors(self, form):
        form_errors = json.loads(form.errors.as_json())
        res = {}
        for field_name, errors in form_errors.items():
            res[field_name] = {"__errors": [error["message"] for error in errors]}
        return res

    @add_frame_context
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["display_sidebar"] = False

        context["page_title"] = self.page_title

        return context

    def get_success_url(self):
        success_url = getattr(self, "success_url", None)
        return success_url

    def get(self, request, *args, **kwargs):
        action = self.get_request_action(request)

        action = request.GET.get("action")
        if action == "initialize_form":
            form = self.get_form()
            json_schema, ui_schema = form.convert_model_form_to_json_schema()

            return JsonResponse(
                {
                    "success": True,
                    "response": {
                        "is_multistep": False,
                        "form": {"json_schema": json_schema, "ui_schema": ui_schema},
                    },
                }
            )

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = request.GET.get("view", None)

        # Existing CRUD Code TODO: Refactor
        form_type = request.GET.get("form_type")

        if form_type == "create_form":
            form = self.get_form(data=request.POST, files=request.FILES)

            form_action = request.GET.get("form_action")

            if form_action == "sync_form":
                json_schema, ui_schema = form.convert_model_form_to_json_schema()

                return get_api_response(
                    success=True,
                    response_content={
                        "is_multistep": False,
                        "form": {
                            "json_schema": json_schema,
                            "ui_schema": ui_schema,
                            "form_data": request.POST.dict(),
                        },
                    },
                    status=200,
                )

            if form_action == "fetch_autcomplete_options":
                field_name = request.GET.get("field_name")
                search_query = request.GET.get("search_query")

                autocomplete_options_method = getattr(
                    form, f"get_{field_name}_autocomplete_options", None
                )
                autocomplete_options = []
                if autocomplete_options_method:
                    autocomplete_options = autocomplete_options_method(
                        request, search_query, request.POST
                    )

                return get_api_response(
                    success=True,
                    response_content={"autocomplete_options": autocomplete_options},
                    status=200,
                )

            if form.is_valid():
                object_instance = form.save()
                workflow_obj = self.get_workflow_obj(object_instance=object_instance)
                if workflow_obj:
                    workflow_obj.execute_transition(workflow_obj.Meta.on_create_status)

                success_url = self.get_success_url()
                response_content = {
                    "message": "Form Saved",
                }
                if success_url:
                    response_content.update({"success_url": success_url})
                return get_api_response(
                    success=True,
                    response_content=response_content,
                    status=200,
                )
            else:
                form_errors = form.get_serialized_form_errors()
                return get_api_response(
                    success=False, response_content={"errors": form_errors}, status=400
                )

        return get_api_response(
            success=False, response_content={"message": "Invalid Request"}, status=400
        )
