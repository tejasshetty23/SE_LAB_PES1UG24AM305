"""
Lab 6 - Step 5: tests written to raise LINE (code) coverage above 90%.

Run:
    coverage run -m pytest CodeCoverageTest_blood_donation_screening.py
    coverage report -m
"""
import pytest
from blood_donation_screening import process_donor_cohort, verify_storage_centrifuge


def make_cohort(donors, registered=True, ctype="standard", fast_track=False):
    return {
        "clinic_registered": registered,
        "type": ctype,
        "fast_track": fast_track,
        "donors": donors,
    }


GOOD = {"age": 25, "weight_kg": 65, "hb": 14.0}


# ---------------- process_donor_cohort ----------------

def test_single_accepted_donor():
    result = process_donor_cohort([make_cohort([GOOD])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_invalid_cohorts_not_a_list_raises():
    with pytest.raises(ValueError):
        process_donor_cohort("not a list", 450)


def test_unregistered_cohort_is_skipped():
    result = process_donor_cohort([make_cohort([GOOD], registered=False)], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_underage_donor_deferred():
    donor = {"age": 16, "weight_kg": 65, "hb": 14.0}
    result = process_donor_cohort([make_cohort([donor])], 450)
    assert result["status"] == "ZERO_YIELD"


def test_low_hemoglobin_high_altitude_resets_and_breaks():
    low = {"age": 30, "weight_kg": 70, "hb": 11.0}
    result = process_donor_cohort(
        [make_cohort([GOOD, low, GOOD], ctype="high_altitude")], 450
    )
    assert result["collected_ml"] == 0
    assert result["status"] == "ZERO_YIELD"


def test_high_hemoglobin_deferred():
    donor = {"age": 30, "weight_kg": 70, "hb": 19.0}
    result = process_donor_cohort([make_cohort([donor])], 450)
    assert result["status"] == "ZERO_YIELD"


def test_fast_track_adds_bonus_volume():
    result = process_donor_cohort([make_cohort([GOOD], fast_track=True)], 450)
    assert result == {"collected_ml": 500, "status": "ACCEPTED"}


def test_high_deferral_status():
    bad = {"age": 10, "weight_kg": 65, "hb": 14.0}
    result = process_donor_cohort([make_cohort([GOOD] + [bad] * 5)], 450)
    assert result == {"collected_ml": 450, "status": "HIGH_DEFERRAL"}


# ---------------- verify_storage_centrifuge ----------------

def test_centrifuge_no_data():
    assert verify_storage_centrifuge([]) == "NO_DATA"


def test_centrifuge_stable():
    assert verify_storage_centrifuge([[3500, 3600, 3400]]) == "STABLE"


def test_centrifuge_abort_on_consecutive_drops():
    assert verify_storage_centrifuge([[3500, 2900, 2800]]) == "ABORT_SPIN"
