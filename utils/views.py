import csv
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render
from service.models import ServiceRequest, ServiceCategory, TechnicianProfile
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.utils import timezone
from datetime import timedelta


def request_reports(request):
    qs = ServiceRequest.objects.select_related('category', 'assigned_to', 'created_by').all()

    # Filters
    status = request.GET.get('status')
    category = request.GET.get('category')
    technician = request.GET.get('technician')
    period = request.GET.get('period')
    export = request.GET.get('export')

    if status:
        qs = qs.filter(status=status)
    if category:
        qs = qs.filter(category_id=category)
    if technician:
        qs = qs.filter(assigned_to_id=technician)

    # Period filtering (daily, weekly, monthly, etc.)
    now = timezone.now()
    if period == "hourly":
        qs = qs.filter(created_at__gte=now - timedelta(hours=1))
    elif period == "daily":
        qs = qs.filter(created_at__date=now.date())
    elif period == "weekly":
        qs = qs.filter(created_at__gte=now - timedelta(days=7))
    elif period == "monthly":
        qs = qs.filter(created_at__month=now.month, created_at__year=now.year)
    elif period == "annual":
        qs = qs.filter(created_at__year=now.year)

    # Export CSV
    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="service_requests.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Title', 'Requester', 'Technician', 'Category',
            'Priority', 'Status', 'Created At', 'Updated At'
        ])
        for r in qs:
            writer.writerow([
                r.id,
                r.title,
                r.created_by.get_full_name(),
                r.assigned_to.get_full_name() if r.assigned_to else '',
                r.category.name,
                r.priority.name if r.priority else '',
                r.status,
                r.created_at,
                r.updated_at
            ])
        return response

    # Export Excel
    if export == 'excel':
        df = pd.DataFrame([{
            'ID': r.id,
            'Title': r.title,
            'Requester': r.created_by.get_full_name(),
            'Technician': r.assigned_to.get_full_name() if r.assigned_to else '',
            'Category': r.category.name,
            'Priority': r.priority.name if r.priority else '',
            'Status': r.status,
            'Created At': r.created_at.replace(tzinfo=None),  # make naive
            'Updated At': r.updated_at.replace(tzinfo=None),  # make naive
        } for r in qs])
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="service_requests.xlsx"'
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return response

    # Export PDF
    if export == 'pdf':
        html_string = render_to_string('adminn/request_reports_pdf.html', {'requests': qs})
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="service_requests.pdf"'
        pisa_status = pisa.CreatePDF(html_string, dest=response)
        return response

    # Pagination
    paginator = Paginator(qs.order_by('-created_at'), 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'statuses': [s[0] for s in ServiceRequest.STATUS_CHOICES],
        'categories': ServiceCategory.objects.all(),
        'technicians': TechnicianProfile.objects.select_related('user').all(),
        'page_obj': page_obj,
        'filters': request.GET
    }

    return render(request, 'adminn/request_reports.html', context)

def request_reports_print(request):
    qs = ServiceRequest.objects.select_related('category', 'assigned_to', 'created_by').all()
    # Same filters as above
    status = request.GET.get('status')
    category = request.GET.get('category')
    technician = request.GET.get('technician')
    period = request.GET.get('period')

    from django.utils import timezone
    from datetime import timedelta
    now = timezone.now()
    if status:
        qs = qs.filter(status=status)
    if category:
        qs = qs.filter(category_id=category)
    if technician:
        qs = qs.filter(assigned_to_id=technician)
    if period == "hourly":
        qs = qs.filter(created_at__gte=now - timedelta(hours=1))
    elif period == "daily":
        qs = qs.filter(created_at__date=now.date())
    elif period == "weekly":
        qs = qs.filter(created_at__gte=now - timedelta(days=7))
    elif period == "monthly":
        qs = qs.filter(created_at__month=now.month, created_at__year=now.year)
    elif period == "annual":
        qs = qs.filter(created_at__year=now.year)

    return render(request, 'adminn/request_reports_print.html', {'requests': qs})
