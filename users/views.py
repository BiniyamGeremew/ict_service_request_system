from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,PasswordResetConfirmView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import CustomLoginForm, EditProfileForm, CustomUserCreationForm, TechnicianCreationForm
from service.models import TechnicianProfile
from users.decorators import group_required 
from service.models import ServiceCategory, ServiceRequest, PriorityLevel, SupportDepartment, TechnicianProfile
from .models import Notification
import json
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404


User = get_user_model()

class UserLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = CustomLoginForm

    def get_success_url(self):
        user = self.request.user
        if not user.is_authenticated:
            return reverse_lazy('login')
        if user.groups.filter(name='admin').exists():
            return reverse_lazy('adminn_dashboard')
        elif user.groups.filter(name='staff').exists():
            return reverse_lazy('staff_dashboard')
        elif user.groups.filter(name='technician').exists():
            return reverse_lazy('technician_dashboard')
        elif user.groups.filter(name='manager').exists():
            return reverse_lazy('manager_dashboard')
        else:
            return reverse_lazy('login')

class UserLogoutView(LogoutView):
    template_name = 'login.html'
    authentication_form = CustomLoginForm

@login_required
@group_required('staff')
def staff_dashboard(request):
    # --- Categories ---
    category_labels = list(ServiceCategory.objects.values_list('name', flat=True))
    category_counts = [ServiceRequest.objects.filter(category=c, created_by=request.user).count() for c in ServiceCategory.objects.all()]

    # --- Statuses ---
    status_labels = ['New', 'Assigned', 'Accepted', 'In Progress', 'Completed', 'Rejected']
    status_counts = [ServiceRequest.objects.filter(created_by=request.user, status=s).count() for s in status_labels]

    # --- Quick stats cards ---
    total_requests = ServiceRequest.objects.filter(created_by=request.user).count()
    pending_requests = ServiceRequest.objects.filter(created_by=request.user, status='New').count()
    completed_requests = ServiceRequest.objects.filter(created_by=request.user, status='Completed').count()
    rejected_requests = ServiceRequest.objects.filter(created_by=request.user, status='Rejected').count()

    # --- Latest requests table ---
    latest_requests = ServiceRequest.objects.filter(created_by=request.user).order_by('-created_at')[:5]

    context = {
        'page_title': 'Staff Dashboard',
        'category_labels_json': json.dumps(category_labels),
        'category_counts_json': json.dumps(category_counts),
        'status_labels_json': json.dumps(status_labels),
        'status_counts_json': json.dumps(status_counts),
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'completed_requests': completed_requests,
        'rejected_requests': rejected_requests,
        'latest_requests': latest_requests,
    }
    return render(request, 'staff/staff_dashboard.html', context)
    
@login_required
def view_profile(request):
    return render(request, 'staff/profile.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('view_profile')
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'staff/edit_profile.html', {'form': form})

@login_required
def submit_request(request):
    return render(request, 'staff/submit_request.html')

@login_required
def my_requests(request):
    return render(request, 'staff/my_requests.html')

@login_required
@group_required('staff')
def notifications(request):
    user_group = request.user.groups.first().name if request.user.groups.exists() else None

    if user_group:
        notifications = Notification.objects.filter(
            target_group=user_group
        ).order_by('-created_at')
    else:
        notifications = Notification.objects.none()

    context = {
        'notifications': notifications
    }
    return render(request, 'staff/notifications.html', context)

@login_required
def submit_feedback(request):
    return render(request, 'staff/feedback.html')

@login_required
def faqs(request):
    return render(request, 'staff/faqs.html')

# PASSWORD VIEWS
class UserPasswordChangeView(PasswordChangeView):
    template_name = 'staff/password_change_form.html'
    success_url = reverse_lazy('password_change_done')

class UserPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'staff/password_change_done.html'


# ADMIN VIEWS
def is_admin(user):
    return user.is_superuser or user.groups.filter(name='admin').exists()

@login_required
@group_required('admin')
def adminn_dashboard(request):
    # --- Users ---
    total_users = User.objects.count()
    total_technicians = User.objects.filter(groups__name='technician').count()
    total_staff = User.objects.filter(groups__name='staff').count()
    total_admins = User.objects.filter(groups__name='admin').count()

    # --- Service Requests ---
    total_requests = ServiceRequest.objects.count()
    pending_requests = ServiceRequest.objects.filter(status='New').count()
    in_progress_requests = ServiceRequest.objects.filter(status='In Progress').count()
    completed_requests = ServiceRequest.objects.filter(status='Completed').count()
    rejected_requests = ServiceRequest.objects.filter(status='Rejected').count()

    # --- Charts ---
    # Users by Role
    user_roles_labels = ['Admin', 'Staff', 'Technician']
    user_roles_counts = [total_admins, total_staff, total_technicians]

    # Requests by Category
    category_labels = list(ServiceCategory.objects.values_list('name', flat=True))
    category_counts = [ServiceRequest.objects.filter(category=c).count() for c in ServiceCategory.objects.all()]

    # Requests by Status
    status_labels = ['New', 'Assigned', 'Accepted', 'In Progress', 'Completed', 'Rejected']
    status_counts = [ServiceRequest.objects.filter(status=s).count() for s in status_labels]

    # Latest Requests
    latest_requests = ServiceRequest.objects.all().order_by('-created_at')[:5]

    context = {
        'total_users': total_users,
        'total_technicians': total_technicians,
        'total_staff': total_staff,
        'total_admins': total_admins,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'in_progress_requests': in_progress_requests,
        'completed_requests': completed_requests,
        'rejected_requests': rejected_requests,
        'user_roles_labels_json': json.dumps(user_roles_labels),
        'user_roles_counts_json': json.dumps(user_roles_counts),
        'category_labels_json': json.dumps(category_labels),
        'category_counts_json': json.dumps(category_counts),
        'status_labels_json': json.dumps(status_labels),
        'status_counts_json': json.dumps(status_counts),
        'latest_requests': latest_requests,
    }
    return render(request, 'adminn/adminn_dashboard.html', context)


@login_required
@group_required('admin')
def add_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            # Assign to group
            role = form.cleaned_data.get('role')
            if role:
                group = Group.objects.get(name=role)
                user.groups.add(group)
            messages.success(request, f"User '{user.username}' created successfully and added to '{role}' group.")
            return redirect('adminn_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'adminn/add_user.html', {'form': form})

@login_required
@group_required('admin')
def view_users(request):
    user_list = User.objects.all().select_related()
    paginator = Paginator(user_list, 5)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    return render(request, 'adminn/view_users.html', {'users': users})

@login_required
@group_required('admin')
def user_details(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'adminn/user_details.html', {'user': user})

@login_required
@group_required('admin')
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            # Update group
            role = form.cleaned_data.get('role')
            if role:
                group = Group.objects.get(name=role)
                user.groups.clear()
                user.groups.add(group)
            messages.success(request, f"User '{user.username}' updated successfully.")
            return redirect('all_users') 
        else:
            messages.error(request, "Error updating user.")
    else:
        form = CustomUserCreationForm(instance=user)

    return render(request, 'adminn/edit_user.html', {'form': form, 'user': user})

@login_required
@group_required('admin')
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.user == user:
        messages.error(request, "You cannot delete yourself!")
        return redirect('all_users')
    
    user.delete()
    messages.success(request, f"User '{user.username}' deleted successfully.")
    return redirect('all_users')

@login_required
@group_required('admin')
def add_technician(request):
    if request.method == "POST":
        form = TechnicianCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            # Assign to technician group
            technician_group = Group.objects.get(name='technician')
            user.groups.add(technician_group)

            # Create TechnicianProfile
            profile = TechnicianProfile.objects.create(user=user)
            profile.departments.set(form.cleaned_data['departments'])
            profile.expertise.set(form.cleaned_data['expertise'])
            profile.save()

            messages.success(request, f"Technician '{user.username}' added successfully.")
            return redirect('technician_list')
    else:
        form = TechnicianCreationForm()

    return render(request, 'adminn/add_technician.html', {'form': form})

@login_required
@group_required('admin')
def staff_list(request):
    staff_group = Group.objects.get(name='staff')
    staff_users = User.objects.filter(groups=staff_group)

    from django.core.paginator import Paginator
    paginator = Paginator(staff_users, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'adminn/staff_list.html', {
        'page_obj': page_obj,
    })

@login_required
@group_required('admin')
def department_list(request):
    departments = ServiceCategory.objects.all().order_by("id")  

    paginator = Paginator(departments, 5)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'adminn/department_list.html', {
        'page_obj': page_obj,
    })

@login_required
@group_required('admin')
def in_progress_requests(request):
    requests_list = ServiceRequest.objects.filter(status='In Progress').order_by('-created_at')

    paginator = Paginator(requests_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'adminn/in_progress_requests_admin.html', {
        'requests': page_obj,
    })

@login_required
@group_required('admin')
def service_category(request):
    categories = ServiceCategory.objects.all().order_by("id") 

    paginator = Paginator(categories, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'adminn/service_category.html', {
        'page_obj': page_obj
    })

@login_required
@group_required('admin')
def priority_list(request):
    priorities = PriorityLevel.objects.all().order_by("id") 
    paginator = Paginator(priorities, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'adminn/priority_list.html', {
        'page_obj': page_obj,
    })

@login_required
@group_required('admin')
def support_department_list(request):
    support_departments = SupportDepartment.objects.all().order_by("id")
    paginator = Paginator(support_departments, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'adminn/support_department_list.html', {
        'page_obj': page_obj,
    })

