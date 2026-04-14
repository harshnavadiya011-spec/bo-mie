from rest_framework import serializers

from .models import Admin, Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "deleted_at")

    def validate_permission(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Permission must be an array of permission codes.")

        normalized_permissions = []
        for permission_code in value:
            if not isinstance(permission_code, str) or not permission_code.strip():
                raise serializers.ValidationError("Each permission must be a non-empty string.")
            normalized_permissions.append(permission_code.strip())

        return list(dict.fromkeys(normalized_permissions))
    
    def validate(self, attrs):
        is_admin = attrs.get("is_admin")
        if self.instance is not None and "is_admin" not in attrs:
            is_admin = self.instance.is_admin

        if is_admin:
            attrs["permission"] = ["all"]

        return attrs
    
class RoleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "role", "permission", "is_admin")
        read_only_fields = fields
    
    def validate(self, attrs):
        is_admin = attrs.get("is_admin")
        if self.instance is not None and "is_admin" not in attrs:
            is_admin = self.instance.is_admin

        if is_admin:
            attrs["permission"] = ["all"]

        return attrs

class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Admin
        fields = (
            "id",
            "name",
            "email",
            "phone",
            "password",
            "status",
            "role",
            "created_at",
            "updated_at",
            "deleted_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "deleted_at")

    def create(self, validated_data):
        password = validated_data.pop("password")
        admin = Admin(**validated_data)
        admin.set_password(password)
        admin.save()
        return admin

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class AdminForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class AdminChangePasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()

class AdminLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()