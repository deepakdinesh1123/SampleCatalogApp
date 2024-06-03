from zango.apps.appauth.models import UserRoleModel
from zango.core.utils import get_datetime_str_in_tenant_timezone


def get_user_profile(request, user_role):
    """
    Get the user profile based on the request and user role.

    Args:
        request: The request object.
        user_role: The user role object.

    Returns:
        dict: The user profile containing name, roles, and current role.
    """
    if user_role.name == "AnonymousUsers":
        profile = {
            "name": "AnonymousUsers",
            "roles": [],
            "current_role": "AnonymousUsers",
        }
        return profile

    user_roles = request.user.roles.all().exclude(name=user_role.name)
    roles = []

    for role in user_roles:
        roles.append({"label": role.name, "url": f"/switch_role/{role.id}"})

    profile = {
        "name": request.user.name,
        "email": request.user.email,
        "mobile_number": str(request.user.mobile) if request.user.mobile else "",
        "other_roles": roles,
        "is_active": request.user.is_active,
        "current_role": user_role.name,
        "date_of_registration": get_datetime_str_in_tenant_timezone(
            request.user.date_joined, request.tenant
        ),
        "last_login": get_datetime_str_in_tenant_timezone(
            request.user.last_login, request.tenant
        ),
    }
    return profile


def get_frame_config(request, user_role):
    """
    Get frame configuration for the given user role.
    If the user role does not have a frame, an empty dictionary is returned.

    Args:
        request: The request object.
        user_role: The user's role.

    Returns:
        dict: The frame configuration dictionary.
    """
    try:
        frame = user_role.frame
        frame_config_dict = frame.config
        user_profile = get_user_profile(request, user_role)
        frame_config_dict.update({"profile": user_profile})
        frame_config_dict.update(
            {
                "logo": request.tenant.logo.url if request.tenant.logo else None,
                "fav_icon": (
                    request.tenant.fav_icon.url if request.tenant.fav_icon else None
                ),
            }
        )
        return frame_config_dict
    except UserRoleModel.frame.RelatedObjectDoesNotExist:
        return {}


def get_frame_landing_url(request, user_role):
    """
    Retrieves the landing URL for a frame based on the request and user role.

    Parameters:
    - request: The request object
    - user_role: The role of the user accessing the frame.

    Returns:
    - The landing URL for the frame if available, otherwise None.
    """

    frame_config = get_frame_config(request, user_role)
    menu = frame_config.get("menu", [])
    if menu:
        return menu[0]["url"]

    return None
