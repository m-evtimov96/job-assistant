from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from job_assistant.crawlers.api.serializers import JobAdSerializer, CategorySerializer
from job_assistant.crawlers.models import JobAd, Category
from django_filters.rest_framework import DjangoFilterBackend


class JobAdViewSet(ReadOnlyModelViewSet):
    queryset = JobAd.objects.all()
    serializer_class = JobAdSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["workplace", "categories"]
    # search_fields = ["categories"]
    ordering = ["-date"]


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]
    ordering = ["id"]