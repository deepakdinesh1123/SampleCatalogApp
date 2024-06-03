import json
import requests

from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect

from zango.apps.appauth.models import UserRoleModel
from zango.apps.shared.tenancy.models import ThemesModel
from zango.core.utils import get_package_url

from .utils import ZelthyLoginView

from .forms import (
    AppLoginForm,
    UserRoleSelectionForm,
    AppUserResetPasswordForm,
)

from ..configure.models import LoginConfigModel, GenericLoginConfigModel


@method_decorator(never_cache, name="dispatch")
class AppUserLoginView(ZelthyLoginView):
    """
    View to render the login page html.
    """

    template_name = "login/login.html"  # To be updated with new html

    userrolemodel = UserRoleModel

    form_list = (
        ("auth", AppLoginForm),
        ("user_role", UserRoleSelectionForm),
        ("password_reset", AppUserResetPasswordForm),
    )

    def get_template_names(self):
        templates = ["custom_login.html"] + super().get_template_names()
        return templates

    def get_context_data(self, **kwargs):
        context = super(AppUserLoginView, self).get_context_data(**kwargs)
        context["tenant"] = self.request.tenant
        context["tenant_logo"] = (
            self.request.build_absolute_uri(self.request.tenant.logo.url)
            if self.request.tenant.logo
            else None
        )
        app_theme_config = ThemesModel.objects.filter(
            tenant=self.request.tenant, is_active=True
        ).first()
        if app_theme_config:
            context["app_theme_config"] = app_theme_config.config

        generic_config = GenericLoginConfigModel.objects.last()
        if generic_config:
            context["generic_config"] = generic_config.config or {}
            context["generic_config_logo"] = (
                self.request.build_absolute_uri(generic_config.logo.url)
                if generic_config.logo
                else None
            )
            context["background_image"] = (
                self.request.build_absolute_uri(generic_config.background_image.url)
                if generic_config.background_image
                else None
            )

        return context

    def get_form_initial(self, step):
        initial = super(AppUserLoginView, self).get_form_initial(step)
        initial["request"] = self.request
        return initial

    def get_user(self):
        self.user_cache = super(AppUserLoginView, self).get_user()
        return self.user_cache

    def post(self, *args, **kwargs):
        if (
            self.request.POST.get("app_user_login_view-current_step") == "auth"
            and self.request.POST.get("auth-saml", "0") != "0"
        ):
            url = get_package_url(
                self.request, f"saml/fetch_saml_config/?action=fetch_config", "sso"
            )
            response = requests.post(
                url,
                data=json.dumps({"saml_id": self.request.POST.get("auth-saml")}),
                headers={"Content-Type": "application/json"},
            )
            if response.status_code == 200:
                url = response.json().get("response")
                return HttpResponseRedirect(url)
        return super(AppUserLoginView, self).post(*args, **kwargs)
