from django import forms
from .models import ServiceRequest, Location

class ServiceRequestForm(forms.ModelForm):
    block_building = forms.CharField(max_length=100, required=True, label="Block/Building")
    floor = forms.CharField(max_length=50, required=True, label="Floor")
    room = forms.CharField(max_length=50, required=True, label="Room")

    class Meta:
        model = ServiceRequest
        fields = ['title', 'description', 'category', 'priority', 'attachment']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.location:
            self.fields['block_building'].initial = self.instance.location.block_building
            self.fields['floor'].initial = self.instance.location.floor
            self.fields['room'].initial = self.instance.location.room

    def save(self, commit=True):
        service_request = super().save(commit=False)

        block = self.cleaned_data['block_building']
        floor = self.cleaned_data['floor']
        room = self.cleaned_data['room']

        location_obj, created = Location.objects.get_or_create(
            block_building=block,
            floor=floor,
            room=room
        )
        service_request.location = location_obj

        if commit:
            service_request.save()
        return service_request
