"""
Root URL Configuration for HealthSense AI Backend.
"""

from django.urls import path, include

urlpatterns = [
    path('api/', include('api.urls')),
]
