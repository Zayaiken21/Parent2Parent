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
    # Above 27, bands widen to 5 years — older parents' day-to-day
    # experiences shift more slowly than a new parent's, so a tight
    # 2-year gap stops being the meaningful dividing line.
    "27_32": {"min": 27, "max": 32, "label": "27–32"},
    "32_37": {"min": 32, "max": 37, "label": "32–37"},
    "37_42": {"min": 37, "max": 42, "label": "37–42"},
    "42_47": {"min": 42, "max": 47, "label": "42–47"},
    "47_52": {"min": 47, "max": 52, "label": "47–52"},
    "52_57": {"min": 52, "max": 57, "label": "52–57"},
    "57_62": {"min": 57, "max": 62, "label": "57–62"},
    "62_65": {"min": 62, "max": 65, "label": "62–65"},
}

# Ordered list for dropdowns
AGE_BAND_ORDER = [
    "11_13", "13_15", "15_17", "18_21", "21_23", "23_25", "25_27",
    "27_32", "32_37", "37_42", "42_47", "47_52", "52_57", "57_62", "62_65",
]

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
# Security questions, keyed by band. Each band has its own multiple-
# choice question — shown as visible options, not a blind free-text
# guess — so it's genuinely answerable by anyone honestly in that
# band, while still being a light deterrent against picking a band
# that doesn't match reality. "correct_answer" is the option that
# must be selected; "distractor_answers" are plausible-sounding wrong
# options pulled from neighboring bands.
# -----------------------------------------------------------------
SECURITY_QUESTIONS: dict[str, dict] = {
    "11_13": {
        "key": "grade_school_11_13",
        "question": "Kids your child's age are usually in which school stage?",
        "correct_answer": "Middle school",
        "distractor_answers": ["High school", "College"],
    },
    "13_15": {
        "key": "grade_school_13_15",
        "question": "Kids your child's age are usually in which school stage?",
        "correct_answer": "Middle school or early high school",
        "distractor_answers": ["Elementary school", "College"],
    },
    "15_17": {
        "key": "grade_school_15_17",
        "question": "Kids your child's age are usually in which school stage?",
        "correct_answer": "High school",
        "distractor_answers": ["Middle school", "Already graduated college"],
    },
    "18_21": {
        "key": "milestone_18_21",
        "question": "At this age, a young adult is most likely:",
        "correct_answer": "Starting college or a first job",
        "distractor_answers": ["Still in middle school", "Settling into an established career"],
    },
    "21_23": {
        "key": "milestone_21_23",
        "question": "At this age, a young adult is most likely:",
        "correct_answer": "Graduating college or starting a career",
        "distractor_answers": ["Still in high school", "Retiring"],
    },
    "23_25": {
        "key": "milestone_23_25",
        "question": "At this age, a young adult is most likely:",
        "correct_answer": "Building an early career",
        "distractor_answers": ["Starting middle school", "Already retired"],
    },
    "25_27": {
        "key": "milestone_25_27",
        "question": "At this age, a young adult is most likely:",
        "correct_answer": "Advancing their career or starting a family",
        "distractor_answers": ["Starting high school", "In elementary school"],
    },
    "27_32": {
        "key": "milestone_27_32",
        "question": "At this age, an adult is most likely:",
        "correct_answer": "Building a career or growing a young family",
        "distractor_answers": ["Starting middle school", "Already retired"],
    },
    "32_37": {
        "key": "milestone_32_37",
        "question": "At this age, an adult is most likely:",
        "correct_answer": "Settled into a career or raising school-age kids",
        "distractor_answers": ["Starting their first job out of college", "In high school"],
    },
    "37_42": {
        "key": "milestone_37_42",
        "question": "At this age, an adult is most likely:",
        "correct_answer": "Mid-career, often raising older kids or teens",
        "distractor_answers": ["Just starting college", "Already in retirement"],
    },
    "42_47": {
        "key": "milestone_42_47",
        "question": "At this age, an adult is most likely:",
        "correct_answer": "Established in their career, kids often becoming teens or young adults",
        "distractor_answers": ["Starting their first job", "In elementary school"],
    },
    "47_52": {
        "key": "milestone_47_52",
        "question": "At this age, an adult is most likely:",
        "correct_answer": "Experienced in their career, often with teen or adult children",
        "distractor_answers": ["Just graduating high school", "Starting their first job"],
    },
    "52_57": {
        "key": "milestone_52_57",
        "question": "At this age, an adult is most likely:",
        "correct_answer": "Later career stage, often with adult children",
        "distractor_answers": ["In middle school", "Starting college"],
    },
    "57_62": {
        "key": "milestone_57_62",
        "question": "At this age, an adult is most likely:",
        "correct_answer": "Nearing retirement, often with grown children",
        "distractor_answers": ["Starting high school", "Beginning their career"],
    },
    "62_65": {
        "key": "milestone_62_65",
        "question": "At this age, an adult is most likely:",
        "correct_answer": "At or near retirement age",
        "distractor_answers": ["Starting college", "In middle school"],
    },
}


def security_question_options(age_band: str) -> list[str]:
    """Returns the visible multiple-choice options for a band's
    security question, in a stable (not randomized) order so the
    form doesn't shuffle between reruns within the same signup."""
    spec = SECURITY_QUESTIONS.get(age_band)
    if not spec:
        return []
    options = [spec["correct_answer"]] + list(spec["distractor_answers"])
    return sorted(options)  # stable alphabetical order, not "correct always first"


def normalize_answer(text: str) -> str:
    return " ".join(text.strip().lower().split())


def check_security_answer(age_band: str, submitted: str) -> bool:
    spec = SECURITY_QUESTIONS.get(age_band)
    if not spec:
        return False
    return normalize_answer(submitted) == normalize_answer(spec["correct_answer"])
