
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import OrganizationApplication
User = get_user_model()


class DonorAccountForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(
        widget=forms.PasswordInput,
        validators=[validate_password]
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')

        if password and confirm and password != confirm:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data





class OrganizationApplicationForm(forms.ModelForm):

    declaration = forms.BooleanField(
        required=True,
        label='I confirm that the information provided is correct.'
    )

    class Meta:
        model = OrganizationApplication
        fields = [
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
            'representative_name',
            'representative_designation',
            'representative_phone',
            'representative_email',
            'request_blood_permission',
            'submit_camp_permission',
            'supporting_document',
        ]

        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class OrganizationAccountForm(forms.Form):

    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username'].strip()

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already taken.')

        return username

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password:
            validate_password(password)

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

        return cleaned_data
