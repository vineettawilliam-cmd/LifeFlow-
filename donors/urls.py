
from django.urls import path
from . import views

urlpatterns = [
    path(
        'register/awareness/',
        views.donor_awareness,
        name='donor_awareness'
    ),
    path(
        'register/details/',
        views.donor_details,
        name='donor_details'
    ),
    path(
        'register/success/',
        views.donor_registration_success,
        name='donor_registration_success'
    ),
    path(
        'create-account/',
        views.donor_create_account,
        name='donor_create_account'
    ),

    path('login/', views.donor_login_view, name='donor_login'),
    path('dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('logout/', views.donor_logout, name='donor_logout'),
    path('profile/', views.donor_profile, name='donor_profile'),
    path('profile/edit/', views.donor_edit_profile, name='donor_edit_profile'),
    path(
        'availability/update/',
        views.donor_update_availability,
        name='donor_update_availability'
    ),
    
    path('donation-history/', views.donation_history, name='donation_history'),
    path(
        'donation-certificate/<int:donation_id>/',
        views.donation_certificate,
        name='donation_certificate'
    ),
    
    path('notifications/', views.donor_notifications, name='donor_notifications'),
    path(
        'notifications/mark-read/',
        views.mark_all_notifications_read,
        name='mark_all_notifications_read'
    ),


]
