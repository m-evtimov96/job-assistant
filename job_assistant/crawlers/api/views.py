from rest_framework import viewsets
from job_assistant.crawlers.api.serializers import JobAdSerializer
from job_assistant.crawlers.models import JobAd


class JobAdViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JobAd.objects.all()
    serializer_class = JobAdSerializer