
from django.contrib import admin
from .models import DonorProfile, DonationRecord, DonorNotification


@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'blood_group',
        'district',
        'mobile_number',
        'availability',
        'emergency_willingness',
        'created_at',
    )

    list_filter = (
        'blood_group',
        'district',
        'availability',
        'emergency_willingness',
    )

    search_fields = (
        'full_name',
        'email',
        'mobile_number',
        'city',
        'district',
    )

    readonly_fields = ('created_at',)




@admin.register(DonationRecord)
class DonationRecordAdmin(admin.ModelAdmin):
    list_display = (
        'donor',
        'donation_date',
        'hospital_name',
        'city',
        'units_donated',
        'is_verified',
    )
    list_filter = ('is_verified', 'donation_date')
    search_fields = ('donor__full_name', 'hospital_name', 'city')


@admin.register(DonorNotification)
class DonorNotificationAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'donor',
        'notification_type',
        'is_read',
        'created_at',
    )
    list_filter = ('notification_type', 'is_read')
    search_fields = ('title', 'donor__full_name')

