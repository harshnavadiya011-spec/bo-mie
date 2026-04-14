
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    RoleView, AdminChangePasswordAPIView, AdminForgotPasswordAPIView, AdminLoginAPIView, AdminUserViewSet
)

router = DefaultRouter()
router.register(r"roles", RoleView, basename="roles")
router.register(r"admins", AdminUserViewSet, basename="admins")

urlpatterns = [
    path("manage-role/", include(router.urls)),
    path("auth/login/", AdminLoginAPIView.as_view(), name="admin-login"),
    path("auth/forgot-password/", AdminForgotPasswordAPIView.as_view(), name="admin-forgot-password"),
    path("auth/change-password/", AdminChangePasswordAPIView.as_view(), name="admin-change-password"),
]
