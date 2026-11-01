from pathlib import Path
import joblib

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from donors.models import DonorProfile, DonationRecord
from requests_app.models import BloodRequest


def home(request):
    context = {
        'total_donors': DonorProfile.objects.count(),

        'pending_requests': BloodRequest.objects.filter(
            status='PENDING'
        ).count(),

        'completed_donations': DonationRecord.objects.filter(
            is_verified=True
        ).count(),

        'upcoming_camps': 0,

        'emergency_requests': BloodRequest.objects.filter(
            request_type='EMERGENCY',
            status='VERIFIED'
        ).order_by('-created_at'),

        'camps': [],
    }

    return render(request, 'core/home.html', context)


@staff_member_required
def ml_analytics(request):
    analytics_path = (
        settings.BASE_DIR
        / 'ml_model'
        / 'visualizations'
        / 'analytics_results.joblib'
    )

    context = {
        'analytics_available': False,
    }

    if analytics_path.exists():
        try:
            results = joblib.load(analytics_path)

            context.update({
                'analytics_available': True,
                'model_name': results.get('model_name', 'Not available'),
                'features': results.get('features', []),
                'cv_results': [
    {
        'model': row['Model'],
        'accuracy': row['Accuracy'],
        'precision': row['Precision'],
        'recall': row['Recall'],
        'f1_score': row['F1 Score'],
    }
    for row in results.get('cv_results', [])
],
                'test_metrics': results.get('test_metrics_at_deployed_threshold', {}),
                'threshold_data': results.get('threshold_data', {}),
            })

        except Exception:
            context['analytics_error'] = (
                'Could not load the saved analytics results.'
            )
    else:
        context['analytics_error'] = (
            'Analytics results file was not found. '
            'Please generate the graphs again.'
        )

    return render(request, 'core/ml_analytics.html', context)