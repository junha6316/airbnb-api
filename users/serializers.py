from re import A
from django.db.models import fields
from .models import User

from rest_framework import serializers

class RelatedUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "avatar",
            "superhost"
        )

class ReadUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = [
            "groups",
            "user_permissions",
            "password",
            "last_login",
            "is_superuser",
            "is_staff",
            "is_active",
            "favs",
            "date_joined",
        ]

class WriteUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email"
        )

class UserSerializer(serializers.ModelSerializer): 

    password = serializers.CharField(write_only=True)
    #password 부분을 overwrite
    class Meta:
        model = User
        fields =  (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "avatar",
            "superhost",
            "password",
        )

        read_only_fields = [
            "id", "superhost", "avatar"
        ]

    def validate_first_name(self, value):
        return value.upper()

    def create(self, validated_data):
        password = validated_data.get("password")
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user