"""Read-only analytics endpoints. Every member of an organisation may view them."""

from datetime import date
from decimal import Decimal

from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsOrganisationMember
from emissions.serializers import ActivityFilterSerializer

from . import services
from .exceptions import AnalyticsError


class AnalyticsAPIView(APIView):
    """An APIView that turns any AnalyticsError into a clean JSON error response."""

    def handle_exception(self, exc):
        if isinstance(exc, AnalyticsError):
            return Response(exc.as_response_data(), status=exc.status_code)
        return super().handle_exception(exc)


def as_json(value):
    """Send money-like Decimals as strings, the same way the other subsystems do."""
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {key: as_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [as_json(item) for item in value]
    return value


def filtered_records(request):
    """Validate ?start=&end=&scope=&site= and return the organisation's matching records."""
    filters = ActivityFilterSerializer(data=request.query_params, context={"request": request})
    filters.is_valid(raise_exception=True)
    return services.filter_records(request.user.organisation, **filters.validated_data)


class DashboardView(AnalyticsAPIView):
    permission_classes = [IsOrganisationMember]

    def get(self, request):
        records = filtered_records(request)
        return Response(as_json(services.dashboard(request.user.organisation, records)))


class ExportCsvView(AnalyticsAPIView):
    """Return the CSV inside JSON so the frontend can reuse its normal API helper."""

    permission_classes = [IsOrganisationMember]

    def get(self, request):
        records = filtered_records(request)
        export_format = request.query_params.get("export_format", "csv")
        content = services.export_csv(records, format=export_format)
        return Response(
            {
                "filename": f"carbondesk-emissions-{date.today().isoformat()}.csv",
                "rows": records.count(),
                "content": content,
            }
        )
