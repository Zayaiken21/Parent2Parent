"""
Single source of truth for age bands. Every other module (signup,
chat room routing, avatar selection, security questions) reads from
here instead of hardcoding band strings, so adding/adjusting a band
later is a one-file change.
"""
from __future__ import annotations

from datetime import date
from typing import Optional

# Band key -> (min_age_inclusive, max_age_inclusive, display label)
AGE_BANDS: dict[str, dict] = {
    "11_13": {"min": 11, "max": 13, "label": "11–13"},
    "13_15": {"min": 13, "max": 15, "label": "13–15"},
    "15_17": {"min": 15, "max": 17, "label": "15–17"},
    "18_21": {"min": 18, "max": 21, "label": "18–21"},
    "21_23": {"min": 21, "max": 23, "label": "21–23"},
    "23_25": {"min": 23, "max": 25, "label": "23–25"},
    "25_27": {"min": 25, "max": 27, "label": "25–27"},
}

# Ordered list for dropdowns
AGE_BAND_ORDER = ["11_13", "13_15", "15_17", "18_21", "21_23", "23_25", "25_27"]

GENDER_LABELS = {"male": "Dads", "female": "Moms"}


def age_band_for_age(age: int) -> Optional[str]:
    """Return the band key whose range contains `age`.

    Bands overlap at their boundary years on purpose (e.g. 13 appears
    in both 11_13 and 13_15) to match how the source brief described
    the spans. We resolve overlaps by preferring the OLDER band, since
    that matches how people naturally describe "I'm 13, almost a
    teenager" rather than clinging to the younger bracket.
    """
    candidates = [
        key for key, span in AGE_BANDS.items()
        if span["min"] <= age <= span["max"]
    ]
    if not candidates:
        return None
    # Prefer the band with the higher "min" (the older-skewing one)
    return max(candidates, key=lambda k: AGE_BANDS[k]["min"])


def age_band_for_birth_year(birth_year: int, today: Optional[date] = None) -> Optional[str]:
    today = today or date.today()
    age = today.year - birth_year
    return age_band_for_age(age)


def room_key_for(age_band: str, gender: str) -> str:
    if gender not in ("male", "female"):
        raise ValueError("gender must be 'male' or 'female'")
    if age_band not in AGE_BANDS:
        raise ValueError(f"unknown age band: {age_band}")
    return f"{age_band}_{gender}"


def room_label_for(age_band: str, gender: str) -> str:
    return f"{AGE_BANDS[age_band]['label']} ({GENDER_LABELS[gender]})"


# -----------------------------------------------------------------
# Security questions, keyed by band. Each band has its own pool so a
# 12-year-old's parent and a 25-year-old's parent get a different
# question — but EVERY question is intentionally easy for someone
# who genuinely falls in that band and is being honest about their
# age. These are a light-touch deterrent against a 12-year-old typing
# in "25_27" to reach an adult chat room, not a hard security gate.
# -----------------------------------------------------------------
SECURITY_QUESTIONS: dict[str, dict] = {
    "11_13": {
        "key": "grade_school_11_13",
        "question": "Kids your child's age are usually in which school stage?",
        "accepted_answers": ["middle school", "elementary", "elementary school", "6th grade", "7th grade", "8th grade"],
    },
    "13_15": {
        "key": "grade_school_13_15",
        "question": "Kids your child's age are usually in which school stage?",
        "accepted_answers": ["middle school", "high school", "9th grade", "8th grade", "freshman"],
    },
    "15_17": {
        "key": "grade_school_15_17",
        "question": "Kids your child's age are usually in which school stage?",
        "accepted_answers": ["high school", "junior", "senior", "10th grade", "11th grade", "12th grade"],
    },
    "18_21": {
        "key": "milestone_18_21",
        "question": "At this age, a young adult is most likely:",
        "accepted_answers": ["starting college", "college", "first job", "moving out", "graduating high school"],
    },
    "21_23": {
        "key": "milestone_21_23",
        "question": "At this age, a young adult is most likely:",
        "accepted_answers": ["graduating college", "early career", "first apartment", "starting career"],
    },
    "23_25": {
        "key": "milestone_23_25",
        "question": "At this age, a young adult is most likely:",
        "accepted_answers": ["early career", "career", "building career", "settling into career"],
    },
    "25_27": {
        "key": "milestone_25_27",
        "question": "At this age, a young adult is most likely:",
        "accepted_answers": ["established career", "career growth", "starting a family", "advancing career"],
    },
}


def normalize_answer(text: str) -> str:
    return " ".join(text.strip().lower().split())


def check_security_answer(age_band: str, submitted: str) -> bool:
    spec = SECURITY_QUESTIONS.get(age_band)
    if not spec:
        return False
    norm = normalize_answer(submitted)
    return any(norm == normalize_answer(ans) for ans in spec["accepted_answers"])
