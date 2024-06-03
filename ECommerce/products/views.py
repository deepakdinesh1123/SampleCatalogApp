from zango.core.utils import get_current_role

from ..packages.crud.base import BaseCrudView
from .tables import EnquiryTable, ProductTable
from .forms import EnquiryForm, ProductForm
from .models import Enquiry, Product


class EnquiryCrudView(BaseCrudView):
    page_title = "Enquiries"
    add_btn_title = "New Enquiry"
    table = EnquiryTable
    form = EnquiryForm

    def has_add_perm(self, request):
        return True

    def display_add_button_check(self, request):
        return get_current_role().name in ["AppUser"]


class ProductCrudView(BaseCrudView):
    page_title = "Products"
    add_btn_title = "Add New Product"
    table = ProductTable
    form = ProductForm

    def has_add_perm(self, request):
        return True

    def display_add_button_check(self, request):
        return get_current_role().name in ["Admin"]
