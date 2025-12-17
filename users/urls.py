from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from . import views
from .views import PasswordResetConfirmView

urlpatterns = [
    # Redirect root to login
    path('', RedirectView.as_view(pattern_name='login', permanent=False)),

    # Login / Logout
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # Password change URLs
    path('password-change/', views.UserPasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', views.UserPasswordChangeDoneView.as_view(), name='password_change_done'),

    # ----------------------
    # Password reset workflow
    # ----------------------
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset.html'
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),

    # ----------------------
    # Admin URLs
    # ----------------------
    path('adminn/dashboard/', views.adminn_dashboard, name='adminn_dashboard'),
    path('adminn/add-user/', views.add_user, name='add_user'),
    path('adminn/view-users/', views.view_users, name='view_users'),
    path('adminn/user-details/<int:user_id>/', views.user_details, name='user_details'),
    path('adminn/edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('adminn/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('adminn/add-technician/', views.add_technician, name='add_technician'),
    path('adminn/staff-list/', views.staff_list, name='staff_list'),
    path('adminn/department_list/', views.department_list, name='department_list'),
    path('adminn/in-progress-requests/', views.in_progress_requests, name='in_progress_requests'),
    path('adminn/service-categories/', views.service_category, name='service_category'),
    path('adminn/priority-list/', views.priority_list, name='priority_list'),
    path('adminn/support-departments/', views.support_department_list, name='support_department_list'),

    # ----------------------
    # Staff URLs
    # ----------------------
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('profile/', views.view_profile, name='view_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('submit-request/', views.submit_request, name='submit_request'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('notifications/', views.notifications, name='notifications'),
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('faqs/', views.faqs, name='faqs'),
]
