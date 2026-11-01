from accounts.models import CustomUser
from donors.models import DonorProfile, DonationRecord
from requests_app.models import BloodRequest, DonorResponse


def admin_dashboard_stats(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}

    return {
        "total_users": CustomUser.objects.count(),
        "total_donors": DonorProfile.objects.count(),
        "available_donors": DonorProfile.objects.filter(
            availability="YES"
        ).count(),

        "total_requests": BloodRequest.objects.count(),
        "pending_requests": BloodRequest.objects.filter(
            status="PENDING"
        ).count(),
        "verified_requests": BloodRequest.objects.filter(
            status="VERIFIED"
        ).count(),
        "emergency_requests": BloodRequest.objects.filter(
            request_type="EMERGENCY",
            status="PENDING"
        ).count(),
        "completed_requests": BloodRequest.objects.filter(
            status="COMPLETED"
        ).count(),

        "verified_donations": DonationRecord.objects.filter(
            is_verified=True
        ).count(),

        "total_responses": DonorResponse.objects.count(),
    }