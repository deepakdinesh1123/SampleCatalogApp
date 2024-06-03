import os
import json

from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from rest_framework.views import APIView

from zango.apps.appauth.models import UserRoleModel
from zango.core.api import get_api_response

from .models import FramesModel
from .serializers import FramesModelSerializer


class FrameConfigureView(TemplateView):
    template_name = "frame/frame_configure.html"
    success_url = "/frame/configure/"

    def get_token(self):
        token = self.request.GET.get("token")
        return token

    def get_success_url(self):
        token = self.get_token()
        if token:
            return f"{self.success_url}?token={token}"
        return self.success_url


class FrameConfigureAPI(APIView):
    def get(self, request, *args, **kwargs):
        action = request.GET.get("action", "")
        if action == "delete":
            obj = FramesModel.objects.get(id=request.GET.get("id"))
            obj.delete()
            return redirect(self.get_success_url())
        if action == "get_configs":
            frames = FramesModelSerializer(
                FramesModel.objects.all().order_by("-modified_at"), many=True
            ).data
            return get_api_response(True, frames, 200)
        if action == "initialize_form":
            path = os.path.dirname(os.path.realpath(__file__))
            with open(f"{path}/schema.json", "r") as f:
                schema = json.load(f)
                user_roles = UserRoleModel.objects.exclude(name="SystemUsers").exclude(
                    id__in=FramesModel.objects.values("user_role")
                )
                schema["json_schema"]["properties"]["user_role"]["enum"] = [
                    obj.pk for obj in user_roles
                ]
                schema["json_schema"]["properties"]["user_role"]["enumNames"] = [
                    obj.name for obj in user_roles
                ]
                return get_api_response(True, {"form": schema}, 200)
        if action == "get_edit_form_schema":
            path = os.path.dirname(os.path.realpath(__file__))
            pk = request.GET.get("pk", None)
            frame = FramesModel.objects.get(pk=pk)
            current_role = frame.user_role
            with open(f"{path}/schema.json", "r") as f:
                schema = json.load(f)

                user_roles = UserRoleModel.objects.exclude(name="SystemUsers").exclude(
                    id__in=FramesModel.objects.values("user_role")
                )
                enum = schema["json_schema"]["properties"]["user_role"]["enum"] = [
                    obj.pk for obj in user_roles
                ]
                enumNames = schema["json_schema"]["properties"]["user_role"][
                    "enumNames"
                ] = [obj.name for obj in user_roles]
                enum.append(current_role.pk)
                enumNames.append(current_role.name)
                schema["json_schema"]["properties"]["user_role"]["enum"] = enum
                schema["json_schema"]["properties"]["user_role"][
                    "enumNames"
                ] = enumNames
                schema["json_schema"]["title"] = "Update Frame Config"
                schema["form_data"] = model_to_dict(FramesModel.objects.get(pk=pk))
                schema["form_data"]["config"] = frame.config.get("config")
                schema["form_data"]["menu"] = frame.config.get("menu", [])
                if frame.config.get("scripts"):
                    schema["form_data"]["scripts"] = frame.config.get("scripts")

            return get_api_response(True, {"form": schema}, 200)

    def post(self, request, *args, **kwargs):
        body = request.data
        action = request.GET.get("action", "")
        if action == "create_config":
            role_pk = body["user_role"]
            user_role = UserRoleModel.objects.get(pk=role_pk)
            try:
                config = {
                    "menu": json.loads(body.get("menu")) if body.get("menu") else [],
                    "config": json.loads(body.get("config"))
                    if body.get("config")
                    else {},
                    "scripts": body.getlist("scripts", []),
                }
                FramesModel.objects.create(config=config, user_role=user_role)
                return get_api_response(True, "config created", 200)
            except Exception as e:
                return get_api_response(False, str(e), 500)

    def put(self, request, *args, **kwargs):
        body = request.data
        action = request.GET.get("action", "")
        pk = request.GET.get("pk", None)
        if action == "update_config":
            frame = FramesModel.objects.get(pk=pk)
            config = {
                "menu": json.loads(body.get("menu")) if body.get("menu") else [],
                "config": json.loads(body.get("config")) if body.get("config") else {},
                "scripts": body.getlist("scripts", []),
            }
            frame.config = config
            if body.get("user_role"):
                frame.user_role = UserRoleModel.objects.get(pk=body["user_role"])
            frame.save()
            return get_api_response(True, "config updated", 200)
        return get_api_response(False, "Invalid action", 400)

    def delete(self, request, *args, **kwargs):
        action = request.GET.get("action", "")
        pk = request.GET.get("pk", None)
        if action == "delete_config":
            frame = FramesModel.objects.get(pk=pk)
            frame.delete()
            return get_api_response(True, "config deleted", 200)
        return get_api_response(False, "Invalid action", 400)
