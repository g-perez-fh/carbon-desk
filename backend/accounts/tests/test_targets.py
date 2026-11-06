from datetime import date
from decimal import Decimal

import pytest

from accounts.models import Alert, ReductionTarget
from accounts.services import TargetProgress, evaluate_targets, target_progress

pytestmark = pytest.mark.django_db


@pytest.fixture
def target(organisation):
    # 1000 kg in 2024, minus 50% by 2028: expected path 875 kg in 2025.
    return ReductionTarget.objects.create(
        organisation=organisation,
        baseline_year=2024,
        baseline_kg_co2e=Decimal("1000"),
        target_year=2028,
        reduction_percent=Decimal("50"),
    )


def test_target_value_is_derived_from_baseline(target):
    assert target.target_kg_co2e == Decimal("500.00")


def test_progress_without_emission_data(target, emissions):
    assert target_progress(target, as_of=date(2026, 6, 1)).status == TargetProgress.NO_DATA


@pytest.mark.parametrize(
    "scope_one, expected_status",
    [("800", TargetProgress.ON_TRACK), ("900", TargetProgress.AT_RISK), ("990", "off_track")],
)
def test_progress_against_linear_path(target, emissions, scope_one, expected_status):
    emissions[1] = Decimal(scope_one)
    progress = target_progress(target, as_of=date(2025, 12, 31))
    assert progress.reporting_year == 2025
    assert progress.expected_kg_co2e == Decimal("875.00")
    assert progress.status == expected_status


def test_current_year_is_extrapolated(target, emissions):
    emissions[2] = Decimal("400")  # recorded up to day 183 of 2026
    progress = target_progress(target, as_of=date(2026, 7, 2))
    assert progress.actual_kg_co2e == Decimal("400.00")
    assert progress.projected_kg_co2e == Decimal("797.81")  # 400 * 365 / 183
    assert progress.expected_kg_co2e == Decimal("750.00")
    assert progress.status == TargetProgress.AT_RISK


def test_scope_specific_target_ignores_other_scopes(organisation, emissions):
    target = ReductionTarget.objects.create(
        organisation=organisation,
        scope="2",
        baseline_year=2024,
        baseline_kg_co2e=Decimal("100"),
        target_year=2025,
        reduction_percent=Decimal("10"),
    )
    emissions.update({1: Decimal("5000"), 2: Decimal("80"), 3: Decimal("5000")})
    assert target_progress(target, as_of=date(2025, 12, 31)).status == TargetProgress.ON_TRACK


def test_evaluate_creates_one_alert_until_read(target, emissions):
    emissions[1] = Decimal("2000")
    as_of = date(2025, 12, 31)
    [alert] = evaluate_targets(target.organisation, as_of)
    assert alert.level == Alert.Level.CRITICAL and "off track" in alert.message
    assert evaluate_targets(target.organisation, as_of) == []
    alert.is_read = True
    alert.save()
    assert len(evaluate_targets(target.organisation, as_of)) == 1


def test_target_api_validates_and_reports_progress(api_for, admin_user, viewer_user, emissions):
    client = api_for(admin_user)
    payload = {
        "scope": "all",
        "baseline_year": 2024,
        "baseline_kg_co2e": "1000",
        "target_year": 2030,
        "reduction_percent": "42",
    }
    created = client.post("/api/accounts/targets/", payload)
    assert created.status_code == 201
    body = created.json()
    assert body["target_kg_co2e"] == "580.00"
    assert body["progress"]["status"] == "no_data"
    assert ReductionTarget.objects.get().created_by == admin_user

    assert client.post("/api/accounts/targets/", payload).status_code == 400
    backwards = {**payload, "target_year": 2020}
    assert client.post("/api/accounts/targets/", backwards).status_code == 400
    assert api_for(viewer_user).post("/api/accounts/targets/", payload).status_code == 403


def test_alert_api_evaluate_and_mark_read(api_for, viewer_user, target, emissions):
    emissions[1] = Decimal("5000")
    client = api_for(viewer_user)
    created = client.post("/api/accounts/targets/evaluate/").json()
    assert len(created) == 1

    unread = client.get("/api/accounts/alerts/?unread=true").json()
    assert len(unread) == 1
    client.post(f"/api/accounts/alerts/{unread[0]['id']}/read/")
    assert client.get("/api/accounts/alerts/?unread=true").json() == []
