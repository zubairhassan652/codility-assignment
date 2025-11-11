from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import JobViewSet, import_jobs_from_csv, scrape_indeed

router = DefaultRouter()
router.register('jobs', JobViewSet, basename='jobs')

urlpatterns = [
    path("scrape-jobs/", scrape_indeed),
    path('import-csv/', import_jobs_from_csv), 
    path("", include(router.urls)),
]
