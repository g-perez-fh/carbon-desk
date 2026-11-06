from datetime import date

from rest_framework import serializers

from .models import Conversation, Message, MonthlySummary
from .services import MAX_MESSAGE_LENGTH


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "role", "content", "created_at"]
        read_only_fields = fields


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ["id", "title", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {"title": {"required": False}}


class ConversationDetailSerializer(ConversationSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta(ConversationSerializer.Meta):
        fields = [*ConversationSerializer.Meta.fields, "messages"]


class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=MAX_MESSAGE_LENGTH, trim_whitespace=True)


class MonthlySummarySerializer(serializers.ModelSerializer):
    generated_by = serializers.CharField(source="generated_by.username", default=None)

    class Meta:
        model = MonthlySummary
        fields = ["id", "month", "totals", "content", "generated_by", "updated_at"]
        read_only_fields = fields


class GenerateSummarySerializer(serializers.Serializer):
    month = serializers.DateField(input_formats=["%Y-%m", "%Y-%m-%d"])

    def validate_month(self, value):
        if value.replace(day=1) > date.today().replace(day=1):
            raise serializers.ValidationError("Summaries can only be generated for past months.")
        return value.replace(day=1)
