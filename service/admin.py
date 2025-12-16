from django.contrib import admin
from .models import ServiceRequest, ServiceCategory, PriorityLevel, SupportDepartment, TechnicianProfile, Location
from users.models import Notification


admin.site.register(ServiceRequest)
admin.site.register(ServiceCategory)
admin.site.register(PriorityLevel)
admin.site.register(SupportDepartment)
admin.site.register(TechnicianProfile)
admin.site.register(Location)
admin.site.register(Notification)

