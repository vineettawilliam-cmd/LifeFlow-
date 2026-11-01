
from django.conf import settings
from django.db import models
from datetime import date


class DonorProfile(models.Model):

    BLOOD_GROUPS = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
        ('PREFER_NOT_TO_SAY', 'Prefer not to say'),
    ]

    AVAILABILITY_CHOICES = [
        ('YES', 'Available'),
        ('NO', 'Not Available'),
    ]

    PREFERRED_TIME_CHOICES = [
        ('MORNING', 'Morning'),
        ('AFTERNOON', 'Afternoon'),
        ('EVENING', 'Evening'),
        ('ANYTIME', 'Anytime'),
    ]

    # Connected after the donor creates an account
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donor_profile'
    )

    # Personal details
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=25, choices=GENDER_CHOICES)
    profile_photo = models.ImageField(
        upload_to='donor_profiles/',
        blank=True,
        null=True
    )

    # Contact details
    email = models.EmailField()
    mobile_number = models.CharField(max_length=15)
    alternate_number = models.CharField(max_length=15, blank=True)

    # Address
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    pin_code = models.CharField(max_length=10)

    # Blood information
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    last_donation_date = models.DateField(null=True, blank=True)

    # Availability and preferences
    availability = models.CharField(
        max_length=3,
        choices=AVAILABILITY_CHOICES,
        default='YES'
    )

    preferred_time = models.CharField(
        max_length=10,
        choices=PREFERRED_TIME_CHOICES,
        default='ANYTIME'
    )

    emergency_willingness = models.BooleanField(default=False)

    # Consent
    information_consent = models.BooleanField(default=False)
    contact_consent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def age(self):
        today = date.today()
        return (
            today.year - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )

    def __str__(self):
        return f"{self.full_name} ({self.blood_group})"




class DonationRecord(models.Model):
    donor = models.ForeignKey(
        DonorProfile,
        on_delete=models.CASCADE,
        related_name='donations'
    )
    donation_date = models.DateField()
    hospital_name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    units_donated = models.PositiveSmallIntegerField(default=1)
    notes = models.TextField(blank=True)

    # Only admin-verified donations count as completed.
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-donation_date']

    def __str__(self):
        return f"{self.donor.full_name} - {self.donation_date}"


class DonorNotification(models.Model):
    donor = models.ForeignKey(
        DonorProfile,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=30,
        default='GENERAL'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
