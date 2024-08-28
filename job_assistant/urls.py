from django.contrib import admin
from django.urls import path, include

from rest_framework import routers

from job_assistant.crawlers.api.views import JobAdViewSet,CategoryViewSet, ProfileViewSet, TechnologyViewSet, WorkplaceViewSet, SearchViewSet

router = routers.DefaultRouter()
router.register(r"job-ads", JobAdViewSet)
router.register(r"categories", CategoryViewSet)
router.register(r"technologies", TechnologyViewSet)
router.register(r"workplaces", WorkplaceViewSet)
router.register(r"searches", SearchViewSet)
router.register(r"profiles", ProfileViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", admin.site.urls),

]
