"""
API URL Routing for HealthSense AI.
"""

from django.urls import path
from .views import HealthCheckView, AnalyzeFoodView
from .views_v2 import AnalyzeFoodViewV2

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('analyze/', AnalyzeFoodView.as_view(), name='analyze_food'),
    path('v1/recommend/', AnalyzeFoodView.as_view(), name='recommend_v1'),
    path('v2/recommend/', AnalyzeFoodViewV2.as_view(), name='recommend_v2'),
]
