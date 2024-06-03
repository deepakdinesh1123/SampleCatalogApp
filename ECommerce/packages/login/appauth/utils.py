from django.contrib.auth import login, REDIRECT_FIELD_NAME
from django.http import Http404
from django.shortcuts import redirect
from django.core.exceptions import ImproperlyConfigured

from formtools.wizard.views import SessionWizardView

from zango.apps.appauth.models import UserRoleModel

from .base import ZelthyLoginBase


USER_AUTH_BACKEND = "zango.apps.appauth.auth_backend.AppUserModelBackend"


class ZelthyLoginView(ZelthyLoginBase, SessionWizardView):

    """
    View for handling the login process
    The login process is composed like a wizard. The first step asks for the
    user's credentials. If the credentials are correct, the wizard prompts user to select a role(from the ones assigned to user).
    Once the user selects the role, it displays Reset password form if the user is logging in for the first time or password is reset from App Panel
    """

    template_name = ""
    userrolemodel = ""
    redirect_field_name = REDIRECT_FIELD_NAME

    form_list = (
        ("auth", ""),
        ("user_role", ""),
        ("password_reset", ""),
    )

    def has_role_step(self):
        return super(ZelthyLoginView, self).has_role_step()

    def has_password_reset_step(self):
        return super(ZelthyLoginView, self).has_password_reset_step()

    def get_user(self):
        """
        Returns the user authenticated by the AuthenticationForm. Returns False
        if not a valid user; see also issue #65.
        """
        if not self.user_cache:
            form_obj = self.get_form(
                step="auth", data=self.storage.get_step_data("auth")
            )
            self.user_cache = form_obj.user_cache if form_obj.is_valid() else False
        return self.user_cache

    def get_next_url_from_request(self):
        """
        Retrieves the 'next' URL from the Django request.

        Args:
            request (HttpRequest): The Django HttpRequest object.

        Returns:
            str: The 'next' URL if present in the request, otherwise None.
        """
        next_param = self.request.GET.get("next")
        return next_param

    def get_landing_page_url(self, user_role):
        """
        Get the landing page URL based on the user's role.

        Args:
            self: The object instance.
            user_role: The user's role.

        Returns:
            str: The landing page URL.

        Raises:
            ImproperlyConfigured: If the landing page URL is not found or if no login config is found for the user's role.
        """
        try:
            login_config = user_role.login_config
            config = login_config.config or {}
            landing_page_url = config.get("landing_url")
            if not landing_page_url:
                raise ImproperlyConfigured(
                    f"No landing_url found for {user_role.name} user role"
                )
        except UserRoleModel.login_config.RelatedObjectDoesNotExist:
            raise ImproperlyConfigured(
                f"No login config found for {user_role.name} user role"
            )
        return landing_page_url

    def get_redirect_url(self, user_role):
        """
        Get the redirect URL based on the landing url configured for the user role,
        giving priority to the next URL from the request if available.

        Args:
            self: The object instance.
            user_role: The user's role.

        Returns:
            str: The redirect URL.
        """
        next_url = self.get_next_url_from_request()
        landing_page_url = self.get_landing_page_url(user_role)
        redirect_url = next_url or landing_page_url
        return redirect_url

    def __init__(self, **kwargs):
        super(ZelthyLoginView, self).__init__(**kwargs)
        self.user_cache = None
        self.device_cache = None

    condition_dict = {
        "user_role": has_role_step,
        "password_reset": has_password_reset_step,
    }

    def done(self, form_list, **kwargs):
        """
        Login the user and redirect to the desired page.
        """
        try:
            form_therapy = [
                form
                for form in form_list
                if isinstance(form, self.form_list.get("user_role"))
            ][0]
            user_role_id = form_therapy.cleaned_data["user_role"]
            user_role = self.get_user().roles.filter(id=user_role_id)[0]
        except Exception as e:
            active_roles = self.get_user().roles.filter(is_active=True)
            if active_roles.count() == 1:
                user_role = active_roles.first()
            elif self.get_user().roles.filter(is_active=True).count() == 1:
                user_role = self.get_user().roles.filter(is_active=True).first()
            else:
                raise Http404(
                    "User does not have any role mapped! Please contact support."
                )
        finally:
            self.request.selected_role_id = user_role.id
        try:
            form_password_reset = [
                form
                for form in form_list
                if isinstance(form, self.form_list.get("password_reset"))
            ][0]
            form_password_reset.save()

        except Exception as e:
            pass

        login(self.request, self.get_user(), backend=USER_AUTH_BACKEND)

        redirect_to = self.get_redirect_url(user_role)

        response = redirect(redirect_to)

        return response

    def get_form_kwargs(self, step=None):
        """
        AuthenticationTokenForm requires the user kwarg.
        """
        kwargs = {}

        if step == "user_role":
            kwargs.update({"user": self.get_user()})

        if step == "password_reset":
            kwargs.update({"user": self.get_user()})

        return kwargs

    def get_user(self):
        """
        Returns the user authenticated by the AuthenticationForm. Returns False
        if not a valid user; see also issue #65.
        """
        if not self.user_cache:
            data = self.storage.get_step_data("auth")
            form_obj = self.get_form(
                step="auth", data=self.storage.get_step_data("auth")
            )
            self.user_cache = form_obj.is_valid() and form_obj.user_cache
        return self.user_cache

    def get_form_metadata(self, step):
        self.storage.extra_data.setdefault("forms", {})
        return self.storage.extra_data["forms"].get(step, None)
