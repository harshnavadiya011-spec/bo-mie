from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .authentication import AdminJWTAuthentication
from .models import Admin, Role
from .permissions import HasRolePermission, IsRoleAdmin

from .serializers import (
    AdminChangePasswordSerializer,
    AdminForgotPasswordSerializer,
    AdminLoginSerializer,
    AdminLogoutSerializer,
    AdminUserSerializer,
    RoleSerializer,
    RoleListSerializer
)


class RoleView(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated, IsRoleAdmin]

    def get_serializer_class(self):
        if self.action == "list":
            return RoleListSerializer
        return RoleSerializer

    def get_queryset(self):
        queryset = Role.objects.all()
        include_deleted = self.request.query_params.get("include_deleted") == "true"

        if not include_deleted:
            queryset = queryset.filter(deleted_at__isnull=True)

        return queryset

    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.save(update_fields=["deleted_at", "updated_at"])


class AdminUserViewSet(ModelViewSet):
    queryset = Admin.objects.select_related("role")
    serializer_class = AdminUserSerializer
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated, HasRolePermission]
    required_permissions = {
        "list": ["admin_get"],
        "retrieve": ["admin_get"],
        "create": ["admin_add"],
        "update": ["admin_update"],
        "partial_update": ["admin_update"],
        "destroy": ["admin_delete"],
    }


    def get_queryset(self):
        queryset = Admin.objects.select_related("role")
        include_deleted = self.request.query_params.get("include_deleted") == "true"

        if not include_deleted:
            queryset = queryset.filter(deleted_at__isnull=True)

        return queryset

    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.save(update_fields=["deleted_at", "updated_at"])


class AdminLoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            admin = Admin.objects.select_related("role").get(
                email=email,
                deleted_at__isnull=True,
                status=True,
            )
        except Admin.DoesNotExist:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        if not admin.verify_password(password):
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken()
        refresh["admin_id"] = admin.id
        refresh["role_id"] = admin.role_id
        refresh["is_admin"] = admin.role.is_admin

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "admin": {
                    "id": admin.id,
                    "name": admin.name,
                    "email": admin.email,
                    "phone": admin.phone,
                    "status": admin.status,
                    "role_id": admin.role_id,
                    "role": admin.role.role,
                    "permission": admin.role.permission,
                },
            },
            status=status.HTTP_200_OK,
        )


class AdminTokenRefreshAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        raw_refresh = request.headers.get("X-Refresh-Token", "")
        refresh_token = self._extract_token(raw_refresh)

        if not refresh_token:
            return Response(
                {"detail": "Provide refresh token in X-Refresh-Token header."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @staticmethod
    def _extract_token(raw_header_value):
        if not raw_header_value:
            return ""

        if raw_header_value.startswith("Bearer "):
            return raw_header_value.split(" ", 1)[1].strip()

        return raw_header_value.strip()


class AdminLogoutAPIView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        raw_refresh = request.headers.get("X-Refresh-Token", "")
        refresh_token = AdminTokenRefreshAPIView._extract_token(raw_refresh)

        if not refresh_token:
            return Response(
                {"detail": "Provide refresh token in X-Refresh-Token header."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({"detail": "Invalid or expired refresh token."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


class AdminForgotPasswordAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = AdminForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            admin = Admin.objects.get(email=email, deleted_at__isnull=True)
        except Admin.DoesNotExist:
            return Response(
                {"detail": "If this email exists, a reset token has been generated."},
                status=status.HTTP_200_OK,
            )

        uid = urlsafe_base64_encode(force_bytes(admin.pk))
        reset_token = default_token_generator.make_token(admin)

        return Response(
            {
                "detail": "Reset token generated.",
                "uid": uid,
                "reset_token": reset_token,
            },
            status=status.HTTP_200_OK,
        )


class AdminChangePasswordAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = AdminChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]

        try:
            admin_id = force_str(urlsafe_base64_decode(uid))
            admin = Admin.objects.get(pk=admin_id, deleted_at__isnull=True)
        except (TypeError, ValueError, OverflowError, Admin.DoesNotExist):
            return Response({"detail": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(admin, token):
            return Response({"detail": "Invalid or expired reset token."}, status=status.HTTP_400_BAD_REQUEST)

        admin.set_password(serializer.validated_data["new_password"])
        admin.save(update_fields=["password", "updated_at"])

        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)


# Backward-compatible aliases for old imports/usages.
AdminView = AdminUserViewSet