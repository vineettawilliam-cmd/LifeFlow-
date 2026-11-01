from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .forms import BloodRequestForm
from .models import BloodRequest, DonorResponse
from donors.models import DonorProfile


def submit_blood_request(request):

    if request.user.is_authenticated:
        if (
            request.user.role == 'ORGANIZATION'
            and not request.user.is_approved
        ):
            messages.error(
                request,
                'Your organization account is awaiting admin approval.'
            )
            return redirect('home')

    if request.method == 'POST':
        form = BloodRequestForm(request.POST)

        if form.is_valid():
            blood_request = form.save(commit=False)

            if request.user.is_authenticated:
                blood_request.requester = request.user

            blood_request.status = 'PENDING'
            blood_request.save()

            request.session['last_blood_request_reference'] = str(
                blood_request.reference_code
            )

            return redirect('blood_request_success')

    else:
        form = BloodRequestForm()

    return render(
        request,
        'requests_app/submit_request.html',
        {'form': form}
    )


def blood_request_success(request):

    reference_code = request.session.pop(
        'last_blood_request_reference',
        None
    )

    if not reference_code:
        return redirect('home')

    return render(
        request,
        'requests_app/request_success.html',
        {'reference_code': reference_code}
    )


def verified_blood_requests(request):

    blood_requests = BloodRequest.objects.filter(
        status='VERIFIED'
    ).order_by('-created_at')

    return render(
        request,
        'requests_app/verified_requests.html',
        {'blood_requests': blood_requests}
    )


def nearby_donors(request, reference_code):

    blood_request = get_object_or_404(
        BloodRequest,
        reference_code=reference_code,
        request_type='EMERGENCY',
        status='VERIFIED'
    )

    donors = DonorProfile.objects.filter(
        blood_group=blood_request.blood_group,
        availability='YES',
        emergency_willingness=True,
        contact_consent=True
    )

    donors = list(donors)

    donors.sort(
        key=lambda donor: (
            0 if donor.city.strip().lower() == blood_request.city.strip().lower()
            else 1 if donor.district.strip().lower() == blood_request.district.strip().lower()
            else 2,
            donor.full_name.lower()
        )
    )

    current_donor = None
    has_responded = False

    if request.user.is_authenticated and request.user.role == 'DONOR':
        try:
            current_donor = request.user.donor_profile
        except DonorProfile.DoesNotExist:
            current_donor = None

    if current_donor:
        has_responded = DonorResponse.objects.filter(
            blood_request=blood_request,
            donor=current_donor
        ).exists()

    return render(
        request,
        'requests_app/nearby_donors.html',
        {
            'blood_request': blood_request,
            'donors': donors,
            'current_donor': current_donor,
            'has_responded': has_responded,
        }
    )


@login_required
@require_POST
def donor_willingness_response(request, reference_code):

    if request.user.role != 'DONOR':
        messages.error(
            request,
            'Only registered donors can respond to emergency requests.'
        )
        return redirect('nearby_donors', reference_code=reference_code)

    blood_request = get_object_or_404(
        BloodRequest,
        reference_code=reference_code,
        request_type='EMERGENCY',
        status='VERIFIED'
    )

    try:
        donor = request.user.donor_profile
    except DonorProfile.DoesNotExist:
        messages.error(
            request,
            'Your donor profile was not found.'
        )
        return redirect('nearby_donors', reference_code=reference_code)

    # Recheck donor eligibility on the server.
    eligible = DonorProfile.objects.filter(
        pk=donor.pk,
        blood_group=blood_request.blood_group,
        availability='YES',
        emergency_willingness=True,
        contact_consent=True
    ).exists()

    if not eligible:
        messages.error(
            request,
            'You are not currently eligible to respond to this request. '
            'Please check your blood group, availability and consent settings.'
        )
        return redirect('nearby_donors', reference_code=reference_code)

    response, created = DonorResponse.objects.get_or_create(
        blood_request=blood_request,
        donor=donor
    )

    if created:
        messages.success(
            request,
            'Your willingness to donate has been recorded successfully.'
        )
    else:
        messages.info(
            request,
            'You have already responded to this emergency request.'
        )

    return redirect('nearby_donors', reference_code=reference_code)


def track_blood_request(request):

    blood_request = None
    error = None

    if request.method == 'POST':
        reference_code = request.POST.get('reference_code', '').strip()
        mobile_number = request.POST.get('mobile_number', '').strip()

        if not reference_code or not mobile_number:
            error = 'Please enter both Reference ID and mobile number.'
        else:
            try:
                blood_request = BloodRequest.objects.get(
                    reference_code=reference_code,
                    bystander_contact=mobile_number
                )
            except (BloodRequest.DoesNotExist, ValueError):
                error = (
                    'No matching request found. Check your Reference ID '
                    'and mobile number.'
                )

    return render(
        request,
        'requests_app/track_request.html',
        {
            'blood_request': blood_request,
            'error': error,
        }
    )