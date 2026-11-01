from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path(
        'ml-analytics/',
        views.ml_analytics,
        name='ml_analytics'
    ),
]