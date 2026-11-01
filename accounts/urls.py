
from django.urls import path
from . import views

urlpatterns = [
    path(
        'organization/apply/',
        views.organization_apply,
        name='organization_apply'
    ),
    path(
        'organization/create-account/<uuid:token>/',
        views.organization_create_account,
        name='organization_create_account'
    ),
    path(
        'organization/login/',
        views.organization_login,
        name='organization_login'
    ),
    path(
        'organization/dashboard/',
        views.organization_dashboard,
        name='organization_dashboard'
    ),
    path(
        'organization/logout/',
        views.organization_logout,
        name='organization_logout'
    ),
]
