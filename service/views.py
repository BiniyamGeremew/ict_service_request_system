from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ServiceRequestForm
from users.forms import EditProfileForm
from .models import ServiceRequest, PriorityLevel, TechnicianProfile, ServiceCategory
from users.decorators import group_required  
from django.contrib.auth import get_user_model
from django.db.models import Case, When, Value, IntegerField
from django.core.paginator import Paginator
from django.utils import timezone
import json

@login_required
@group_required('staff')
def submit_request_view(request):
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, request.FILES)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.created_by = request.user
            service_request.status = 'New'
            service_request.department = request.user.department
            service_request.save()
            messages.success(request, 'Request submitted successfully.')
            return redirect('submit_request')
    else:
        form = ServiceRequestForm()
    return render(request, 'staff/submit_request.html', {'form': form})

@login_required
@group_required('staff')
def my_requests(request):
    # Define the status order
    status_order = Case(
        When(status='New', then=1),
        When(status='Assigned', then=2),
        When(status='Accepted', then=3),
        When(status='In Progress', then=4),
        When(status='Completed', then=5),
        When(status='Rejected', then=6),
        default=7,
        output_field=IntegerField()
    )

    requests_qs = ServiceRequest.objects.filter(created_by=request.user).annotate(
        status_order=status_order
    ).order_by(
        'status_order',            # Custom status order ascending
        'priority__resolution_time_hours',  # Priority by expected resolution time ascending
        '-created_at'              # Latest requests first
    )

    paginator = Paginator(requests_qs, 5) 
    page_number = request.GET.get('page')
    requests_page = paginator.get_page(page_number)

    return render(request, 'staff/my_requests.html', {
        'requests': requests_page
    })

@login_required
@group_required('staff')
def request_details(request, pk):
    req = get_object_or_404(ServiceRequest, pk=pk, created_by=request.user)
    return render(request, 'staff/request_details.html', {'request_obj': req})

@login_required
@group_required('staff')
def edit_request(request, pk):
    request_obj = get_object_or_404(ServiceRequest, pk=pk, created_by=request.user)

    if request.method == "POST":
        form = ServiceRequestForm(request.POST, request.FILES, instance=request_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Request updated successfully.")
            return redirect('my_requests')
    else:
        form = ServiceRequestForm(instance=request_obj)

    return render(request, 'staff/edit_request.html', {
        'form': form,
        'request_obj': request_obj
    })

@login_required
@group_required('staff')
def delete_request(request, pk):
    req = get_object_or_404(ServiceRequest, pk=pk, created_by=request.user)

    if request.method == 'POST':
        req.delete()
        messages.success(request, 'Request deleted successfully.')
        return redirect('my_requests')

# ADMIN VIEWS
@login_required
@group_required('admin') 
def all_requests(request):
    requests_qs = ServiceRequest.objects.all()
    status = request.GET.get('status')    
    priority = request.GET.get('priority') 

    if status:
        requests_qs = requests_qs.filter(status=status)
    if priority:
        requests_qs = requests_qs.filter(priority_id=priority)

    # --- Add sorting logic: Status → Priority → Newest ---
    requests_qs = requests_qs.annotate(
        status_order=Case(
            When(status='New', then=Value(1)),           # Highest priority: New
            When(status='Assigned', then=Value(2)),      # Then assigned
            When(status='Accepted', then=Value(3)),      # Technician accepted
            When(status='In Progress', then=Value(4)),   # Technician started work
            When(status='Completed', then=Value(5)),     # Work finished
            When(status='Rejected', then=Value(6)),      # Rejected tasks
            default=Value(7),
            output_field=IntegerField()
        )
    ).order_by(
        'status_order',
        'priority__resolution_time_hours',
        '-created_at'
    )

    paginator = Paginator(requests_qs, 5)
    page_number = request.GET.get('page')
    requests_page = paginator.get_page(page_number)

    priorities = PriorityLevel.objects.all()

    return render(request, 'adminn/all_requests.html', {
        'requests': requests_page,
        'priorities': priorities
    })

@login_required
@group_required('admin')
def admin_request_details(request, request_id):

    request_obj = get_object_or_404(ServiceRequest, id=request_id)

    return render(request, 'adminn/admin_request_details.html', {
        'request_obj': request_obj,
    })

@login_required
@group_required('admin')
def assign_technician(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)

    if service_request.assigned_to:
        messages.warning(request, "This request is already assigned to a technician.")
        return redirect('all_requests')

    # Get technicians with expertise in this request's category
    category = service_request.category
    technicians = TechnicianProfile.objects.filter(
        expertise=category
    ).select_related('user')

    # Sort by fewest active requests first
    sorted_techs = sorted(technicians, key=lambda t: t.active_request_count)

    if request.method == 'POST':
        technician_id = request.POST.get('technician')
        technician = get_object_or_404(TechnicianProfile, id=technician_id)

        service_request.assigned_to = technician.user
        service_request.status = 'Assigned'
        service_request.save()

        messages.success(request, f"Technician {technician.user.get_full_name()} assigned successfully.")
        return redirect('all_requests')

    return render(request, 'adminn/assign_technician.html', {
        'service_request': service_request,
        'technicians': sorted_techs,
    })

User = get_user_model()

@login_required
@group_required('admin')
def technician_detail(request, pk):
    technician = get_object_or_404(User, pk=pk)
    return render(request, 'adminn/technician_detail.html', {
        'technician': technician
    })

@login_required
@group_required('admin')
def completed_requests(request):
    requests_qs = ServiceRequest.objects.filter(status='Completed')
    return render(request, 'adminn/completed_requests.html', {'requests': requests_qs})

@login_required
@group_required('admin')
def in_progress_requests(request):
    requests_qs = ServiceRequest.objects.filter(status='In Progress')
    return render(request, 'adminn/in_progress_requests.html', {'requests': requests_qs})

@login_required
@group_required('admin')
def pending_requests(request):
    requests_qs = ServiceRequest.objects.filter(status='New')
    return render(request, 'adminn/pending_requests.html', {'requests': requests_qs})

@login_required
@group_required('admin')
def technician_list(request):
    technicians = TechnicianProfile.objects.select_related('user').all()

    paginator = Paginator(technicians, 5)
    page_number = request.GET.get('page')
    technicians_page = paginator.get_page(page_number)

    return render(request, 'adminn/technician_list.html', {
        'technicians': technicians_page
    })

# TECHNICIAN VIEWS
@login_required
@group_required('technician')
def technician_dashboard(request):
    # Requests assigned to this technician
    user_requests = ServiceRequest.objects.filter(assigned_to=request.user)

    # --- Quick stats cards ---
    total_assigned = user_requests.count()
    accepted = user_requests.filter(status='Accepted').count()
    in_progress = user_requests.filter(status='In Progress').count()
    completed = user_requests.filter(status='Completed').count()
    rejected = user_requests.filter(status='Rejected').count()
    awaiting_confirmation = user_requests.filter(status='Awaiting Confirmation').count()  # updated to use user_requests

    # --- Categories for charts ---
    category_labels = list(ServiceCategory.objects.values_list('name', flat=True))
    category_counts = [user_requests.filter(category=c).count() for c in ServiceCategory.objects.all()]

    # --- Statuses for charts ---
    status_labels = ['New', 'Assigned', 'Accepted', 'In Progress', 'Completed', 'Rejected']
    status_counts = [user_requests.filter(status=s).count() for s in status_labels]

    # --- Latest requests table ---
    latest_requests = user_requests.order_by('-created_at')[:5]

    context = {
        'page_title': 'Technician Dashboard',
        'category_labels_json': json.dumps(category_labels),
        'category_counts_json': json.dumps(category_counts),
        'status_labels_json': json.dumps(status_labels),
        'status_counts_json': json.dumps(status_counts),
        'total_assigned': total_assigned,
        'accepted': accepted,
        'in_progress': in_progress,
        'completed': completed,
        'rejected': rejected,
        'awaiting_confirmation': awaiting_confirmation,  
        'latest_requests': latest_requests,
    }
    return render(request, 'technician/technician_dashboard.html', context)

@login_required
@group_required('technician')
def technician_assigned_requests(request):
    assigned_requests = ServiceRequest.objects.filter(assigned_to=request.user, status__in=['Assigned', 'Accepted', 'In Progress'])
    return render(request, 'technician/technician_assigned_requests.html', {
        'assigned_requests': assigned_requests
    })

@login_required
@group_required('technician')
def technician_request_detail(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id, assigned_to=request.user)
    return render(request, 'technician/technician_request_detail.html', {
        'service_request': service_request
    })

@login_required
@group_required('technician')
def technician_start_request(request, request_id):
    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id,
        assigned_to=request.user,
        status='Accepted'
    )

    service_request.status = 'In Progress'
    service_request.save()

    messages.success(request, f"Request #{service_request.id} is now In Progress.")
    return redirect('technician_in_progress')

@login_required
@group_required('technician')
def technician_in_progress(request):
    in_progress = ServiceRequest.objects.filter(assigned_to=request.user, status='In Progress')
    return render(request, 'technician/technician_in_progress.html', {'in_progress': in_progress})

@login_required
@group_required('technician')
def technician_completed_requests(request):
    completed_requests = ServiceRequest.objects.filter(
        assigned_to=request.user,
        status='Completed'
    )
    return render(request, 'technician/technician_completed_requests.html', {'completed_requests': completed_requests})

@login_required
@group_required('technician')
def technician_profile(request):
    context = {}
    return render(request, 'technician/technician_profile.html', context)

@login_required
def technician_edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('view_profile')
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'technician/technician_edit_profile.html', {'form': form})

@login_required
@group_required('technician')
def technician_notifications(request):
    context = {}
    return render(request, 'technician/technician_notifications.html', context)

@login_required
@group_required('technician')
def technician_accepted_requests(request):
    accepted_requests = ServiceRequest.objects.filter(
        assigned_to=request.user,
        status='Accepted'
    )
    return render(request, 'technician/technician_accepted_requests.html', {
        'accepted_requests': accepted_requests
    })

@login_required
@group_required('technician')
def technician_rejected_requests(request):
    rejected_requests = ServiceRequest.objects.filter(
        assigned_to=request.user,
        status='Rejected'
    )
    return render(request, 'technician/technician_rejected_requests.html', {
        'rejected_requests': rejected_requests
    })

@login_required
@group_required('technician')
def technician_reject_request(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id, assigned_to=request.user)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        if reason:
            service_request.status = 'Rejected'
            service_request.rejection_reason = reason  
            service_request.save()

            messages.success(request, f"Request #{service_request.id} has been rejected.")
            return redirect('technician_assigned_requests')
        else:
            messages.error(request, "Please provide a reason for rejection.")

    return redirect('technician_assigned_requests')

@login_required
@group_required('technician')
def technician_accept_request(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id, assigned_to=request.user, status='Assigned')
    service_request.status = 'Accepted'
    service_request.save()
    messages.success(request, f"Request #{service_request.id} accepted successfully.")
    return redirect('technician_assigned_requests')

@login_required
@group_required('technician')
def technician_reject_request(request, request_id):
    if request.method == 'POST':
        reason = request.POST.get('reason')
        service_request = get_object_or_404(ServiceRequest, id=request_id, assigned_to=request.user, status='Assigned')
        service_request.status = 'Rejected'
        service_request.rejection_reason = reason  
        service_request.save()
        messages.warning(request, f"Request #{service_request.id} rejected.")
    return redirect('technician_assigned_requests')

# MANAGER VIEWS
@login_required
@group_required('manager')
def manager_dashboard(request):
    context = {}
    return render(request, 'manager/manager_dashboard.html', context)

@login_required
@group_required('staff')
def confirm_completion(request, pk):
    req = get_object_or_404(ServiceRequest, pk=pk, created_by=request.user)

    if req.status != "Awaiting Confirmation":
        messages.error(request, "This request cannot be confirmed yet.")
        return redirect('my_requests')

    req.status = "Completed"
    req.save()
    messages.success(request, "Request marked as completed successfully.")
    return redirect('my_requests')

@login_required
@group_required('technician')
def mark_request_complete(request, pk):
    service_request = get_object_or_404(ServiceRequest, pk=pk, assigned_to=request.user)
    service_request.status = 'Awaiting Confirmation' 
    service_request.completed_at = timezone.now()
    service_request.save()
    messages.success(request, f"Request #{service_request.id} marked as completed, awaiting staff confirmation.")
    return redirect('technician_completed_requests')

@login_required
@group_required('technician')
def technician_awaiting_confirmation(request):
    # Filter requests for the logged-in user that are awaiting confirmation
    requests = ServiceRequest.objects.filter(
        assigned_to=request.user, 
        status="Awaiting Confirmation"
    )
    context = {
        'requests': requests
    }
    return render(request, 'technician/awaiting_confirmation.html', context)
