from django.urls import path
from . import views

urlpatterns = [
    # Staff URLs
    path('submit/', views.submit_request_view, name='submit_request'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('requests/<int:pk>/view/', views.request_details, name='request_details'),
    path('requests/<int:pk>/edit/', views.edit_request, name='edit_request'),
    path('requests/<int:pk>/delete/', views.delete_request, name='delete_request'),
    path('requests/<int:pk>/confirm/', views.confirm_completion, name='confirm_completion'),

    # Admin URLs
    path('all-requests/', views.all_requests, name='all_requests'),
    path('adminn/request/<int:request_id>/', views.admin_request_details, name='admin_request_details'),
    path('assign_technician/<int:request_id>/', views.assign_technician, name='assign_technician'),
    path('completed_requests/', views.completed_requests, name='completed_requests'),
    path('in_progress_requests/', views.in_progress_requests, name='in_progress_requests'),
    path('pending_requests/', views.pending_requests, name='pending_requests'),
    path('technicians/', views.technician_list, name='technician_list'),
    path('technician/<int:pk>/', views.technician_detail, name='technician_detail'),

    # Technician URLs
    path('technician/dashboard/', views.technician_dashboard, name='technician_dashboard'),
    path('technician/assigned-requests/', views.technician_assigned_requests, name='technician_assigned_requests'),
    path('technician/request/<int:request_id>/', views.technician_request_detail, name='technician_request_detail'),
    path('requests/<int:request_id>/start/', views.technician_start_request, name='technician_start_request'),

    path('technician/in-progress/', views.technician_in_progress, name='technician_in_progress'),
    path('technician/completed-requests/', views.technician_completed_requests, name='technician_completed_requests'),
    path('technician/complete/<int:pk>/', views.mark_request_complete, name='mark_request_complete'),

    path('technician/profile/', views.technician_profile, name='technician_profile'),
    path('technician/tech-edit-profile/', views.technician_edit_profile, name='technician_edit_profile'),
    path('technician/notifications/', views.technician_notifications, name='technician_notifications'),
    path('technician/accepted-requests/', views.technician_accepted_requests, name='technician_accepted_requests'),
    path('technician/rejected-requests/', views.technician_rejected_requests, name='technician_rejected_requests'),
    
    path('technician/request/<int:request_id>/accept/', views.technician_accept_request, name='technician_accept_request'),
    path('technician/request/<int:request_id>/reject/', views.technician_reject_request, name='technician_reject_request'),
    path('technician/awaiting-confirmation/', views.technician_awaiting_confirmation, name='technician_awaiting_confirmation'),
    
    # Manager URLs
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
]
