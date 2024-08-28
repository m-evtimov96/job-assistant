
from rest_framework import serializers

from job_assistant.crawlers.models import Favourite, JobAd, Category, Profile, Technology, Workplace, Search

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
        fields = ["id", "url", "title", "date", "company", "workplace", "categories", "technologies"]

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

class SearchSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Search
        fields = ["user", "categories", "technologies", "workplaces"]

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ["user", "bio", "education", "work_experience", "skills", "other"]

class FavouriteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Favourite
        fields = ["user", "job_ad"]
