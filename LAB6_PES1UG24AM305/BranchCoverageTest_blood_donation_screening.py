"""
Lab 6 - Step 7: tests written to raise BRANCH coverage above 90%.
Extends the code-coverage suite with the False/True side of every decision
and with boundary values (17 yrs, 50 kg, Hb 12.5 / 18.0, 3000 rpm, ...).

Run:
    coverage run --branch -m pytest BranchCoverageTest_blood_donation_screening.py
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


def donor(age=25, weight_kg=65, hb=14.0):
    return {"age": age, "weight_kg": weight_kg, "hb": hb}


# ================= process_donor_cohort: input validation =================

def test_single_accepted_donor():
    result = process_donor_cohort([make_cohort([donor()])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


@pytest.mark.parametrize("bad_cohorts", ["text", None, {"a": 1}, 5])
def test_non_list_cohorts_raises(bad_cohorts):
    with pytest.raises(ValueError):
        process_donor_cohort(bad_cohorts, 450)


@pytest.mark.parametrize("volume", [0, -100])
def test_non_positive_volume_raises(volume):
    with pytest.raises(ValueError):
        process_donor_cohort([make_cohort([donor()])], volume)


def test_empty_cohort_list_is_zero_yield():
    assert process_donor_cohort([], 450) == {"collected_ml": 0, "status": "ZERO_YIELD"}


# ================= registration / defaults =================

def test_unregistered_cohort_skipped_even_with_fast_track():
    result = process_donor_cohort([make_cohort([donor()], registered=False, fast_track=True)], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_missing_keys_use_defaults_and_are_skipped():
    # no "clinic_registered" key -> treated as not registered
    assert process_donor_cohort([{"donors": [donor()]}], 450)["status"] == "ZERO_YIELD"


def test_registered_cohort_without_donors_key():
    result = process_donor_cohort([{"clinic_registered": True}], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_donor_with_missing_fields_is_deferred():
    result = process_donor_cohort([make_cohort([{}])], 450)  # age=0 -> deferred
    assert result["status"] == "ZERO_YIELD"


# ================= age / weight boundaries =================

def test_age_16_deferred():
    assert process_donor_cohort([make_cohort([donor(age=16)])], 450)["collected_ml"] == 0


def test_age_17_accepted_boundary():
    assert process_donor_cohort([make_cohort([donor(age=17)])], 450)["collected_ml"] == 450


def test_weight_49_deferred():
    assert process_donor_cohort([make_cohort([donor(weight_kg=49)])], 450)["collected_ml"] == 0


def test_weight_50_accepted_boundary():
    assert process_donor_cohort([make_cohort([donor(weight_kg=50)])], 450)["collected_ml"] == 450


# ================= hemoglobin boundaries =================

def test_hb_just_below_min_deferred():
    assert process_donor_cohort([make_cohort([donor(hb=12.4)])], 450)["collected_ml"] == 0


def test_hb_exactly_min_accepted():
    assert process_donor_cohort([make_cohort([donor(hb=12.5)])], 450)["collected_ml"] == 450


def test_hb_exactly_max_accepted():
    assert process_donor_cohort([make_cohort([donor(hb=18.0)])], 450)["collected_ml"] == 450


def test_hb_just_above_max_deferred():
    assert process_donor_cohort([make_cohort([donor(hb=18.1)])], 450)["collected_ml"] == 0


def test_low_hb_standard_cohort_continues_to_next_donor():
    result = process_donor_cohort([make_cohort([donor(hb=10.0), donor()])], 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_low_hb_high_altitude_resets_total_and_stops_cohort():
    cohort = make_cohort([donor(), donor(hb=10.0), donor()], ctype="high_altitude")
    result = process_donor_cohort([cohort], 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_high_altitude_cohort_with_normal_hb_not_affected():
    cohort = make_cohort([donor(), donor()], ctype="high_altitude")
    assert process_donor_cohort([cohort], 450)["collected_ml"] == 900


def test_high_altitude_reset_also_wipes_earlier_cohorts():
    # documents current behaviour: total_collected_ml is global, not per cohort
    first = make_cohort([donor()])
    second = make_cohort([donor(hb=10.0)], ctype="high_altitude")
    result = process_donor_cohort([first, second], 450)
    assert result["collected_ml"] == 0


# ================= fast track =================

def test_fast_track_true_adds_50():
    result = process_donor_cohort([make_cohort([donor()], fast_track=True)], 450)
    assert result["collected_ml"] == 500


def test_fast_track_false_adds_nothing():
    result = process_donor_cohort([make_cohort([donor()], fast_track=False)], 450)
    assert result["collected_ml"] == 450


def test_fast_track_bonus_applies_even_after_high_altitude_break():
    # documents current behaviour: the +50 still happens after the inner break
    cohort = make_cohort([donor(hb=10.0)], ctype="high_altitude", fast_track=True)
    result = process_donor_cohort([cohort], 450)
    assert result == {"collected_ml": 50, "status": "ACCEPTED"}


# ================= final status =================

def test_deferred_count_exactly_4_is_not_high_deferral():
    donors = [donor()] + [donor(age=10)] * 4
    assert process_donor_cohort([make_cohort(donors)], 450)["status"] == "ACCEPTED"


def test_deferred_count_5_is_high_deferral():
    donors = [donor()] + [donor(age=10)] * 5
    result = process_donor_cohort([make_cohort(donors)], 450)
    assert result == {"collected_ml": 450, "status": "HIGH_DEFERRAL"}


def test_high_deferral_takes_priority_over_zero_yield():
    result = process_donor_cohort([make_cohort([donor(age=10)] * 5)], 450)
    assert result == {"collected_ml": 0, "status": "HIGH_DEFERRAL"}


def test_zero_yield_status():
    assert process_donor_cohort([make_cohort([donor(age=10)])], 450)["status"] == "ZERO_YIELD"


def test_multiple_cohorts_accumulate():
    cohorts = [make_cohort([donor()]), make_cohort([donor(), donor()], fast_track=True)]
    assert process_donor_cohort(cohorts, 100) == {"collected_ml": 350, "status": "ACCEPTED"}


# ================= verify_storage_centrifuge =================

@pytest.mark.parametrize("runs", [[], None])
def test_centrifuge_no_data(runs):
    assert verify_storage_centrifuge(runs) == "NO_DATA"


def test_centrifuge_all_good_is_stable():
    assert verify_storage_centrifuge([[3500, 3600], [4000]]) == "STABLE"


def test_centrifuge_empty_run_is_stable():
    assert verify_storage_centrifuge([[]]) == "STABLE"


def test_centrifuge_rpm_exactly_3000_is_not_a_drop():
    assert verify_storage_centrifuge([[3000, 3000, 3000]]) == "STABLE"


def test_centrifuge_single_drop_is_stable():
    assert verify_storage_centrifuge([[2999]]) == "STABLE"


def test_centrifuge_non_consecutive_drops_reset_streak():
    assert verify_storage_centrifuge([[2500, 3500, 2500, 3500]]) == "STABLE"


def test_centrifuge_two_consecutive_drops_abort():
    assert verify_storage_centrifuge([[3500, 2900, 2800]]) == "ABORT_SPIN"


def test_centrifuge_streak_does_not_carry_across_runs():
    assert verify_storage_centrifuge([[2500], [2500]]) == "STABLE"


def test_centrifuge_abort_in_later_run():
    assert verify_storage_centrifuge([[3500], [2000, 2000]]) == "ABORT_SPIN"
