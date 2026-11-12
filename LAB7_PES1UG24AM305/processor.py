"""Input-validation examples for Lab 7: Hypothesis fuzz testing.

The functions deliberately validate untrusted input and raise ValueError for
malformed values rather than allowing accidental IndexError, KeyError,
ZeroDivisionError, or conversion exceptions to escape.
"""


def validate_blood_type(blood_code):
    """Normalize a valid ABO/Rh code, such as 'O+' or 'AB-'."""
    if not isinstance(blood_code, str):
        raise ValueError("Blood type must be a string.")

    cleaned = blood_code.strip().upper()
    if len(cleaned) < 2:
        raise ValueError("Blood type must contain an ABO group and Rh sign.")

    antigen = cleaned[:-1]
    rh_char = cleaned[-1]
    if antigen not in {"A", "B", "AB", "O"} or rh_char not in {"+", "-"}:
        raise ValueError("Invalid blood type. Expected A+, B-, AB+, O-, etc.")

    rh_map = {"+": "Positive", "-": "Negative"}
    return f"{antigen} {rh_map[rh_char]}"


def calculate_pulse_pressure(bp_string):
    """Calculate pulse pressure and systolic/diastolic ratio."""
    if not isinstance(bp_string, str):
        raise ValueError("Blood pressure must be a string.")

    parts = bp_string.strip().split("/")
    if len(parts) != 2:
        raise ValueError("Blood pressure must use systolic/diastolic format.")

    try:
        systolic, diastolic = (int(part.strip()) for part in parts)
    except (TypeError, ValueError) as exc:
        raise ValueError("Blood pressure values must be integers.") from exc

    if systolic <= 0 or diastolic <= 0:
        raise ValueError("Blood pressure values must be positive.")
    if systolic <= diastolic:
        raise ValueError("Systolic pressure must be greater than diastolic.")

    pulse_diff = systolic - diastolic
    ratio = round(systolic / diastolic, 2)
    return f"Diff: {pulse_diff}, Ratio: {ratio}"


def parse_donor_registry(donor_entry):
    """Parse 'DonorID|WeightKg|Hemoglobin' and determine basic eligibility."""
    if not isinstance(donor_entry, str):
        raise ValueError("Donor record must be a string.")

    fields = donor_entry.split("|")
    if len(fields) != 3:
        raise ValueError("Donor record must contain exactly three pipe-separated fields.")

    donor_id = fields[0].strip()
    if not donor_id:
        raise ValueError("Donor ID cannot be empty.")

    try:
        weight = float(fields[1].strip())
        hemoglobin = float(fields[2].strip())
    except (TypeError, ValueError) as exc:
        raise ValueError("Weight and hemoglobin must be numeric.") from exc

    # Reject NaN and positive/negative infinity.
    if not (weight == weight and hemoglobin == hemoglobin):
        raise ValueError("Weight and hemoglobin must be finite numbers.")
    if weight in (float("inf"), float("-inf")) or hemoglobin in (
        float("inf"), float("-inf")
    ):
        raise ValueError("Weight and hemoglobin must be finite numbers.")
    if weight < 0 or hemoglobin < 0:
        raise ValueError("Weight and hemoglobin cannot be negative.")

    eligible = weight >= 50.0 and hemoglobin >= 12.5
    return f"Donor {donor_id}: {'Eligible' if eligible else 'Deferred'}"


def main():
    print("==== Running validate_blood_type ====")
    b_input = input("Enter blood type (e.g. A+, O-, AB+): ")
    try:
        print("Validated:", validate_blood_type(b_input))
    except ValueError as exc:
        print("Invalid blood type:", exc)

    print("\n==== Running calculate_pulse_pressure ====")
    bp_input = input("Enter BP (e.g. 120/80): ")
    try:
        print("BP Metrics:", calculate_pulse_pressure(bp_input))
    except ValueError as exc:
        print("Invalid blood pressure:", exc)

    print("\n==== Running parse_donor_registry ====")
    d_input = input("Enter record (ID|Weight|Hemoglobin): ")
    try:
        print("Status:", parse_donor_registry(d_input))
    except ValueError as exc:
        print("Invalid donor record:", exc)


if __name__ == "__main__":
    main()
