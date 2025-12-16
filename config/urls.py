from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),  
    path('request/', include('service.urls')),
    path('', include('utils.urls')),
]
