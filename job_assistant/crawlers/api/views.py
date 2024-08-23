from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from job_assistant.crawlers.api.serializers import JobAdSerializer, CategorySerializer, TechnologySerializer, WorkplaceSerializer
from job_assistant.crawlers.models import JobAd, Category, Technology, Workplace
from django_filters.rest_framework import DjangoFilterBackend


class JobAdViewSet(ReadOnlyModelViewSet):
    queryset = JobAd.objects.all()
    serializer_class = JobAdSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # TODO: Make the filter fields shorter in the url https://stackoverflow.com/questions/57846913/django-rest-framework-filtering-using-or-on-multiple-values-from-one-url-para
    filterset_fields = ["workplace", "categories", "technologies"]
    # search_fields = ["categories"]
    ordering = ["-date"]


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]
    ordering = ["id"]


class TechnologyViewSet(ReadOnlyModelViewSet):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]
    ordering = ["id"]


class WorkplaceViewSet(ReadOnlyModelViewSet):
    queryset = Workplace.objects.all()
    serializer_class = WorkplaceSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]
    ordering = ["id"]