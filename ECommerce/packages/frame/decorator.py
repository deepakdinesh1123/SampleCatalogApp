import json
from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import ImproperlyConfigured

from zango.core.utils import get_current_role
from zango.core.utils import get_current_request
from zango.apps.shared.tenancy.models import ThemesModel

from .helpers import get_frame_config, get_frame_landing_url


def add_frame_context(view_func_or_class):
    """
    Decorator to add frame context to the view function or class.

    Args:
        view_func_or_class: The view function or class to which the frame context will be added.

    Returns:
        The context with the frame configuration added.
    """

    @wraps(view_func_or_class)
    def _wrapped_view(instance, **kwargs):
        user_role = get_current_role()
        request = get_current_request()
        frame_config_dict = get_frame_config(request, user_role)
        context = view_func_or_class(instance, **kwargs)

        if not isinstance(context, dict):
            raise ValueError(
                f"Expected view {view_func_or_class.__name__} to return a dictionary as context."
            )
        display_sidebar = context.get("display_sidebar", True)
        frame_config_dict["display_sidebar"] = display_sidebar
        scripts = frame_config_dict.pop("scripts", [])
        app_theme = ThemesModel.objects.filter(
            tenant=request.tenant, is_active=True
        ).first()
        if app_theme:
            frame_config = {
                "frame_config": json.dumps(frame_config_dict),
                "app_theme_config": json.dumps(app_theme.config),
            }
        else:
            frame_config = {"frame_config": json.dumps(frame_config_dict)}
        context.update(**frame_config)
        context["scripts"] = scripts
        return context

    return _wrapped_view


def apply_frame_routing(view_func_or_class):
    """
    Decorator to apply frame routing logic.

    - Checks the current user's role and frame configuration.
    - Redirects the user if necessary based on frame configuration or role.
    - Redirects to the first menu item's URL if a frame configuration for user role is found.
    - Redirects anonymous users to the login page if no frame configuration is found for AnonymousUsers user role.
    - Raises ImproperlyConfigured if no frame configuration is found for the user's role.

    Args:
        view_func_or_class (function or class): The view function or class to decorate.

    Returns:
        function or class: Decorated function or class.
    """

    @wraps(view_func_or_class)
    def _wrapped_view(instance, *args, **kwargs):
        request = get_current_request()
        user_role = get_current_role()
        frame_landing_url = get_frame_landing_url(request, user_role)
        if frame_landing_url:
            return redirect(frame_landing_url)

        if user_role.name == "AnonymousUsers":
            return redirect("/login/")
        raise ImproperlyConfigured(
            f"Frame is not configured {user_role.name} user role."
        )

    return _wrapped_view
