
from rest_framework import serializers

from job_assistant.crawlers.models import JobAd

class JobAdSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = JobAd
        fields = "__all__"