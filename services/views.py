from django.shortcuts import render
from .models import Service  

def services_view(request):
    services = Service.objects.all().order_by('name')
    return render(request, 'services.html', {'services': services})