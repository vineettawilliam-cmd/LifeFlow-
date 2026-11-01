
from pathlib import Path

import joblib
import pandas as pd

from django.utils import timezone

from donors.models import DonationRecord


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "ml_model"
    / "saved_models"
    / "best_donor_model_v2.joblib"
)

THRESHOLD_PATH = (
    BASE_DIR
    / "ml_model"
    / "saved_models"
    / "donor_threshold_v2.joblib"
)


def months_between(start_date, end_date):
    """Calculate completed calendar months between two dates."""

    return (
        (end_date.year - start_date.year) * 12
        + end_date.month - start_date.month
        - (end_date.day < start_date.day)
    )


def get_donor_ai_insight(donor):
    """
    Generate an experimental donor-engagement insight
    using administrator-verified donation records only.
    """

    records = DonationRecord.objects.filter(
        donor=donor,
        is_verified=True
    ).order_by("donation_date")

    if not records.exists():
        return {
            "available": False,
            "reason": "Insufficient verified donation history.",
        }

    donation_dates = list(
        records.values_list("donation_date", flat=True)
    )

    today = timezone.localdate()

    first_date = donation_dates[0]
    latest_date = donation_dates[-1]

    recency = months_between(latest_date, today)
    frequency = len(donation_dates)
    total_time = months_between(first_date, today)

    # Validate against the historical training dataset ranges.
    if not (0 <= recency <= 74):
        return {
            "available": False,
            "reason": "Recency is outside the model's training range.",
        }

    if not (1 <= frequency <= 50):
        return {
            "available": False,
            "reason": "Donation frequency is outside the model's training range.",
        }

    if not (2 <= total_time <= 98):
        return {
            "available": False,
            "reason": "At least two months of donation history are required.",
        }

    # Load the V2 model and selected threshold.
    if not MODEL_PATH.exists() or not THRESHOLD_PATH.exists():
        return {
            "available": False,
            "reason": "The updated AI model or threshold file is missing.",
        }

    saved_data = joblib.load(MODEL_PATH)
    threshold_data = joblib.load(THRESHOLD_PATH)

    model = saved_data["model"]
    features = saved_data["features"]
    threshold = float(threshold_data["threshold"])

    # Prepare donor features.
    donor_data = pd.DataFrame([{
        "Recency (months)": recency,
        "Frequency (times)": frequency,
        "Time (months)": total_time,
    }])

    donor_data = donor_data[features]

    # Calculate positive-class probability.
    probability = float(
        model.predict_proba(donor_data)[0][1]
    )

    # Apply the training-selected high-recall threshold.
    prediction = int(probability >= threshold)

    return {
        "available": True,
        "prediction": prediction,
        "probability": round(probability * 100, 2),
        "threshold": round(threshold * 100, 2),
        "label": (
            "Higher historical return likelihood"
            if prediction == 1
            else "Lower historical return likelihood"
        ),
        "features": {
            "recency": recency,
            "frequency": frequency,
            "time": total_time,
        },
        "disclaimer": (
            "Experimental estimate based on an external historical dataset. "
            "This is not a medical assessment or a guarantee of future donation."
        ),
    }
