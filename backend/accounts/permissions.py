"""Role-based API permissions. Reuse these in every subsystem that exposes company data.

Roles: admins manage the organisation, editors enter data, viewers only read.
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOrganisationMember(BasePermission):
    message = "Your account is not linked to an organisation."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.organisation_id)


class IsOrganisationAdmin(IsOrganisationMember):
    message = "Only organisation administrators can do this."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_org_admin


class IsOrganisationAdminOrReadOnly(IsOrganisationMember):
    message = "Only organisation administrators can make changes."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and (
            request.method in SAFE_METHODS or request.user.is_org_admin
        )


class CanEditDataOrReadOnly(IsOrganisationMember):
    message = "Viewers have read-only access."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and (
            request.method in SAFE_METHODS or request.user.can_edit_data
        )
