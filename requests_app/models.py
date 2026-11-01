
import uuid

from django.conf import settings
from django.db import models


class BloodRequest(models.Model):

    REQUEST_TYPES = [
        ('NORMAL', 'Normal'),
        ('EMERGENCY', 'Emergency'),
    ]

    BLOOD_GROUPS = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('UNKNOWN', 'Unknown'),
    ]

    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
        ('UNKNOWN', 'Unknown'),
    ]

    COMPONENT_CHOICES = [
        ('WHOLE_BLOOD', 'Whole Blood'),
        ('PRBC', 'Packed Red Blood Cells'),
        ('PLATELETS', 'Platelets'),
        ('PLASMA', 'Plasma'),
        ('CRYOPRECIPITATE', 'Cryoprecipitate'),
    ]

    URGENCY_CHOICES = [
        ('NORMAL', 'Normal'),
        ('URGENT', 'Urgent'),
        ('CRITICAL', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Verification'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
        ('COMPLETION_REVIEW', 'Completion Review'),
        ('COMPLETED', 'Completed'),
    ]

    # Unique reference for every blood request
    reference_code = models.UUIDField(
        default=uuid.uuid4,
        editable=False
    )

    # Login is optional for public blood requests
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blood_requests'
    )

    request_type = models.CharField(
        max_length=15,
        choices=REQUEST_TYPES,
        default='NORMAL'
    )

    patient_name = models.CharField(max_length=150)
    patient_age = models.PositiveSmallIntegerField(null=True, blank=True)
    patient_gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='UNKNOWN'
    )

    blood_group = models.CharField(
        max_length=7,
        choices=BLOOD_GROUPS
    )

    units_required = models.PositiveSmallIntegerField(default=1)

    component = models.CharField(
        max_length=20,
        choices=COMPONENT_CHOICES,
        default='WHOLE_BLOOD'
    )

    urgency = models.CharField(
        max_length=15,
        choices=URGENCY_CHOICES,
        default='NORMAL'
    )

    required_by = models.DateTimeField(null=True, blank=True)
    reason = models.TextField()

    hospital_name = models.CharField(max_length=200)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    hospital_address = models.TextField()
    ward = models.CharField(max_length=100, blank=True)
    doctor_contact = models.CharField(max_length=15, blank=True)

    bystander_name = models.CharField(max_length=150)
    bystander_contact = models.CharField(max_length=15)
    alternate_contact = models.CharField(max_length=15, blank=True)
    relationship = models.CharField(max_length=100, blank=True)

    information_confirmed = models.BooleanField(default=False)
    contact_consent = models.BooleanField(default=False)

    status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    admin_remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.request_type} - {self.blood_group} - {self.hospital_name}"


class DonorResponse(models.Model):
    RESPONSE_STATUS = [
        ('WILLING', 'Willing to Donate'),
        ('CONTACTED', 'Donor Contacted'),
        ('DECLINED', 'Declined'),
        ('COMPLETED', 'Donation Completed'),
    ]

    blood_request = models.ForeignKey(
        BloodRequest,
        on_delete=models.CASCADE,
        related_name='donor_responses'
    )

    donor = models.ForeignKey(
        'donors.DonorProfile',
        on_delete=models.CASCADE,
        related_name='emergency_responses'
    )

    status = models.CharField(
        max_length=15,
        choices=RESPONSE_STATUS,
        default='WILLING'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['blood_request', 'donor'],
                name='unique_donor_response_per_request'
            )
        ]

    def __str__(self):
        return f'{self.donor.full_name} - {self.blood_request.reference_code}'