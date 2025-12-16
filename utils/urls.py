from django.urls import path
from . import views


urlpatterns = [
    path('reports/requests/', views.request_reports, name='request_reports'),
    path('reports/requests/print/', views.request_reports_print, name='request_reports_print'),
]