from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ('LifeFlow Information', {
            'fields': (
                'role',
                'phone',
                'is_approved',
            )
        }),
    )

    list_display = (
        'username',
        'email',
        'role',
        'is_approved',
        'is_staff',
    )



from .models import OrganizationApplication

@admin.register(OrganizationApplication)
class OrganizationApplicationAdmin(admin.ModelAdmin):

    list_display = (
        'organization_name',
        'organization_type',
        'email',
        'district',
        'status',
        'created_at',
    )

    list_filter = (
        'organization_type',
        'status',
        'district',
        'created_at',
    )

    search_fields = (
        'organization_name',
        'email',
        'phone',
        'representative_name',
        'representative_email',
    )

    readonly_fields = (
        'setup_token',
        'created_at',
        'updated_at',
        'account',
    )

    # Admin approval and rejection actions
    actions = [
        'approve_applications',
        'reject_applications',
    ]

    fieldsets = (
        ('Organization Details', {
            'fields': (
                'organization_name',
                'organization_type',
                'registration_number',
                'email',
                'phone',
                'state',
                'district',
                'city',
                'address',
                'pin_code',
                'supporting_document',
            )
        }),

        ('Representative Details', {
            'fields': (
                'representative_name',
                'representative_designation',
                'representative_phone',
                'representative_email',
            )
        }),

        ('Requested Permissions', {
            'fields': (
                'request_blood_permission',
                'submit_camp_permission',
            )
        }),

        ('Admin Review', {
            'fields': (
                'status',
                'admin_remarks',
                'setup_token',
                'account',
                'created_at',
                'updated_at',
            )
        }),
    )

    # APPROVE APPLICATIONS
    @admin.action(description='Approve selected organizations')
    def approve_applications(self, request, queryset):

        updated = queryset.filter(
            status='PENDING'
        ).update(
            status='APPROVED'
        )

        self.message_user(
            request,
            f'{updated} organization application(s) approved successfully.'
        )

    # REJECT APPLICATIONS
    @admin.action(description='Reject selected organizations')
    def reject_applications(self, request, queryset):

        updated = queryset.filter(
            status='PENDING'
        ).update(
            status='REJECTED'
        )

        self.message_user(
            request,
            f'{updated} organization application(s) rejected successfully.'
        )