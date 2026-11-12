# Lab 7 — Fuzz Testing with Hypothesis

**Course folder:** `LAB7_PES1UG24AM305`

## Files
- `processor.py` — hardened input-processing application.
- `test_processor.py` — Hypothesis property-based fuzz tests and targeted validation tests.
- `requirements.txt` — Python test dependencies.
- `Lab7_FuzzTesting_Report.pdf` — add the screenshot report required by the lab handout after capturing the real terminal output.

## Run locally
From this directory:

```bash
python -m pip install -r requirements.txt
python processor.py
python -m pytest -v test_processor.py
```

For the interactive application, a valid demonstration input is:
- Blood type: `O+`
- Blood pressure: `120/80`
- Donor record: `D001|55|13.2`

Expected valid outputs:
- `O Positive`
- `Diff: 40, Ratio: 1.5`
- `Donor D001: Eligible`

## Required evidence from the lab handout
The PDF report must contain actual screenshots of:
1. The original buggy program running.
2. The fuzz tests failing against the original buggy program.
3. The fixed application running.
4. The fuzz tests passing against the fixed program.

Do not use simulated terminal output as evidence. To capture the first two screenshots, temporarily restore the original starter `processor.py` from the assigned course repository and run the original starter tests, then restore this fixed version before capturing the last two screenshots.

## Notes
The eligibility check follows the lab's starter logic: weight >= 50 kg and hemoglobin >= 12.5. These are the exercise's programmed criteria, not medical advice or a complete real-world donor-screening protocol.
