"""Error-handling behavior of the analytics services and API views."""

from datetime import date
from decimal import Decimal

import pytest

from accounts.models import Site
from analytics import services
from analytics.exceptions import ExportError, InvalidFilterError, NoDataError
from emissions.models import ActivityRecord, EmissionFactor

pytestmark = pytest.mark.django_db


@pytest.fixture
def one_record(organisation):
    site = Site.objects.create(organisation=organisation, name="Main office")
    factor = EmissionFactor.objects.create(
        organisation=organisation,
        name="Electricity",
        scope=2,
        unit="kWh",
        kg_per_unit=Decimal("1"),
        source="Synthetic test factor",
        year=2026,
    )
    ActivityRecord.objects.create(
        organisation=organisation,
        site=site,
        factor=factor,
        description="Electricity 2026-01-10",
        date=date(2026, 1, 10),
        quantity=Decimal("100"),
        category=factor.name,
        scope=factor.scope,
        unit=factor.unit,
        factor_value=factor.kg_per_unit,
        factor_source=factor.source,
        factor_year=factor.year,
        kg_co2e=Decimal("100"),
    )
    return ActivityRecord.objects.filter(organisation=organisation)


def test_filter_records_rejects_invalid_scope(organisation):
    with pytest.raises(InvalidFilterError):
        services.filter_records(organisation, scope=9)


def test_filter_records_rejects_end_before_start(organisation):
    with pytest.raises(InvalidFilterError):
        services.filter_records(organisation, start=date(2026, 3, 1), end=date(2026, 1, 1))


def test_export_csv_rejects_unsupported_format(one_record):
    with pytest.raises(ExportError):
        services.export_csv(one_record, format="pdf")


def test_export_csv_raises_no_data_for_empty_queryset(organisation):
    empty = ActivityRecord.objects.filter(organisation=organisation)
    with pytest.raises(NoDataError):
        services.export_csv(empty)


def test_export_csv_still_works_for_real_data(one_record):
    content = services.export_csv(one_record)
    assert "100" in content


def test_export_api_returns_404_json_for_no_data(api_for, viewer_user):
    response = api_for(viewer_user).get("/api/analytics/export/csv/")
    assert response.status_code == 404
    assert response.json() == {
        "error": "no_data",
        "detail": "No activity records matched these filters.",
    }


def test_export_api_rejects_unsupported_format(api_for, viewer_user, one_record):
    response = api_for(viewer_user).get("/api/analytics/export/csv/", {"export_format": "pdf"})
    assert response.status_code == 400
    assert response.json()["error"] == "export_error"


def test_export_api_still_returns_csv_by_default(api_for, viewer_user, one_record):
    response = api_for(viewer_user).get("/api/analytics/export/csv/")
    assert response.status_code == 200
    assert response.data["rows"] == 1
