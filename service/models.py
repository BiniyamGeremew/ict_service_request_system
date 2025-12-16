from django.db import models
from django.conf import settings

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class PriorityLevel(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default='blue')
    resolution_time_hours = models.PositiveIntegerField(help_text="Expected resolution time in hours")

    def __str__(self):
        return self.name


class SupportDepartment(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class TechnicianProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    expertise = models.ManyToManyField(ServiceCategory)
    departments = models.ManyToManyField(SupportDepartment, blank=True)  # Optional

    def __str__(self):
        return f"{self.user.username} - Technician"

    @property
    def active_request_count(self):
        """
        Count active requests assigned to this technician.
        Active means: 'Assigned' or 'In Progress'
        """
        return self.user.requests_assigned.filter(
            status__in=['Assigned', 'In Progress']
        ).count()


class Location(models.Model):
    block_building = models.CharField(max_length=100)
    floor = models.CharField(max_length=50)
    room = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.block_building} - Floor {self.floor} - Room {self.room}"

class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),                 
        ('Assigned', 'Assigned'),      
        ('Accepted', 'Accepted'),      
        ('Rejected', 'Rejected'),       
        ('In Progress', 'In Progress'), 
        ('Awaiting Confirmation', 'Awaiting Confirmation'),  
        ('Completed', 'Completed'),   
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)

    #location = models.CharField(max_length=255)

    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    priority = models.ForeignKey(PriorityLevel, on_delete=models.SET_NULL, null=True)
    attachment = models.FileField(upload_to='service_attachments/', null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requests_made'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requests_assigned'
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='New'
    )

    rejection_reason = models.TextField(blank=True, null=True)
    rejected_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


