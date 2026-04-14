from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Admin


class AdminJWTAuthentication(JWTAuthentication):
    """Authenticates Admin model instances using JWT access tokens."""

    def get_user(self, validated_token):
        admin_id = validated_token.get("admin_id") or validated_token.get("user_id")

        if not admin_id:
            raise exceptions.AuthenticationFailed("Token missing admin identity.")

        try:
            admin = Admin.objects.select_related("role").get(
                id=admin_id,
                deleted_at__isnull=True,
                status=True,
            )
        except Admin.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("Admin not found or inactive.") from exc

        return admin


# Backward compatible alias
AdminTokenAuthentication = AdminJWTAuthentication