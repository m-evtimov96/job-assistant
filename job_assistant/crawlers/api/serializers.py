
from rest_framework import serializers

from job_assistant.crawlers.models import JobAd, Category, Technology, Workplace

class JobAdSerializer(serializers.HyperlinkedModelSerializer):
    categories = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
     )
    technologies = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )
    workplace = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name"
    )
    class Meta:
        model = JobAd
        fields = ["url", "title", "body", "date", "company", "workplace", "categories", "technologies"]

class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class TechnologySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Technology
        fields = ["id", "name"]

class WorkplaceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Workplace
        fields = ["id", "name"]