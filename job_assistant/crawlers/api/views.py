from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from job_assistant.crawlers.api.serializers import JobAdSerializer
from job_assistant.crawlers.models import JobAd
from django_filters.rest_framework import DjangoFilterBackend


class JobAdViewSet(ReadOnlyModelViewSet):
    queryset = JobAd.objects.all()
    serializer_class = JobAdSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["workplace", "categories"]
    # search_fields = ["categories"]
    ordering = ["-date"]