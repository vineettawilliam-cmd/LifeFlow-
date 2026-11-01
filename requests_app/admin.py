
from django.contrib import admin, messages
from django.db import transaction
from django.db.models import Q

from .models import BloodRequest, DonorResponse
from donors.models import DonorProfile, DonorNotification


def notify_matching_donors(blood_request):
    """
    Notify available, emergency-willing donors in the same district
    whose blood group exactly matches the request.

    Unknown blood groups and non-red-cell components are left
    for manual review.
    """

    if blood_request.blood_group == 'UNKNOWN':
        return 0

    if blood_request.component not in ['WHOLE_BLOOD', 'PRBC']:
        return 0

    matching_donors = DonorProfile.objects.filter(
        blood_group=blood_request.blood_group,
        availability='YES',
        emergency_willingness=True,
        district__iexact=blood_request.district.strip()
    )

    notification_count = 0

    for donor in matching_donors:
        _, created = DonorNotification.objects.get_or_create(
            donor=donor,
            title=f'Emergency Blood Request - {blood_request.reference_code}',
            notification_type='EMERGENCY',
            defaults={
                'message': (
                    f'An emergency blood request matching your blood group '
                    f'({blood_request.blood_group}) has been verified. '
                    f'Hospital: {blood_request.hospital_name}. '
                    f'City: {blood_request.city}. '
                    f'Units required: {blood_request.units_required}. '
                    f'Urgency: {blood_request.get_urgency_display()}. '
                    f'Please open the emergency request page to view details '
                    f'and respond if you are willing.'
                )
            }
        )

        if created:
            notification_count += 1

    return notification_count


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'reference_code',
        'patient_name',
        'request_type',
        'blood_group',
        'units_required',
        'urgency',
        'hospital_name',
        'status',
        'requester',
        'created_at',
    )

    list_filter = (
        'request_type',
        'blood_group',
        'urgency',
        'status',
        'district',
        'created_at',
    )

    search_fields = (
        'reference_code',
        'patient_name',
        'hospital_name',
        'bystander_name',
        'bystander_contact',
    )

    readonly_fields = (
        'reference_code',
        'created_at',
        'updated_at',
    )

    list_per_page = 25

    actions = ['approve_requests', 'reject_requests']

    @admin.action(description='Approve selected blood requests')
    def approve_requests(self, request, queryset):

        approved_count = 0
        notification_count = 0

        with transaction.atomic():

            pending_requests = queryset.filter(status='PENDING')

            for blood_request in pending_requests:
                blood_request.status = 'VERIFIED'
                blood_request.save(update_fields=['status', 'updated_at'])

                approved_count += 1

                if blood_request.request_type == 'EMERGENCY':
                    notification_count += notify_matching_donors(
                        blood_request
                    )

        self.message_user(
            request,
            (
                f'{approved_count} blood request(s) approved. '
                f'{notification_count} emergency notification(s) created.'
            ),
            messages.SUCCESS
        )

    @admin.action(description='Reject selected blood requests')
    def reject_requests(self, request, queryset):

        updated = queryset.filter(status='PENDING').update(
            status='REJECTED'
        )

        self.message_user(
            request,
            f'{updated} blood request(s) rejected.',
            messages.SUCCESS
        )


@admin.register(DonorResponse)
class DonorResponseAdmin(admin.ModelAdmin):

    list_display = (
        'donor_name',
        'donor_blood_group',
        'hospital_name',
        'request_blood_group',
        'status',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'status',
        'blood_request__urgency',
        'blood_request__district',
        'created_at',
    )

    search_fields = (
        'donor__full_name',
        'blood_request__hospital_name',
        'blood_request__reference_code',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    list_editable = ('status',)

    list_per_page = 25

    @admin.display(description='Donor')
    def donor_name(self, obj):
        return obj.donor.full_name

    @admin.display(description='Donor Blood Group')
    def donor_blood_group(self, obj):
        return obj.donor.blood_group

    @admin.display(description='Hospital')
    def hospital_name(self, obj):
        return obj.blood_request.hospital_name

    @admin.display(description='Required Blood Group')
    def request_blood_group(self, obj):
        return obj.blood_request.blood_group

    def save_model(self, request, obj, form, change):

        old_status = None

        if change:
            old_status = DonorResponse.objects.filter(
                pk=obj.pk
            ).values_list('status', flat=True).first()

        super().save_model(request, obj, form, change)

        if change and old_status != obj.status:
            DonorNotification.objects.create(
                donor=obj.donor,
                title='Emergency Response Status Updated',
                message=(
                    f'Your response for the blood request at '
                    f'{obj.blood_request.hospital_name} has been updated '
                    f'to: {obj.get_status_display()}.'
                ),
                notification_type='EMERGENCY'
            )
