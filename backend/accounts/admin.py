from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Alert, AuditLog, Organisation, ReductionTarget, Site, User


@admin.register(User)
class ProjectUserAdmin(UserAdmin):
    list_display = ["username", "email", "organisation", "role", "is_active", "is_staff"]
    list_filter = ["role", "organisation", *UserAdmin.list_filter]
    fieldsets = [*UserAdmin.fieldsets, ("Organisation", {"fields": ["organisation", "role"]})]


class SiteInline(admin.TabularInline):
    model = Site
    extra = 0


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ["name", "industry", "country", "employee_count", "created_at"]
    search_fields = ["name"]
    inlines = [SiteInline]


@admin.register(ReductionTarget)
class ReductionTargetAdmin(admin.ModelAdmin):
    list_display = ["organisation", "scope", "baseline_year", "target_year", "reduction_percent"]
    list_filter = ["organisation", "scope"]


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ["organisation", "level", "message", "is_read", "created_at"]
    list_filter = ["organisation", "level", "is_read"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["created_at", "organisation", "actor", "action", "object_type", "object_repr"]
    list_filter = ["organisation", "action"]
    readonly_fields = [field.name for field in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
