from django.contrib import admin

from .models import Conversation, Message, MonthlySummary


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ["role", "content", "created_at"]


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["title", "organisation", "user", "updated_at"]
    list_filter = ["organisation"]
    inlines = [MessageInline]


@admin.register(MonthlySummary)
class MonthlySummaryAdmin(admin.ModelAdmin):
    list_display = ["organisation", "month", "generated_by", "updated_at"]
    list_filter = ["organisation"]
