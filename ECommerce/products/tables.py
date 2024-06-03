from ..packages.crud.table.base import ModelTable
from ..packages.crud.table.column import ModelCol

from .models import Product, Enquiry
from .forms import ProductForm, EnquiryForm


class ProductTable(ModelTable):

    table_actions = []
    row_actions = [
        {
            "name": "Edit",
            "key": "Edit",
            "description": "Edit Contract",
            "type": "form",
            "form": ProductForm,
            "roles": ["Admin"],
        }
    ]

    class Meta:
        model = Product
        fields = ["name", "description", "image", "price", "category"]


class EnquiryTable(ModelTable):

    table_actions = []
    row_actions = []

    class Meta:
        model = Enquiry
        fields = ["email", "message", "product"]
