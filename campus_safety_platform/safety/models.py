from django.db import models

class SafetyReport(models.Model):
    reporter = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    description = models.TextField()
    lat = models.FloatField()
    lon = models.FloatField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.category} by {self.reporter} at {self.timestamp}"

class SafeRoute(models.Model):
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    risk_score = models.FloatField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"Route {self.origin} -> {self.destination}"

class LoadShedding(models.Model):
    area = models.CharField(max_length=100)
    stage = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.area} stage {self.stage}"
