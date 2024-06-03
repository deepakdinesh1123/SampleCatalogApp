from rest_framework import serializers
from .models import FramesModel

class FramesModelSerializer(serializers.ModelSerializer):
    user_role = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = FramesModel
        fields = ["pk", "user_role", "config"]