import os
import json


from django.views.generic import TemplateView

from rest_framework.views import APIView

from zango.core.api import get_api_response
from zango.apps.appauth.models import UserRoleModel

from .serializers import LoginConfigModelSerializer
from .models import LoginConfigModel, GenericLoginConfigModel
from .mixin import ConfigViewMixin


class LoginConfigureView(TemplateView, ConfigViewMixin):
    template_name = "login/login_configure.html"
    success_url = "/login/configure/"


class LoginConfigureAPIView(APIView, ConfigViewMixin):
    success_url = "/login/configure/"

    def get(self, request, *args, **kwargs):
        action = request.GET.get("action", "")
        if action == "get_configs":
            generic_config_obj = GenericLoginConfigModel.objects.last()
            generic_config = {}
            if generic_config_obj:
                generic_config = {
                    "config": generic_config_obj.config or {},
                    "background_image": request.build_absolute_uri(
                        generic_config_obj.background_image.url
                    )
                    if generic_config_obj.background_image
                    else None,
                    "logo": request.build_absolute_uri(generic_config_obj.logo.url)
                    if generic_config_obj.logo
                    else None,
                }

            login_configs = LoginConfigModelSerializer(
                LoginConfigModel.objects.all().order_by("-modified_at"), many=True
            ).data

            config = {
                "generic_config": generic_config,
                "login_configs": login_configs,
            }
            return get_api_response(True, config, 200)

        if action == "initialize_form":
            path = os.path.dirname(os.path.realpath(__file__))
            with open(f"{path}/config_form_schema.json", "r") as f:
                schema = json.load(f)
                user_roles = UserRoleModel.objects.all().exclude(name="AnonymousUsers")
                schema["json_schema"]["properties"]["user_role_configs"]["items"][
                    "properties"
                ]["user_role"]["enum"] = [str(obj.pk) for obj in user_roles]
                schema["json_schema"]["properties"]["user_role_configs"]["items"][
                    "properties"
                ]["user_role"]["enumNames"] = [obj.name for obj in user_roles]

                schema["form_data"] = {}

                generic_config = GenericLoginConfigModel.objects.last()
                if generic_config:
                    schema["form_data"] = generic_config.config or {}
                    if generic_config.logo:
                        schema["json_schema"]["properties"]["logo"][
                            "default"
                        ] = request.build_absolute_uri(generic_config.logo.url)
                    if generic_config.background_image:
                        schema["json_schema"]["properties"]["background_image"][
                            "default"
                        ] = request.build_absolute_uri(
                            generic_config.background_image.url
                        )

                login_configs = LoginConfigModel.objects.all()
                user_role_configs = []
                for login_config in login_configs:
                    config = login_config.config or {}
                    user_role_configs.append(
                        {
                            "user_role": str(login_config.user_role.id),
                            "url": config.get("landing_url"),
                        }
                    )
                if user_role_configs:
                    schema["form_data"]["user_role_configs"] = user_role_configs
                return get_api_response(True, {"form": schema}, 200)

    def post(self, request, *args, **kwargs):
        body = request.data
        action = request.GET.get("action", "")
        if action == "save_config":
            generic_config = {
                "header_text": body.get("header_text", ""),
                "paragraph_text": body.get("paragraph_text", ""),
                "paragraph_text_color": body.get("paragraph_text_color", "#FFFFFF"),
                "background_color": body.get("background_color", "#5048ED"),
                "card_title": body.get("card_title", ""),
                "card_color": body.get("card_color", "#5048ED"),
                "card_text_color": body.get("card_text_color", "#6c747d"),
                "corner_radius": int(body.get("corner_radius", 4)),
                "logo_placement": body.get("logo_placement", "topLeft"),
            }

            generic_config_data = {
                "config": generic_config,
                "background_image": body.get("background_image"),
                "logo": body.get("logo"),
            }

            # Check if a GenericLoginConfigModel object exists
            try:
                generic_config_model = GenericLoginConfigModel.objects.get()
                if type(generic_config_data.get("background_image")) == str:
                    generic_config_data.pop("background_image", None)
                if type(generic_config_data.get("logo")) == str:
                    generic_config_data.pop("logo", None)

                # If it exists, update its attributes with new data
                for key, value in generic_config_data.items():
                    setattr(generic_config_model, key, value)
                generic_config_model.save()
            except GenericLoginConfigModel.DoesNotExist:
                # If it doesn't exist, create a new object with the provided data
                GenericLoginConfigModel.objects.create(**generic_config_data)

            user_role_configs = json.loads(body.get("user_role_configs", "[]"))

            # Check for duplicate user role
            user_role_ids = [config.get("user_role") for config in user_role_configs]
            if len(user_role_ids) != len(set(user_role_ids)):
                error_respone = {
                    "user_role_configs": {
                        "__errors": [
                            "Duplicate user role found in routing configuration"
                        ]
                    }
                }
                return get_api_response(False, {"errors": error_respone}, 400)

            for role_config in user_role_configs:
                user_role_id = role_config.get("user_role")
                url = role_config.get("url")
                login_config, _ = LoginConfigModel.objects.get_or_create(
                    user_role_id=user_role_id
                )
                config = login_config.config or {}
                config.update({"landing_url": url})
                login_config.config = config
                login_config.save()

            # Remove any login configs that are not in the user_role_configs list
            LoginConfigModel.objects.exclude(user_role_id__in=user_role_ids).delete()

            return get_api_response(True, "Configuration Saved", 200)

        return get_api_response(False, "Invalid action", 400)

    def delete(self, request, *args, **kwargs):
        action = request.GET.get("action", "")
        if action == "delete_config":
            generic_config_obj = GenericLoginConfigModel.objects.last()
            if generic_config_obj:
                generic_config_obj.delete()

            login_configs = LoginConfigModel.objects.all()
            login_configs.delete()

            return get_api_response(True, "Login Config Deleted", 200)

        return get_api_response(False, "Invalid action", 400)
