
from rest_framework import serializers

from job_assistant.crawlers.models import JobAd

class JobAdSerializer(serializers.HyperlinkedModelSerializer):
    categories = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
     )
    class Meta:
        model = JobAd
        fields = ["url", "title", "body", "date", "company", "workplace", "categories"]