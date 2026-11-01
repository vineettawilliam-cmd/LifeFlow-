
from django import forms
from django.utils import timezone
from .models import BloodRequest


class BloodRequestForm(forms.ModelForm):

    class Meta:
        model = BloodRequest

        fields = [
            'request_type',
            'patient_name',
            'patient_age',
            'patient_gender',
            'blood_group',
            'units_required',
            'component',
            'urgency',
            'required_by',
            'reason',
            'hospital_name',
            'state',
            'district',
            'city',
            'hospital_address',
            'ward',
            'doctor_contact',
            'bystander_name',
            'bystander_contact',
            'alternate_contact',
            'relationship',
            'information_confirmed',
            'contact_consent',
        ]

        widgets = {
            'required_by': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            ),
            'reason': forms.Textarea(attrs={'rows': 3}),
            'hospital_address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_patient_age(self):
        age = self.cleaned_data.get('patient_age')

        if age is not None and (age < 0 or age > 120):
            raise forms.ValidationError(
                'Please enter a valid patient age between 0 and 120.'
            )

        return age

    def clean_units_required(self):
        units = self.cleaned_data.get('units_required')

        if units is not None and (units < 1 or units > 100):
            raise forms.ValidationError(
                'Please enter units between 1 and 100.'
            )

        return units

    def clean_required_by(self):
        required_by = self.cleaned_data.get('required_by')

        if required_by and timezone.is_naive(required_by):
            required_by = timezone.make_aware(required_by)

        if required_by and required_by < timezone.now():
            raise forms.ValidationError(
                'Required date and time cannot be in the past.'
            )

        return required_by

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('information_confirmed'):
            self.add_error(
                'information_confirmed',
                'Please confirm that the information is correct.'
            )

        if not cleaned_data.get('contact_consent'):
            self.add_error(
                'contact_consent',
                'Please provide consent for request-related contact.'
            )

        return cleaned_data
