from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_blood_request, name='submit_blood_request'),
    path('success/', views.blood_request_success, name='blood_request_success'),
    path('verified/', views.verified_blood_requests, name='verified_blood_requests'),

    path(
        'emergency/<uuid:reference_code>/nearby-donors/',
        views.nearby_donors,
        name='nearby_donors'
    ),

    path(
        'emergency/<uuid:reference_code>/respond/',
        views.donor_willingness_response,
        name='donor_willingness_response'
    ),

    path('track/', views.track_blood_request, name='track_blood_request'),
]