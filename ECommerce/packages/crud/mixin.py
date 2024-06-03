import json

from django import forms

from phonenumber_field.formfields import PhoneNumberField


from .fields import (
    CharJSONSchemaField,
    EmailJSONSchemaField,
    ChoiceJSONSchemaField,
    IntegerJSONSchemaField,
    TextJSONSchemaField,
    DateJSONSchemaField,
    DateTimeJSONSchemaField,
    FileJSONSchemaField,
    BooleanJSONSchemaField,
    NumberJSONSchemaField,
    MobileJSONSchemaField,
    MultipleChoiceJSONSchemaField,
)

from .form_fields import ModelField


class FormsMixin(object):
    FIELD_MAP = {
        forms.CharField: CharJSONSchemaField,
        forms.EmailField: EmailJSONSchemaField,
        forms.IntegerField: IntegerJSONSchemaField,
        forms.DecimalField: NumberJSONSchemaField,
        forms.BooleanField: BooleanJSONSchemaField,
        forms.ChoiceField: ChoiceJSONSchemaField,
        forms.MultipleChoiceField: MultipleChoiceJSONSchemaField,
        forms.TypedChoiceField: ChoiceJSONSchemaField,
        forms.TypedMultipleChoiceField: MultipleChoiceJSONSchemaField,
        forms.ModelChoiceField: ChoiceJSONSchemaField,
        forms.ModelMultipleChoiceField: MultipleChoiceJSONSchemaField,
        forms.Textarea: TextJSONSchemaField,
        forms.DateField: DateJSONSchemaField,
        forms.DateTimeField: DateTimeJSONSchemaField,
        forms.FileField: FileJSONSchemaField,
        PhoneNumberField: MobileJSONSchemaField,
    }

    def convert_model_form_to_json_schema(self):
        json_schema = {
            "type": "object",
            "properties": {},
            "required": [],
        }
        # Form title
        if hasattr(self.Meta, "title"):
            json_schema["title"] = self.Meta.title

        ui_schema = {}

        for field_name, field in self.fields.items():
            field_class = field.__class__

            json_field_class = self.FIELD_MAP.get(field_class, None)

            if json_field_class:
                json_field = json_field_class(field, self.declared_fields[field_name])

                field_schema = json_field.to_json_schema(
                    initial=self.initial.get(field_name)
                )
                field_ui_schema = json_field.to_ui_schema()

                if self.declared_fields[field_name].properties.get("hidden"):
                    field_ui_schema["ui:widget"] = "hidden"

                if self.declared_fields[field_name].extra_schema:
                    field_schema.update(self.declared_fields[field_name].extra_schema)
                if self.declared_fields[field_name].extra_ui_schema:
                    field_ui_schema.update(
                        self.declared_fields[field_name].extra_ui_schema
                    )

                json_schema["properties"][field_name] = field_schema
                ui_schema[field_name] = field_ui_schema

                if field.required or self.declared_fields[field_name].properties.get(
                    "required"
                ):
                    json_schema["required"].append(field_name)

        # custom fields
        for custom_field_name, custom_field in self.custom_schema_fields.items():
            json_schema["properties"][custom_field_name] = custom_field.schema
            ui_schema[custom_field_name] = custom_field.ui_schema
            if custom_field.required:
                json_schema["required"].append(custom_field_name)

        meta_class = getattr(self, "_meta", getattr(self, "Meta", None))

        if meta_class:
            # Extra UI Schema and JSON Schema
            extra_ui_schema = getattr(meta_class, "extra_ui_schema", {})
            extra_schema = getattr(meta_class, "extra_schema", {})

            # Fields Order
            if getattr(meta_class, "order", None):
                field_order = meta_class.order
                extra_ui_schema.update({"ui:order": field_order})

            json_schema.update(extra_schema)
            ui_schema.update(extra_ui_schema)
        return json_schema, ui_schema

    def get_serialized_form_errors(self):
        form_errors = json.loads(self.errors.as_json())
        res = {}
        for field_name, errors in form_errors.items():
            res[field_name] = {"__errors": [error["message"] for error in errors]}
        return res


class CrudRequestMixin(object):
    def get_request_action(self, request):
        """
        Get the request action from the given request.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            str: The value of the 'action' parameter from the request's GET parameters.
        """
        action = request.GET.get("action")
        return action

    def get_request_user(seflf, request):
        from zango.core.utils import get_current_role

        user_role = get_current_role()
        print("user_role: ", user_role)
        print("request.user: ", request.user)
        return request.user if user_role.name != "AnonymousUsers" else None
