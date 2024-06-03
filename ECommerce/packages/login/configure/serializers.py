from rest_framework import serializers

from .models import LoginConfigModel


class LoginConfigModelSerializer(serializers.ModelSerializer):
    user_role = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = LoginConfigModel
        fields = ["pk", "user_role", "config"]
