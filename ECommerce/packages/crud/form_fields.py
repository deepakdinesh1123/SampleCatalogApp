from django import forms


class ModelField:
    def __init__(
        self,
        label="",
        placeholder="",
        required=False,
        required_msg="",
        pattern="",
        pattern_msg="",
        readonly=False,
        hidden=False,
        initial=None,
        sync_enabled=False,
        autocomplete={},
        extra_schema={},
        extra_ui_schema={},
    ):
        properties = {}
        if label:
            properties["label"] = label
        if placeholder:
            properties["placeholder"] = placeholder
        if required:
            properties["required"] = required
        if required_msg:
            properties["required_msg"] = required_msg
        if pattern:
            properties["pattern"] = pattern
            properties["pattern_msg"] = pattern_msg
        if hidden:
            properties.update(hidden=True)
        if readonly:
            properties.update(readonly=True)
        properties.update(sync_enabled=sync_enabled)
        properties.update(autocomplete=autocomplete)

        self.extra_schema = extra_schema
        self.extra_ui_schema = extra_ui_schema
        self.properties = properties
        self.initial = initial


class CustomSchemaField:
    def __init__(
        self,
        required=False,
        schema={},
        ui_schema={},
    ):
        self.required = required
        self.schema = schema
        self.ui_schema = ui_schema

        # Add Error Messages
        if not self.ui_schema.get("ui:errorMessages"):
            self.ui_schema["ui:errorMessages"] = {}


class CustomField:
    FIELD_MAP = {
        "CharField": forms.CharField,
        "ModelMultiChoiceField": forms.ModelMultipleChoiceField
        # Add other mappings here
    }

    def __init__(self, type, inital=None, **kwargs):
        self.properties = {}
        if type not in self.FIELD_MAP:
            raise ValueError(f"Invalid field type: {type}")
        self.field_cls = self.FIELD_MAP[type]
        self.kwargs = kwargs
        self.initial = inital
