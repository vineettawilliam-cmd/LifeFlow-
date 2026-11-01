
from django.shortcuts import render, redirect
from .forms import DonorRegistrationForm

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.auth import get_user_model, login
from accounts.forms import DonorAccountForm
from .models import DonorProfile

User = get_user_model()

from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from .forms import DonorProfileUpdateForm
from .models import DonationRecord, DonorNotification
from ml_model.predict_service import get_donor_ai_insight

def donor_awareness(request):
    if request.method == 'POST':
        read_awareness = request.POST.get('read_awareness')
        understand_eligibility = request.POST.get(
            'understand_eligibility'
        )

        if read_awareness and understand_eligibility:
            request.session['donor_awareness_accepted'] = True
            return redirect('donor_details')

        return render(request, 'donors/awareness.html', {
            'error': 'Please accept both declarations before continuing.'
        })

    return render(request, 'donors/awareness.html')


def donor_details(request):

    if not request.session.get('donor_awareness_accepted'):
        return redirect('donor_awareness')

    if request.method == 'POST':
        form = DonorRegistrationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            donor = form.save()
            request.session['pending_donor_id'] = donor.id
            request.session.pop('donor_awareness_accepted', None)

            return redirect('donor_registration_success')

    else:
        form = DonorRegistrationForm()

    return render(request, 'donors/donor_details.html', {
        'form': form
    })


def donor_registration_success(request):
    donor_id = request.session.get('pending_donor_id')

    if not donor_id:
        return redirect('donor_awareness')

    return redirect('donor_create_account')


def donor_create_account(request):
    donor_id = request.session.get('pending_donor_id')

    if not donor_id:
        return redirect('donor_awareness')

    try:
        donor = DonorProfile.objects.get(id=donor_id)
    except DonorProfile.DoesNotExist:
        request.session.pop('pending_donor_id', None)
        return redirect('donor_awareness')

    if donor.user:
        return redirect('donor_login')

    if request.method == 'POST':
        form = DonorAccountForm(request.POST)

        if form.is_valid():

            # Check for an existing email
            if User.objects.filter(email__iexact=donor.email).exists():
                messages.error(
                    request,
                    "This email is already registered. "
                    "Please contact the admin to resolve the existing account."
                )

                return render(
                    request,
                    'accounts/create_account.html',
                    {'form': form, 'donor': donor}
                )

            # Check for an existing username
            if User.objects.filter(
                username__iexact=form.cleaned_data['username']
            ).exists():
                form.add_error(
                    'username',
                    'This username is already taken. Please choose another.'
                )

            else:
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                    email=donor.email,
                    phone=donor.mobile_number,
                    role='DONOR',
                    is_approved=True
                )

                donor.user = user
                donor.save(update_fields=['user'])

                request.session.pop('pending_donor_id', None)

                login(request, user)

                return redirect('donor_dashboard')

    else:
        form = DonorAccountForm()

    return render(
        request,
        'accounts/create_account.html',
        {
            'form': form,
            'donor': donor
        }
    )

    donor_id = request.session.get('pending_donor_id')

    if not donor_id:
        return redirect('donor_awareness')

    try:
        donor = DonorProfile.objects.get(id=donor_id)
    except DonorProfile.DoesNotExist:
        return redirect('donor_awareness')

    if donor.user:
        return redirect('donor_login')

    if request.method == 'POST':
        form = DonorAccountForm(request.POST)

        if form.is_valid():

            # Check whether this email is already registered
            if User.objects.filter(email__iexact=donor.email).exists():
                messages.error(
                    request,
                    "This email is already registered with another account. "
                    "Please log in using your existing account or contact the admin."
                 )

                return render(request, 'accounts/create_account.html', {
                    'form': form,
                    'donor': donor
                })

            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=donor.email,
                phone=donor.mobile_number,
                role='DONOR',
                is_approved=True
            )

            donor.user = user
            donor.save(update_fields=['user'])

            request.session.pop('pending_donor_id', None)

            login(request, user)

            return redirect('donor_dashboard')
        else:
                form = DonorAccountForm()

                return render(request, 'accounts/create_account.html', {
                'form': form,
                'donor': donor
            })


def donor_login_view(request):
    if request.user.is_authenticated and request.user.role == 'DONOR':
        return redirect('donor_dashboard')

    # Clear old registration/application messages on login page GET
    if request.method == 'GET':
        list(messages.get_messages(request))

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.role == 'DONOR':
            if user.is_approved:
                login(request, user)
                return redirect('donor_dashboard')

            messages.warning(
                request,
                'Your donor account is awaiting admin approval.'
            )
        else:
            messages.error(
                request,
                'Invalid username or password. Please try again.'
            )

    return render(request, 'accounts/donor_login.html')




@login_required
def donor_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('donor_login')

    return redirect('donor_dashboard')


@login_required
def donor_dashboard(request):
    if request.user.role != 'DONOR':
        return redirect('home')

    donor = get_object_or_404(
        DonorProfile,
        user=request.user
    )

    verified_donations = DonationRecord.objects.filter(
        donor=donor,
        is_verified=True
    )
    # Generate experimental AI donor insight
    try:
        ai_insight = get_donor_ai_insight(donor)

    except FileNotFoundError:
        ai_insight = {
            'available': False,
            'reason': 'AI model files are not available.'
        }

    except Exception:
        ai_insight = {
            'available': False,
            'reason': 'AI insight is temporarily unavailable.'
        }

    context = {
        'donor': donor,
        'total_donations': verified_donations.count(),
        'unread_notifications': DonorNotification.objects.filter(
            donor=donor,
            is_read=False
        ).count(),
        'recent_donations': verified_donations.order_by(
            '-donation_date'
        )[:5],
        'recent_notifications': DonorNotification.objects.filter(
            donor=donor
        )[:5],
        'ai_insight': ai_insight,
    }

    return render(request, 'donors/dashboard.html', context)



@login_required
def donor_profile(request):
    if request.user.role != 'DONOR':
        return redirect('home')

    donor = get_object_or_404(
        DonorProfile,
        user=request.user
    )

    return render(request, 'donors/profile.html', {
        'donor': donor
    })


@login_required
def donor_edit_profile(request):
    if request.user.role != 'DONOR':
        return redirect('home')

    donor = get_object_or_404(
        DonorProfile,
        user=request.user
    )

    if request.method == 'POST':
        form = DonorProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=donor
        )

        if form.is_valid():
            updated_donor = form.save()

            # Keep account contact details synchronized.
            request.user.email = updated_donor.email
            request.user.phone = updated_donor.mobile_number
            request.user.save(update_fields=['email', 'phone'])

            messages.success(request, 'Profile updated successfully!')
            return redirect('donor_profile')

    else:
        form = DonorProfileUpdateForm(instance=donor)

    return render(request, 'donors/edit_profile.html', {
        'form': form,
        'donor': donor
    })


@login_required
@require_POST
def donor_update_availability(request):
    if request.user.role != 'DONOR':
        return redirect('home')

    donor = get_object_or_404(
        DonorProfile,
        user=request.user
    )

    new_status = request.POST.get('availability')

    if new_status in ['YES', 'NO']:
        donor.availability = new_status
        donor.save(update_fields=['availability'])
        messages.success(request, 'Availability updated successfully!')
    else:
        messages.error(request, 'Invalid availability selection.')

    return redirect('donor_dashboard')



@login_required
def donation_history(request):
    if request.user.role != 'DONOR':
        return redirect('home')

    donor = get_object_or_404(DonorProfile, user=request.user)

    donations = DonationRecord.objects.filter(
        donor=donor,
        is_verified=True
    ).order_by('-donation_date')

    return render(request, 'donors/donation_history.html', {
        'donor': donor,
        'donations': donations,
    })


@login_required
def donation_certificate(request, donation_id):
    if request.user.role != 'DONOR':
        return redirect('home')

    donor = get_object_or_404(DonorProfile, user=request.user)

    donation = get_object_or_404(
        DonationRecord,
        id=donation_id,
        donor=donor,
        is_verified=True
    )

    return render(request, 'donors/donation_certificate.html', {
        'donor': donor,
        'donation': donation,
    })



@login_required
def donor_notifications(request):
    if request.user.role != 'DONOR':
        return redirect('home')

    donor = get_object_or_404(DonorProfile, user=request.user)

    notifications = DonorNotification.objects.filter(
        donor=donor
    ).order_by('-created_at')

    return render(request, 'donors/notifications.html', {
        'donor': donor,
        'notifications': notifications,
    })


@login_required
@require_POST
def mark_all_notifications_read(request):
    if request.user.role != 'DONOR':
        return redirect('home')

    donor = get_object_or_404(DonorProfile, user=request.user)

    DonorNotification.objects.filter(
        donor=donor,
        is_read=False
    ).update(is_read=True)

    messages.success(request, 'All notifications marked as read.')
    return redirect('donor_notifications')
