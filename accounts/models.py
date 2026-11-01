
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    ROLE_CHOICES = [
        ('DONOR', 'Donor'),
        ('REQUESTER', 'Blood Requester'),
        ('ORGANIZATION', 'Hospital / Organization'),
        ('ADMIN', 'Admin'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='REQUESTER'
    )

    email = models.EmailField(unique=True)

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.role}"



import uuid


class OrganizationApplication(models.Model):

    ORGANIZATION_TYPES = [
        ('HOSPITAL', 'Hospital'),
        ('BLOOD_BANK', 'Blood Bank'),
        ('NGO', 'NGO'),
        ('CAMP_ORGANIZER', 'Camp Organizer'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('MORE_INFO', 'More Information Required'),
    ]

    organization_name = models.CharField(max_length=200)
    organization_type = models.CharField(
        max_length=30,
        choices=ORGANIZATION_TYPES
    )

    registration_number = models.CharField(
        max_length=100,
        blank=True
    )

    email = models.EmailField()
    phone = models.CharField(max_length=15)

    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    pin_code = models.CharField(max_length=10, blank=True)

    representative_name = models.CharField(max_length=150)
    representative_designation = models.CharField(max_length=100)
    representative_phone = models.CharField(max_length=15)
    representative_email = models.EmailField()

    request_blood_permission = models.BooleanField(default=False)
    submit_camp_permission = models.BooleanField(default=False)

    supporting_document = models.FileField(
        upload_to='organization_documents/',
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    admin_remarks = models.TextField(blank=True)

    setup_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    account = models.OneToOneField(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organization_application'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.organization_name} - {self.get_status_display()}'
