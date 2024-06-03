import uuid
from django.db import models
from zango.apps.dynamic_models.models import DynamicModelBase
from zango.apps.appauth.models import UserRoleModel
from zango.apps.dynamic_models.fields import ZOneToOneField


class FramesModel(DynamicModelBase):
    user_role = ZOneToOneField(
        UserRoleModel, on_delete=models.PROTECT, related_name="frame"
    )
    config = models.JSONField()
