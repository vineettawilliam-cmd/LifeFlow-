
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import OrganizationApplication
from .forms import OrganizationApplicationForm, OrganizationAccountForm

User = get_user_model()


def organization_apply(request):
    if request.method == 'POST':
        form = OrganizationApplicationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            application = form.save()

            messages.success(
                request,
                'Your application has been submitted successfully. '
                'Please wait for admin verification.'
            )

            return render(
                request,
                'accounts/organization_application_success.html',
                {'application': application}
            )
    else:
        form = OrganizationApplicationForm()

    return render(request, 'accounts/organization_apply.html', {
        'form': form
    })


def organization_create_account(request, token):
    application = get_object_or_404(
        OrganizationApplication,
        setup_token=token
    )

    if application.status != 'APPROVED':
        messages.error(
            request,
            'Your application must be approved before creating an account.'
        )
        return redirect('home')

    if application.account:
        messages.info(request, 'An account already exists for this application.')
        return redirect('organization_login')

    if request.method == 'POST':
        form = OrganizationAccountForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                email=application.email,
                phone=application.phone,
                role='ORGANIZATION',
                is_approved=True
            )

            application.account = user
            application.save(update_fields=['account'])

            login(request, user)

            messages.success(
                request,
                'Your organization account has been created successfully.'
            )

            return redirect('organization_dashboard')
    else:
        form = OrganizationAccountForm()

    return render(request, 'accounts/organization_create_account.html', {
        'form': form,
        'application': application
    })


def organization_login(request):
    if request.user.is_authenticated:
        if request.user.role == 'ORGANIZATION':
            return redirect('organization_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if (
            user is not None
            and user.role == 'ORGANIZATION'
            and user.is_approved
        ):
            login(request, user)
            return redirect('organization_dashboard')

        messages.error(
            request,
            'Invalid organization username or password.'
        )

    return render(request, 'accounts/organization_login.html')


@login_required
def organization_dashboard(request):
    if (
        request.user.role != 'ORGANIZATION'
        or not request.user.is_approved
    ):
        return redirect('home')

    application = get_object_or_404(
        OrganizationApplication,
        account=request.user
    )

    return render(request, 'accounts/organization_dashboard.html', {
        'application': application
    })


@login_required
@require_POST
def organization_logout(request):
    if request.user.role != 'ORGANIZATION':
        return redirect('home')

    logout(request)
    return redirect('organization_login')
