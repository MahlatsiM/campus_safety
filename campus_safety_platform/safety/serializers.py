from rest_framework import serializers
from .models import SafetyReport, SafeRoute, LoadShedding

class SafetyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyReport
        fields = "__all__"

class SafeRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafeRoute
        fields = "__all__"

class LoadSheddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoadShedding
        fields = "__all__"
