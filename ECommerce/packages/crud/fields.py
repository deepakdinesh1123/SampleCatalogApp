import phonenumbers

from django.conf import settings


class BaseField:
    def __init__(self, field, declared_field):
        self.field = field
        self.declared_field = declared_field
        if not hasattr(self.declared_field, "properties"):
            self.declared_field.properties = {}
        self.field_schema = {"title": self.field.label}
        self.ui_schema = {}

    def to_json_schema(self, initial=None):
        raise NotImplementedError("Subclasses must implement this method.")

    def to_ui_schema(self):
        raise NotImplementedError("Subclasses must implement this method.")


class BaseJSONSchemaField(BaseField):
    def to_json_schema(self, initial=None):
        initial_val = initial or self.field.initial
        if initial_val:
            self.field_schema["default"] = initial_val
        if self.declared_field.properties.get("label"):
            self.field_schema["title"] = self.declared_field.properties.get("label")
        if self.declared_field.properties.get("pattern"):
            self.field_schema["pattern"] = self.declared_field.properties.get("pattern")

        return self.field_schema

    def to_ui_schema(self):
        if self.field.disabled:
            self.ui_schema["ui:disabled"] = True

        if self.declared_field.properties.get("readonly"):
            self.ui_schema["ui:readonly"] = True

        error_messages = {}

        if self.declared_field.properties.get("placeholder"):
            self.ui_schema["ui:placeholder"] = self.declared_field.properties.get(
                "placeholder"
            )

        self.ui_schema["ui:syncEnabled"] = self.declared_field.properties.get(
            "sync_enabled", False
        )

        self.ui_schema["ui:autocomplete"] = self.declared_field.properties.get(
            "autocomplete", {}
        )

        if self.declared_field.properties.get("required_msg"):
            error_messages["required"] = self.declared_field.properties.get(
                "required_msg"
            )

        if self.declared_field.properties.get("pattern_msg"):
            error_messages["pattern"] = self.declared_field.properties.get(
                "pattern_msg"
            )

        self.ui_schema["ui:errorMessages"] = error_messages

        return self.ui_schema


class BaseStringField(BaseJSONSchemaField):
    def to_json_schema(self, initial=None):
        self.field_schema = super().to_json_schema(initial)
        self.field_schema["type"] = "string"
        if self.field.min_length:
            self.field_schema["minLength"] = self.field.max_length
        if self.field.max_length:
            self.field_schema["maxLength"] = self.field.max_length

        return self.field_schema


class CharJSONSchemaField(BaseStringField):
    def to_ui_schema(self):
        self.ui_schema = super(CharJSONSchemaField, self).to_ui_schema()
        self.ui_schema["ui:widget"] = "TextFieldWidget"
        return self.ui_schema


class TextJSONSchemaField(BaseStringField):
    def to_ui_schema(self):
        self.ui_schema = super(TextJSONSchemaField, self).to_ui_schema()
        self.ui_schema["ui:widget"] = "TextareaFieldWidget"
        return self.ui_schema


class EmailJSONSchemaField(BaseStringField):
    def to_ui_schema(self):
        self.ui_schema = super(EmailJSONSchemaField, self).to_ui_schema()
        self.ui_schema["ui:widget"] = "EmailFieldWidget"
        return self.ui_schema


class MobileJSONSchemaField(BaseStringField):
    def to_json_schema(self, initial=None):
        self.field_schema = super(MobileJSONSchemaField, self).to_json_schema(initial)
        if self.field_schema.get("default"):
            self.field_schema["default"] = str(
                self.field_schema["default"].national_number
            )

        # Get country code from region
        country_code = phonenumbers.country_code_for_region(
            settings.PHONENUMBER_DEFAULT_REGION
        )

        self.field_schema["countryCode"] = f"+{country_code}"
        return self.field_schema

    def to_ui_schema(self):
        self.ui_schema = super(MobileJSONSchemaField, self).to_ui_schema()
        self.ui_schema["ui:widget"] = "MobileFieldWidget"
        return self.ui_schema


class IntegerJSONSchemaField(BaseJSONSchemaField):
    def to_json_schema(self, initial=None):
        super(IntegerJSONSchemaField, self).to_json_schema(initial)
        self.field_schema["type"] = "integer"
        if self.field.min_value:
            self.field_schema["minimum"] = self.field.min_value
        if self.field.max_value:
            self.field_schema["maximum"] = self.field.max_value
        return self.field_schema

    def to_ui_schema(self):
        super(IntegerJSONSchemaField, self).to_ui_schema()
        self.ui_schema["ui:widget"] = "NumberFieldWidget"
        return self.ui_schema


class NumberJSONSchemaField(BaseJSONSchemaField):
    def to_json_schema(self, initial=None):
        super(NumberJSONSchemaField, self).to_json_schema(initial)
        self.field_schema["type"] = "number"
        if self.field.min_value:
            self.field_schema["minimum"] = self.field.min_value
        if self.field.max_value:
            self.field_schema["maximum"] = self.field.max_value

        if self.field_schema.get("default"):
            self.field_schema["default"] = float(self.field_schema["default"])
        return self.field_schema

    def to_ui_schema(self):
        super(NumberJSONSchemaField, self).to_ui_schema()
        self.ui_schema["ui:widget"] = "NumberFieldWidget"
        return self.ui_schema


class BooleanJSONSchemaField(BaseJSONSchemaField):
    def to_json_schema(self, initial=None):
        super(BooleanJSONSchemaField, self).to_json_schema(initial)
        self.field_schema["type"] = "boolean"
        return self.field_schema

    def to_ui_schema(self):
        super(BooleanJSONSchemaField, self).to_ui_schema()
        self.ui_schema["ui:widget"] = "radio"
        return self.ui_schema


class ChoiceJSONSchemaField(BaseJSONSchemaField):
    def to_json_schema(self, initial=None):
        super(ChoiceJSONSchemaField, self).to_json_schema(initial)
        self.field_schema["type"] = "string"

        if not self.declared_field.properties.get("autocomplete", {}).get(
            "enabled", False
        ):
            self.field_schema["enum"] = [
                str(choice[0]) for choice in self.field.choices if str(choice[0])
            ]
            self.field_schema["enumNames"] = [
                str(choice[1]) for choice in self.field.choices if str(choice[0])
            ]

        if self.field_schema.get("default"):
            if not isinstance(self.field_schema["default"], list):
                self.field_schema["default"] = str(self.field_schema["default"])
            else:
                self.field_schema["default"] = [
                    str(default_val) for default_val in self.field_schema["default"]
                ]
        return self.field_schema

    def to_ui_schema(self):
        super(ChoiceJSONSchemaField, self).to_ui_schema()
        if self.ui_schema.get("ui:autocomplete", {}).get("enabled", False):
            self.ui_schema["ui:widget"] = "AsyncSelectFieldWidget"
        else:
            self.ui_schema["ui:widget"] = "SelectFieldWidget"
        return self.ui_schema


class MultipleChoiceJSONSchemaField(ChoiceJSONSchemaField):
    def to_json_schema(self, initial=None):
        self.field_schema = super(MultipleChoiceJSONSchemaField, self).to_json_schema(
            initial
        )
        self.field_schema["type"] = "array"
        self.field_schema["uniqueItems"] = True

        self.field_schema["items"] = {
            "type": "string",
            "enum": self.field_schema["enum"],
            "enumNames": self.field_schema["enumNames"],
        }
        self.field_schema.pop("enum", None)
        self.field_schema.pop("enumNames", None)
        return self.field_schema

    def to_ui_schema(self):
        super(MultipleChoiceJSONSchemaField, self).to_ui_schema()
        self.ui_schema["ui:widget"] = "SelectFieldWidget"
        self.ui_schema["ui:options"] = {"multiple": True}
        return self.ui_schema


class EMailJSONSchemaField(BaseJSONSchemaField):
    def to_ui_schema(self):
        self.ui_schema = super(EMailJSONSchemaField, self).to_ui_schema()
        self.ui_schema["ui:widget"] = "EmailFieldWidget"
        return self.ui_schema


class DateJSONSchemaField(BaseJSONSchemaField):
    def to_json_schema(self, initial=None):
        self.field_schema = super().to_json_schema(initial)
        self.field_schema["type"] = "string"
        self.field_schema["default"] = (
            str(self.field_schema["default"])
            if self.field_schema.get("default")
            else ""
        )
        return self.field_schema

    def to_ui_schema(self):
        from zango.core.utils import get_current_request

        request = get_current_request()

        self.ui_schema = super(DateJSONSchemaField, self).to_ui_schema()
        self.ui_schema["ui:widget"] = "DatePickerFieldWidget"
        self.ui_schema["ui:options"] = {
            "dateFormat": request.tenant.date_format
            if request.tenant.date_format
            else "%d %b %Y"
        }
        # TODO: Handle range
        # "ui:options": {
        #     "yearsRange": [
        #     1980,
        #     2030
        #     ]
        # }
        return self.ui_schema


class DateTimeJSONSchemaField(BaseJSONSchemaField):
    def to_json_schema(self, initial=None):
        self.field_schema = super().to_json_schema(initial)
        self.field_schema["type"] = "string"
        self.field_schema["default"] = (
            str(self.field_schema["default"])
            if self.field_schema.get("default")
            else ""
        )
        return self.field_schema

    def to_ui_schema(self):
        from zango.core.utils import get_current_request

        request = get_current_request()
        self.ui_schema = super(DateTimeJSONSchemaField, self).to_ui_schema()
        self.ui_schema["ui:widget"] = "DateTimePickerFieldWidget"  # "date-time"
        self.ui_schema["ui:options"] = {
            "datetimeFormat": request.tenant.datetime_format
            if request.tenant.datetime_format
            else "%d %B %Y %I:%M %p"
        }
        # TODO: Handle range
        # "ui:options": {
        #     "yearsRange": [
        #     1980,
        #     2030
        #     ]
        # }
        return self.ui_schema


class FileJSONSchemaField(BaseJSONSchemaField):
    def to_json_schema(self, initial=None):
        self.field_schema = super().to_json_schema(initial)
        self.field_schema["type"] = "string"
        if self.field_schema.get("default"):
            from zango.core.utils import get_current_request

            request = get_current_request()
            url = request.build_absolute_uri(self.field_schema["default"].url)
            self.field_schema["default"] = url
        return self.field_schema

    def to_ui_schema(self):
        self.ui_schema = super(FileJSONSchemaField, self).to_ui_schema()
        self.ui_schema["ui:widget"] = "FileFieldWidget"
        self.ui_schema["ui:format"] = "data-url"
        return self.ui_schema


class AnyOfJsonSchemaField(BaseJSONSchemaField):
    fields = []

    def to_json_schema(self, initial=None):
        self.field_schema["type"] = "objects"
        any_of_fields = []
        for f in self.fields:
            any_of_fields.append({"properties": f.to_json_schema(initial)})

        self.field_schema["anyOf"] = any_of_fields
        return self.field_schema

    def to_ui_schema(self):
        pass
