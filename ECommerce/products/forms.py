from ..packages.crud.forms import BaseForm
from ..packages.crud.form_fields import ModelField

from .models import Product, Enquiry


class ProductForm(BaseForm):
    name = ModelField(
        placeholder="Product Name",
        required=True,
        required_msg="Please enter the product name",
    )
    description = ModelField(placeholder="Product Description", required=False)
    image = ModelField(placeholder="Product Image", required=False)
    price = ModelField(
        placeholder="Product Price",
        required=True,
        required_msg="Please enter the product price",
    )
    category = ModelField(
        placeholder="Category", required=True, required_msg="Please select a category"
    )

    class Meta:
        model = Product
        title = "Product"
        order = ["name", "description", "image", "price", "category"]


class EnquiryForm(BaseForm):
    email = ModelField(
        placeholder="Email",
        required=True,
        required_msg="Please enter your email",
    )
    message = ModelField(
        placeholder="Message",
        required=True,
        required_msg="Please enter your message",
    )
    product = ModelField(placeholder="Product", required=False)

    class Meta:
        model = Enquiry
        title = "Enquiry"
        order = [
            "email",
            "message",
            "product",
        ]
