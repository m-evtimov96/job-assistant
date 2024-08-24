from django.db.models import Q
from rest_framework.filters import BaseFilterBackend

class MultiKeywordNameSearchFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_terms = request.query_params.get('search', '').split()
        if not search_terms:
            return queryset
        
        query = Q()
        for term in search_terms:
            query |= Q(name__icontains=term)
        
        return queryset.filter(query)