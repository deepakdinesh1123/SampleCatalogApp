import copy

from django import forms
from django.forms.models import ModelFormMetaclass


from .form_fields import ModelField

from .mixin import FormsMixin


class CustomModelFormMetaclass(ModelFormMetaclass):
    def __new__(mcs, name, bases, attrs):
        """
        do away with the need for users to specify fields in Meta of the form class
        """
        if "Meta" in attrs.keys():
            meta = attrs["Meta"]
            setattr(meta, "fields", "__all__")
        return super().__new__(mcs, name, bases, attrs)


class BaseForm(forms.ModelForm, FormsMixin, metaclass=CustomModelFormMetaclass):
    def __init__(self, *args, **kwargs):
        self.declared_fields = {}
        self.form_fields = {}
        self.custom_schema_fields = {}
        self.crud_view_instance = kwargs.pop("crud_view_instance", None)

        # Walk through the MRO to get attributes from both parent and child classes
        form_class_attrs = {}
        for cls in reversed(self.__class__.mro()):
            # Use dir() to get all attributes of the class
            class_attributes = [attr for attr in dir(cls) if not attr.startswith("__")]

            # Use getattr() to get the values of the attributes
            attribute_values = {attr: getattr(cls, attr) for attr in class_attributes}

            # Update the dictionary with the values
            form_class_attrs.update(attribute_values)

        self.declared_fields.update(form_class_attrs.get("declared_fields", {}))
        for attr_name, attr_value in form_class_attrs.items():
            if attr_value.__class__.__name__ == "ModelField":
                self.declared_fields[attr_name] = attr_value
            elif attr_value.__class__.__name__ == "CustomSchemaField":
                self.custom_schema_fields[attr_name] = attr_value
        unique_together = []
        if hasattr(self.Meta, "unique_together"):
            unique_together = getattr(self.Meta, "unique_together")

        order = getattr(self.Meta, "order", None)

        super(BaseForm, self).__init__(*args, **kwargs)
        self._meta.unique_together = unique_together
        self._meta.order = order
        self.remove_extra_model_field()
        for field_name, field_obj in self.declared_fields.items():
            if isinstance(field_obj, forms.Field):
                self.declared_fields.update(
                    {
                        field_name: ModelField(
                            label=field_obj.label,
                            placeholder=field_obj.widget.attrs.get("placeholder", None),
                            required=field_obj.required,
                            pattern=getattr(field_obj, "regex", None),
                            readonly=field_obj.widget.attrs.get("readonly", None),
                            hidden=isinstance(field_obj.widget, forms.HiddenInput),
                            extra_schema={},
                            extra_ui_schema={},
                        )
                    }
                )
            if field_obj.initial:
                if callable(field_obj.initial):
                    self.fields[field_name].initial = field_obj.initial()
                else:
                    self.fields[field_name].initial = field_obj.initial

    def remove_extra_model_field(self):
        fields = copy.deepcopy(self.fields)
        for f in fields:
            if f not in self.declared_fields.keys():
                del self.fields[f]

    def clean(self, *args, **kwargs):
        super(BaseForm, self).clean(*args, **kwargs)

        # Unique together
        if hasattr(self._meta, "unique_together"):
            unique_together = self._meta.unique_together

            pk = self.instance.pk
            for constraint in unique_together:
                fields = constraint.get("fields", [])
                message = constraint.get("message", "")

                unique_kwargs = {}
                for f in fields:
                    if not self.cleaned_data.get(f):
                        break
                    unique_kwargs[f] = self.cleaned_data[f]
                objects = self._meta.model.objects.filter(**unique_kwargs)
                if objects:
                    if not pk:
                        raise forms.ValidationError(message)
                    else:
                        if not (len(objects) == 1 and objects[0].id == pk):
                            raise forms.ValidationError(message)

    def add_custom_fields(self):
        fields = copy.deepcopy(self.fields)
        for f in self.declared_fields.keys():
            if f not in fields:
                self.fields[f] = self.declared_fields[f].field_cls(
                    **self.declared_fields[f].kwargs
                )


class BaseSimpleForm(forms.Form, FormsMixin):
    def __init__(self, *args, **kwargs):
        self.declared_fields = {}
        self.form_fields = {}
        self.custom_schema_fields = {}
        self.crud_view_instance = kwargs.pop("crud_view_instance", None)

        # Walk through the MRO to get attributes from both parent and child classes
        form_class_attrs = {}
        for cls in reversed(self.__class__.mro()):
            # Use dir() to get all attributes of the class
            class_attributes = [attr for attr in dir(cls) if not attr.startswith("__")]

            # Use getattr() to get the values of the attributes
            attribute_values = {attr: getattr(cls, attr) for attr in class_attributes}

            # Update the dictionary with the values
            form_class_attrs.update(attribute_values)

        self.declared_fields.update(form_class_attrs.get("declared_fields", {}))
        for attr_name, attr_value in form_class_attrs.items():
            if attr_value.__class__.__name__ == "CustomSchemaField":
                self.custom_schema_fields[attr_name] = attr_value
        super(BaseSimpleForm, self).__init__(*args, **kwargs)

        for field_name, field_obj in self.declared_fields.items():
            if isinstance(field_obj, forms.Field):
                self.declared_fields.update(
                    {
                        field_name: ModelField(
                            label=field_obj.label,
                            placeholder=field_obj.widget.attrs.get("placeholder", None),
                            required=field_obj.required,
                            pattern=getattr(field_obj, "regex", None),
                            readonly=field_obj.widget.attrs.get("readonly", None),
                            hidden=isinstance(field_obj.widget, forms.HiddenInput),
                            extra_schema={},
                            extra_ui_schema={},
                        )
                    }
                )
            if field_obj.initial:
                if callable(field_obj.initial):
                    self.fields[field_name].initial = field_obj.initial()
                else:
                    self.fields[field_name].initial = field_obj.initial
