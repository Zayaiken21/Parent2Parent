"""
Child development curriculum: 0–21, grouped the way developmental
professionals commonly group it — tight 2-3 month increments in
early infancy, widening to multi-year spans as kids age, because
that's where the rate of change actually slows down.

This is reference/educational content, not medical advice. Each
stage includes:
  - age_range: display string
  - focus: the dominant developmental theme professionals track here
  - milestones: a few concrete, observable things at this stage
  - connection_tips: how a parent can build emotional connection
  - structure_tips: how a parent can build healthy structure/routines

Sources synthesized from CDC "Learn the Signs. Act Early." milestone
checklists, Cleveland Clinic's child development overview, and
standard lifespan-development stage groupings (e.g. Erikson-adjacent
early/middle/late adolescence splits). This is a plain-language
summary for a general parenting audience, not a clinical reference —
always encourage parents to talk to their pediatrician for anything
that worries them.
"""
from __future__ import annotations

CURRICULUM_STAGES: list[dict] = [
    {
        "stage_key": "0_3mo",
        "age_range": "0–3 months",
        "focus": "Automatic reflexes, bonding, first social smiles",
        "milestones": [
            "Calms when picked up or spoken to softly",
            "Follows faces and bright objects with their eyes",
            "Begins to smile in response to your voice or face",
            "Lifts head briefly during tummy time",
        ],
        "connection_tips": [
            "Hold and talk to your baby often — your voice is already familiar and calming.",
            "Make eye contact during feeding; this is some of the earliest bonding.",
        ],
        "structure_tips": [
            "Start a loose feed/sleep rhythm, not a strict schedule — babies this age need flexibility.",
            "Consistent bedtime routines (dim lights, quiet voice) start paying off even now.",
        ],
    },
    {
        "stage_key": "3_6mo",
        "age_range": "3–6 months",
        "focus": "Motor control, recognizing caregivers, early sounds",
        "milestones": [
            "Holds head steady without support",
            "Reaches for and grasps objects",
            "Laughs and makes vowel sounds ('ooh', 'aah')",
            "Recognizes familiar faces and may show stranger wariness starting",
        ],
        "connection_tips": [
            "Narrate your day out loud — babies absorb language rhythm long before words.",
            "Respond to their sounds like a conversation; it teaches turn-taking.",
        ],
        "structure_tips": [
            "Predictable nap/wake windows help mood regulation for both baby and parent.",
        ],
    },
    {
        "stage_key": "6_9mo",
        "age_range": "6–9 months",
        "focus": "Sitting, exploring, object permanence beginning",
        "milestones": [
            "Sits without support",
            "Passes objects between hands, bangs things together",
            "Babbles with consonant sounds ('ba-ba', 'da-da')",
            "Shows interest in peekaboo and where objects go",
        ],
        "connection_tips": [
            "Play peekaboo and simple turn-taking games; this is real relationship-building, not just fun.",
        ],
        "structure_tips": [
            "Babyproofing now prevents a lot of 'no' moments later — structure your space, not just your schedule.",
        ],
    },
    {
        "stage_key": "9_12mo",
        "age_range": "9–12 months",
        "focus": "Mobility, first words, separation awareness",
        "milestones": [
            "Pulls to stand, may cruise along furniture",
            "Says 'mama'/'dada' with meaning, or similar first words",
            "Waves bye-bye, points at things they want",
            "May show separation anxiety when you leave the room",
        ],
        "connection_tips": [
            "Stay calm and brief during goodbyes — a confident, predictable goodbye builds trust faster than a long, anxious one.",
        ],
        "structure_tips": [
            "Keep mealtime and bedtime routines consistent; predictability eases separation anxiety.",
        ],
    },
    {
        "stage_key": "1_3y",
        "age_range": "1–3 years (Toddlerhood)",
        "focus": "Rapid language growth, walking to running, independence-seeking",
        "milestones": [
            "Walks independently, then runs and climbs",
            "Vocabulary expands from a few words to short phrases",
            "Says 'no' and tests limits — a normal sign of identity forming",
            "Engages in pretend play",
        ],
        "connection_tips": [
            "Get on their level (literally — eye level) when talking, especially during big emotions.",
            "Narrate feelings for them: 'You're frustrated because the tower fell.' This builds emotional vocabulary.",
        ],
        "structure_tips": [
            "Offer small choices ('red cup or blue cup?') to satisfy their independence drive within safe limits.",
            "Keep routines visual and consistent — toddlers thrive on knowing what's next.",
        ],
    },
    {
        "stage_key": "3_5y",
        "age_range": "3–5 years (Preschool)",
        "focus": "Coordination, social play, early abstract thinking",
        "milestones": [
            "Hops, pedals a tricycle, draws basic shapes",
            "Plays cooperatively with other children, takes turns",
            "Asks lots of 'why' questions — genuine abstract thinking emerging",
            "Begins to understand rules and consequences",
        ],
        "connection_tips": [
            "Answer their 'why' questions seriously, even the silly-seeming ones — it tells them curiosity is welcome.",
            "Have dedicated one-on-one playtime with no phone, even 10–15 minutes, daily.",
        ],
        "structure_tips": [
            "Set a small number of clear, consistent house rules rather than many shifting ones.",
            "Use natural consequences ('toys left out get put away for the day') over punishment-first approaches.",
        ],
    },
    {
        "stage_key": "6_12y",
        "age_range": "6–12 years (School-Age)",
        "focus": "Academic skills, peer relationships, forming opinions outside the family",
        "milestones": [
            "Reads and writes with growing fluency",
            "Forms close friendships and begins to compare themselves to peers",
            "Develops interests and opinions that may differ from parents'",
            "Capable of more complex responsibility (chores, homework routines)",
        ],
        "connection_tips": [
            "Ask open questions about their day instead of yes/no ones ('what was the best part?' not 'good day?').",
            "Take their opinions seriously even when you disagree — this is when they decide whether home is a safe place to think out loud.",
        ],
        "structure_tips": [
            "Give them ownership of some structure (a homework routine they help design) rather than only imposed structure.",
            "Be consistent about screen-time and bedtime rules — this age tests limits more, not less.",
        ],
    },
    {
        "stage_key": "12_15y",
        "age_range": "12–15 years (Early Adolescence)",
        "focus": "Puberty onset, identity exploration begins, peer influence rises",
        "milestones": [
            "Physical changes of puberty begin or are underway",
            "Mood swings tied to both hormones and identity questions",
            "Peer approval starts to matter more than parent approval in daily choices",
            "Capable of more abstract, hypothetical thinking",
        ],
        "connection_tips": [
            "Stay available without forcing conversation — a lot of teens open up sideways (in the car, doing a task together) more than face-to-face.",
            "Avoid reacting strongly to the first thing they share, or they'll filter what they tell you next time.",
        ],
        "structure_tips": [
            "Shift from controlling every decision to setting boundaries with explained reasons — 'because I said so' loses effectiveness here.",
            "Keep a few non-negotiables (safety-related) and loosen the rest gradually as trust is shown.",
        ],
    },
    {
        "stage_key": "15_18y",
        "age_range": "15–18 years (Middle Adolescence)",
        "focus": "Identity solidifying, increasing autonomy, future-orientation",
        "milestones": [
            "Forms a clearer sense of personal identity and values",
            "Seeks more independence (driving, jobs, less supervision)",
            "Begins serious future-planning (school, work, relationships)",
            "Risk-taking behavior can increase as part of identity testing",
        ],
        "connection_tips": [
            "Treat them more like a young adult in conversation — ask their opinion on family decisions where appropriate.",
            "Keep showing up for the small stuff; presence matters more than long talks at this age.",
        ],
        "structure_tips": [
            "Co-create rules around new freedoms (curfew, driving) rather than dictating them unilaterally.",
            "Let natural consequences play out more — this is the practice ground for adult decision-making.",
        ],
    },
    {
        "stage_key": "18_21y",
        "age_range": "18–21 years (Late Adolescence / Emerging Adulthood)",
        "focus": "Transition to legal adulthood, major life decisions, evolving parent-child relationship",
        "milestones": [
            "Navigating college, work, or other major post-high-school paths",
            "Often living independently or semi-independently for the first time",
            "Forming long-term romantic and friend relationships as an adult",
            "Continuing to develop financial and emotional independence",
        ],
        "connection_tips": [
            "Shift from a parent-of-a-child voice to a parent-of-an-adult voice — advice offered, not imposed.",
            "Make space for them to come back for support without it feeling like a step backward for either of you.",
        ],
        "structure_tips": [
            "If they're still at home, renegotiate household structure as a household of adults, not parent-and-kid.",
            "Support without rescuing — let them own the consequences of adult decisions where safety isn't at stake.",
        ],
    },
]


def get_stage(stage_key: str) -> dict | None:
    for stage in CURRICULUM_STAGES:
        if stage["stage_key"] == stage_key:
            return stage
    return None


def stages_relevant_to_age_band(age_band: str) -> list[dict]:
    """All parenting guidance is available to everyone (per your
    requirement), but we can still suggest the stages most likely
    relevant to a parent whose OWN age band we know, by loosely
    mapping their age band to the child ages they're statistically
    most likely raising. This is a soft suggestion, never a filter —
    the full curriculum list is always browsable regardless.
    """
    suggestions = {
        "11_13": ["0_3mo", "3_6mo", "6_9mo", "9_12mo"],
        "13_15": ["0_3mo", "3_6mo", "6_9mo", "9_12mo", "1_3y"],
        "15_17": ["1_3y", "3_5y"],
        "18_21": ["3_5y", "6_12y"],
        "21_23": ["6_12y", "12_15y"],
        "23_25": ["12_15y", "15_18y"],
        "25_27": ["15_18y", "18_21y"],
        # Above 27, parents are statistically more likely raising
        # school-age kids through young adults — and at the older end,
        # are plausibly grandparents raising a grandchild, so we keep
        # the suggestion list broad rather than narrowing too far.
        "27_32": ["3_5y", "6_12y"],
        "32_37": ["6_12y", "12_15y"],
        "37_42": ["12_15y", "15_18y"],
        "42_47": ["15_18y", "18_21y"],
        "47_52": ["15_18y", "18_21y"],
        "52_57": ["0_3mo", "3_6mo", "6_9mo", "1_3y"],  # plausibly raising a grandchild
        "57_62": ["0_3mo", "3_6mo", "6_9mo", "1_3y"],
        "62_65": ["0_3mo", "3_6mo", "6_9mo", "1_3y"],
    }
    keys = suggestions.get(age_band, [])
    return [s for s in CURRICULUM_STAGES if s["stage_key"] in keys]
