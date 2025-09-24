from rest_framework import viewsets
from .models import SafetyReport, SafeRoute, LoadShedding
from .serializers import SafetyReportSerializer, SafeRouteSerializer, LoadSheddingSerializer
from django.shortcuts import render

# API ViewSets
class SafetyReportViewSet(viewsets.ModelViewSet):
    queryset = SafetyReport.objects.all().order_by('-timestamp')
    serializer_class = SafetyReportSerializer

class SafeRouteViewSet(viewsets.ModelViewSet):
    queryset = SafeRoute.objects.all().order_by('-timestamp')
    serializer_class = SafeRouteSerializer

class LoadSheddingViewSet(viewsets.ModelViewSet):
    queryset = LoadShedding.objects.all().order_by('-start_time')
    serializer_class = LoadSheddingSerializer

# Dashboard page
def dashboard(request):
    return render(request, "dashboard.html")
