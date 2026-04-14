from rest_framework import permissions


class IsRoleAdmin(permissions.BasePermission):
    """Allow access only to admins whose role is flagged as is_admin."""

    message = "Only admin roles can access this endpoint."

    def has_permission(self, request, view):
        admin = getattr(request, "user", None)
        role = getattr(admin, "role", None)
        return bool(admin and getattr(admin, "is_authenticated", False) and role and role.is_admin)


class HasRolePermission(permissions.BasePermission):
    """Permission checker based on role.permission codes with admin bypass."""

    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        admin = getattr(request, "user", None)
        if not admin or not getattr(admin, "is_authenticated", False):
            return False

        role = getattr(admin, "role", None)
        if not role:
            return False

        if role.is_admin:
            return True

        required_permissions = self._resolve_required_permissions(view)
        if not required_permissions:
            return True

        granted_permissions = {perm.strip() for perm in (role.permission or []) if isinstance(perm, str) and perm.strip()}
        return bool(granted_permissions.intersection(required_permissions))

    def _resolve_required_permissions(self, view):
        action = getattr(view, "action", None)
        permission_map = getattr(view, "required_permissions", {})

        if not isinstance(permission_map, dict):
            return set()

        required = permission_map.get(action, [])

        if isinstance(required, str):
            return {required}

        if isinstance(required, (list, tuple, set)):
            return {perm for perm in required if isinstance(perm, str) and perm}

        return set()