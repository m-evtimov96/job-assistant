from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from job_assistant.crawlers.api.serializers import FavouriteSerializer, JobAdSerializer, CategorySerializer, ProfileSerializer, TechnologySerializer, WorkplaceSerializer, SearchSerializer
from job_assistant.crawlers.api.filters import JobAdFilterSet, MultiKeywordNameSearchFilter
from job_assistant.crawlers.models import Favourite, JobAd, Category, Profile, Technology, Workplace, Search
from django_filters.rest_framework import DjangoFilterBackend


class JobAdViewSet(ReadOnlyModelViewSet):
    queryset = JobAd.objects.all()
    serializer_class = JobAdSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JobAdFilterSet
    search_fields = ["title"] #This searches with AND, maybe change to OR ? and maybe add body field ?
    ordering = ["-date"]


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [MultiKeywordNameSearchFilter]
    ordering = ["id"]

class TechnologyViewSet(ReadOnlyModelViewSet):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    filter_backends = [MultiKeywordNameSearchFilter]
    ordering = ["id"]


class WorkplaceViewSet(ReadOnlyModelViewSet):
    queryset = Workplace.objects.all()
    serializer_class = WorkplaceSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]
    ordering = ["id"]


class SearchViewSet(ModelViewSet):
    queryset = Search.objects.all()
    serializer_class = SearchSerializer
    lookup_field = "user"


class ProfileViewSet(ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = "user"


class FavouriteViewSet(ModelViewSet):
    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'job_ad']    
    lookup_field = "user"
