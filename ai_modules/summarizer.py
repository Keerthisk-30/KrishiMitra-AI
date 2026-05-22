from transformers import pipeline

# AI Summarizer Model

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)


def generate_summary(text):

    lower_text = text.lower()

    problem = ""
    cause = ""
    solutions = []
    prevention = []

    # ----------------------------
    # PEST ATTACK
    # ----------------------------

    if "pest" in lower_text or "insect" in lower_text:

        problem = (
            "Crop is affected by pest infestation."
        )

        cause = (
            "Pests may increase due to excess moisture, "
            "poor crop monitoring, or infected plants."
        )

        solutions.extend([
            "Use neem-based organic pesticides.",
            "Remove infected leaves immediately.",
            "Monitor crops regularly."
        ])

        prevention.extend([
            "Maintain field cleanliness.",
            "Inspect crops weekly."
        ])

    # ----------------------------
    # FUNGAL DISEASE
    # ----------------------------

    if "fungal" in lower_text or "fungus" in lower_text:

        problem = (
            "Fungal infection has affected the crop."
        )

        cause = (
            "Excess water stagnation and humidity "
            "can increase fungal growth."
        )

        solutions.extend([
            "Use organic fungicides.",
            "Improve drainage systems.",
            "Remove infected plant areas."
        ])

        prevention.extend([
            "Avoid water stagnation.",
            "Maintain proper airflow between plants."
        ])

    # ----------------------------
    # RAIN DAMAGE
    # ----------------------------

    if (
        "rain" in lower_text
        or "heavy rainfall" in lower_text
        or "water stagnation" in lower_text
        or "flood" in lower_text
    ):

        problem = (
            "Crop damage occurred due to heavy rainfall."
        )

        cause = (
            "Standing water weakens roots and "
            "reduces oxygen supply to crops."
        )

        solutions.extend([
            "Improve field drainage.",
            "Use raised-bed farming methods.",
            "Remove excess water quickly."
        ])

        prevention.extend([
            "Create water outlet channels.",
            "Monitor weather forecasts regularly."
        ])

    # ----------------------------
    # FERTILIZER ISSUES
    # ----------------------------

    if "fertilizer" in lower_text:

        problem = (
            "Crop health is affected by fertilizer imbalance."
        )

        cause = (
            "Excess fertilizer may damage roots "
            "and reduce soil quality."
        )

        solutions.extend([
            "Reduce excessive fertilizer usage.",
            "Use organic compost.",
            "Test soil nutrients regularly."
        ])

        prevention.extend([
            "Apply balanced fertilizers.",
            "Avoid over-fertilization."
        ])

    # ----------------------------
    # YELLOW LEAVES / GROWTH
    # ----------------------------

    if (
    "yellow" in lower_text
    or "nutrient" in lower_text
    or "deficiency" in lower_text):

        solutions.extend([
            "Use balanced nutrients and micronutrients.",
            "Maintain proper irrigation."
        ])

        prevention.extend([
            "Check soil health regularly."
        ])

    # ----------------------------
    # DEFAULT CASE
    # ----------------------------

    if not problem:

        problem = (
            "Crop health issue detected."
        )

        cause = (
            "Environmental or nutrient factors "
            "may affect crop growth."
        )

        solutions.extend([
            "Consult nearby agricultural experts.",
            "Monitor crop condition regularly."
        ])

        prevention.extend([
            "Maintain balanced irrigation and nutrition."
        ])

    # ----------------------------
    # REMOVE DUPLICATES
    # ----------------------------

    solutions = list(dict.fromkeys(solutions))

    prevention = list(dict.fromkeys(prevention))

    # ----------------------------
    # FINAL AI RESPONSE
    # ----------------------------

    final_output = f"""
Problem:
{problem}

Cause:
{cause}

Recommended Solutions:
- {' - '.join(solutions)}

Prevention Tips:
- {' - '.join(prevention)}
"""

    return final_output