from zango.apps.dynamic_models.models import DynamicModelBase
from zango.apps.dynamic_models.fields import ZForeignKey
from zango.core.storage_utils import ZFileField
from django.db import models


class Product(DynamicModelBase):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    image = ZFileField(blank=True, null=True)
    price = models.IntegerField()
    category = models.CharField(
        max_length=100,
        choices=[
            ("electronics", "Electronics"),
            ("fashion", "Fashion"),
            ("home", "Home"),
        ],
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Enquiry(DynamicModelBase):
    email = models.EmailField()
    message = models.TextField()
    product = ZForeignKey(Product, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.message
