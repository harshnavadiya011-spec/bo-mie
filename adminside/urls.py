
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminChangePasswordAPIView,
    AdminForgotPasswordAPIView,
    AdminLoginAPIView,
    AdminLogoutAPIView,
    AdminTokenRefreshAPIView,
    AdminUserViewSet,
    RoleView,
)


router = DefaultRouter()
router.register(r"role", RoleView, basename="role")
router.register(r"admins", AdminUserViewSet, basename="admins")

urlpatterns = [
    path("manage-roles/", include(router.urls)),

    path("auth/login/", AdminLoginAPIView.as_view(), name="admin-login"),
    path("auth/refresh/", AdminTokenRefreshAPIView.as_view(), name="admin-refresh-token"),
    path("auth/logout/", AdminLogoutAPIView.as_view(), name="admin-logout"),
    path("auth/forgot-password/", AdminForgotPasswordAPIView.as_view(), name="admin-forgot-password"),
    path("auth/change-password/", AdminChangePasswordAPIView.as_view(), name="admin-change-password")
]
