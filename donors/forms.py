
from datetime import date
from django import forms
from .models import DonorProfile


class DonorRegistrationForm(forms.ModelForm):

    class Meta:
        model = DonorProfile
        exclude = ['user', 'created_at']
        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'last_donation_date': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'address': forms.Textarea(
                attrs={'rows': 3}
            ),
        }

    def clean_date_of_birth(self):
        dob = self.cleaned_data['date_of_birth']

        if dob >= date.today():
            raise forms.ValidationError(
                'Please enter a valid date of birth.'
            )

        age = (
            date.today().year - dob.year
            - ((date.today().month, date.today().day)
               < (dob.month, dob.day))
        )

        if age < 18:
            raise forms.ValidationError(
                'You must be at least 18 years old to register as a donor.'
            )

        return dob

    def clean_last_donation_date(self):
        donation_date = self.cleaned_data.get('last_donation_date')

        if donation_date and donation_date > date.today():
            raise forms.ValidationError(
                'Last donation date cannot be in the future.'
            )

        return donation_date

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('information_consent'):
            self.add_error(
                'information_consent',
                'Please confirm that your information is accurate.'
            )

        if not cleaned_data.get('contact_consent'):
            self.add_error(
                'contact_consent',
                'Please provide consent for donation-related contact.'
            )

        return cleaned_data



class DonorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = DonorProfile
        fields = [
            'full_name',
            'date_of_birth',
            'gender',
            'profile_photo',
            'email',
            'mobile_number',
            'alternate_number',
            'state',
            'district',
            'city',
            'address',
            'pin_code',
            'blood_group',
            'last_donation_date',
            'preferred_time',
            'emergency_willingness',
        ]

        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'last_donation_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_date_of_birth(self):
        dob = self.cleaned_data['date_of_birth']

        if dob >= date.today():
            raise forms.ValidationError(
                'Please enter a valid date of birth.'
            )

        age = (
            date.today().year - dob.year
            - (
                (date.today().month, date.today().day)
                < (dob.month, dob.day)
            )
        )

        if age < 18:
            raise forms.ValidationError(
                'Donor must be at least 18 years old.'
            )

        return dob

    def clean_last_donation_date(self):
        donation_date = self.cleaned_data.get('last_donation_date')

        if donation_date and donation_date > date.today():
            raise forms.ValidationError(
                'Last donation date cannot be in the future.'
            )

        return donation_date
