import pytz

from django.db import models
from django.db import connection

from rest_framework import serializers
from rest_framework.serializers import SerializerMetaclass

from zango.core.utils import get_current_request
from zango.core.storage_utils import ZFileField
from zango.apps.dynamic_models.fields import ZForeignKey, ZOneToOneField


class StringRelatedMeta(SerializerMetaclass):
    def __new__(cls, name, bases, attrs):
        # Get the Meta class from attrs
        meta = attrs.get("Meta", None)
        metadata = attrs.get("metadata", {})
        # Check if there's a model defined in Meta
        request = get_current_request()
        if request:
            tenant = request.tenant
        else:
            tenant = connection.tenant
        if meta and hasattr(meta, "model"):
            model = meta.model

            # Get the fields to include from the meta class
            fields_to_include = getattr(meta, "fields", [])

            # Check if there are any fields to include
            if fields_to_include:
                # Filter the model's fields based on the fields to include
                included_fields = [
                    field
                    for field in model._meta.fields
                    if field.name in fields_to_include
                ]
            else:
                # If no fields to include, include all fields from the model
                included_fields = model._meta.fields

            for field in included_fields:
                if isinstance(
                    field,
                    (
                        models.ForeignKey,
                        models.OneToOneField,
                        ZForeignKey,
                        ZOneToOneField,
                    ),
                ):
                    # Use StringRelatedField for this field
                    related_object_attribute = None
                    for column in metadata["columns"]:
                        if column["name"] == field.name:
                            if column.get("related_object_attribute"):
                                related_object_attribute = column[
                                    "related_object_attribute"
                                ]
                    if related_object_attribute is not None:
                        attrs[field.name] = ForeignKeySerializer(
                            related_object_attribute
                        )
                    else:
                        attrs[field.name] = serializers.StringRelatedField()
                elif isinstance(field, (models.DateTimeField)):
                    attrs[field.name] = serializers.DateTimeField(
                        format=tenant.datetime_format,
                        default_timezone=pytz.timezone(tenant.timezone),
                    )
                elif isinstance(field, (models.DateField)):
                    attrs[field.name] = serializers.DateField(
                        format=tenant.date_format or "%d %b %Y",
                    )
                elif isinstance(field, (models.FileField, ZFileField)):
                    attrs[field.name] = FileSerializer()
                elif isinstance(field, models.CharField) and field.choices:
                    attrs[field.name] = serializers.CharField(
                        source=f"get_{field.name}_display"
                    )

        return super().__new__(cls, name, bases, attrs)


class FileSerializer(serializers.Field):
    def to_representation(self, value):
        if not value:
            return "NA"
        request = get_current_request()
        if request:
            url = request.build_absolute_uri(value.url)
            svg = f"""
                    <a href='{url}' target='_blank' style='color: var(--primary-color);'>
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9.45455 27H22.5455C23.9006 26.999 24.999 25.9442 25 24.6429V12.0714C24.999 10.7701 23.9006 9.71527 22.5455 9.71429H20.0909V7.35714C20.0899 6.0558 18.9915 5.00098 17.6364 5H9.45455C8.09943 5.00098 7.00102 6.0558 7 7.35714V24.6429C7.00102 25.9442 8.09943 26.999 9.45455 27ZM8.63636 7.35714C8.63636 6.92303 9.00249 6.57143 9.45455 6.57143H17.6364C18.0884 6.57143 18.4545 6.92303 18.4545 7.35714V10.5C18.4545 10.7082 18.5405 10.9086 18.6939 11.0559C18.8473 11.2032 19.0559 11.2857 19.2727 11.2857H22.5454C22.9975 11.2857 23.3636 11.6373 23.3636 12.0714V24.6428C23.3636 25.077 22.9975 25.4286 22.5454 25.4286H9.45453C9.00248 25.4286 8.63635 25.077 8.63635 24.6428L8.63636 7.35714Z" fill="currentColor"/>
                    <path d="M11.0906 23.8576H15.9997C16.4518 23.8576 16.8179 23.506 16.8179 23.0718C16.8179 22.6377 16.4518 22.2861 15.9997 22.2861H11.0906C10.6386 22.2861 10.2724 22.6377 10.2724 23.0718C10.2724 23.506 10.6386 23.8576 11.0906 23.8576Z" fill="currentColor"/>
                    <path d="M11.0906 20.714H19.2724C19.7245 20.714 20.0906 20.3624 20.0906 19.9283C20.0906 19.4942 19.7245 19.1426 19.2724 19.1426H11.0906C10.6386 19.1426 10.2724 19.4942 10.2724 19.9283C10.2724 20.3624 10.6386 20.714 11.0906 20.714Z" fill="currentColor"/>
                    <path d="M13.5452 17.5718C15.3523 17.5718 16.8179 16.1644 16.8179 14.429C16.8179 12.6936 15.3523 11.2861 13.5452 11.2861V12.8576C14.2069 12.8576 14.8042 13.2406 15.0568 13.8279C15.3104 14.4152 15.1703 15.091 14.7019 15.5398C14.2345 15.9896 13.5308 16.1242 12.9193 15.8806C12.3077 15.638 11.9088 15.0645 11.9088 14.429H10.2724C10.2745 16.1645 11.738 17.5699 13.5452 17.5719L13.5452 17.5718Z" fill="currentColor"/>
                    </a>
                """
            return svg

        return "File"


class ForeignKeySerializer(serializers.Field):
    def __init__(self, field, *args, **kwargs):
        super(ForeignKeySerializer, self).__init__(*args, **kwargs)
        self.field = field

    def to_representation(self, value):
        return vars(value).get(self.field)
