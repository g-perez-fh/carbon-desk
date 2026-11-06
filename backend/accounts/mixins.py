from .models import AuditLog
from .services import describe_changes, record_audit


class OrganisationScopedMixin:
    """Limit a DRF view to the requesting user's organisation and audit its writes.

    Querysets are filtered by the ``organisation`` field and new objects are attached
    to the user's organisation, so one company never sees another company's records.
    Combine with a permission from ``accounts.permissions``.
    """

    audit = True

    def get_queryset(self):
        return super().get_queryset().filter(organisation=self.request.user.organisation)

    def extra_save_kwargs(self):
        """Override to set more server-controlled fields on create, e.g. ``created_by``."""
        return {}

    def perform_create(self, serializer):
        instance = serializer.save(
            organisation=self.request.user.organisation, **self.extra_save_kwargs()
        )
        if self.audit:
            record_audit(actor=self.request.user, action=AuditLog.Action.CREATE, instance=instance)

    def perform_update(self, serializer):
        changes = describe_changes(serializer.instance, serializer.validated_data)
        instance = serializer.save()
        if self.audit and changes:
            record_audit(
                actor=self.request.user,
                action=AuditLog.Action.UPDATE,
                instance=instance,
                changes=changes,
            )

    def perform_destroy(self, instance):
        if self.audit:
            record_audit(actor=self.request.user, action=AuditLog.Action.DELETE, instance=instance)
        instance.delete()
