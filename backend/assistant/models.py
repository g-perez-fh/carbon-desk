from django.conf import settings
from django.db import models


class Conversation(models.Model):
    """A private chat between one user and the assistant about their company."""

    organisation = models.ForeignKey(
        "accounts.Organisation", on_delete=models.CASCADE, related_name="conversations"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations"
    )
    title = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-id"]

    def __str__(self):
        return self.title or f"Conversation {self.pk}"


class Message(models.Model):
    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class MonthlySummary(models.Model):
    """Generated overview of one month's emissions for an organisation."""

    organisation = models.ForeignKey(
        "accounts.Organisation", on_delete=models.CASCADE, related_name="monthly_summaries"
    )
    month = models.DateField(help_text="First day of the summarised month.")
    totals = models.JSONField(default=dict)
    content = models.TextField()
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-month"]
        verbose_name_plural = "monthly summaries"
        constraints = [
            models.UniqueConstraint(
                fields=["organisation", "month"], name="unique_summary_per_month"
            )
        ]

    def __str__(self):
        return f"{self.organisation} {self.month:%B %Y}"
