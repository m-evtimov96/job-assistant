from django.db.models import Q
from rest_framework.filters import BaseFilterBackend
import django_filters
from job_assistant.crawlers.models import JobAd

class MultiKeywordNameSearchFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_terms = request.query_params.get('search', '').split()
        if not search_terms:
            return queryset
        
        query = Q()
        for term in search_terms:
            query |= Q(name__icontains=term)
        
        return queryset.filter(query)
    


class JobAdFilterSet(django_filters.FilterSet):
    id = django_filters.BaseInFilter(field_name='id', lookup_expr='in')
    workplace = django_filters.BaseInFilter(field_name='workplace', lookup_expr='in')
    categories = django_filters.BaseInFilter(field_name='categories', lookup_expr='in')
    technologies = django_filters.BaseInFilter(field_name='technologies', lookup_expr='in')

    class Meta:
        model = JobAd
        fields = ['id', 'workplace', 'categories', 'technologies']
