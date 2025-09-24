from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r"safety-reports", views.SafetyReportViewSet)
router.register(r"safe-routes", views.SafeRouteViewSet)
router.register(r"loadshedding", views.LoadSheddingViewSet)

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/", include(router.urls)),
]
