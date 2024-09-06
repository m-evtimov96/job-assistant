from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from job_assistant.crawlers.api.serializers import FavouriteSerializer, JobAdSerializer, CategorySerializer, ProfileSerializer, TechnologySerializer, WorkplaceSerializer, SearchSerializer
from job_assistant.crawlers.api.filters import JobAdFilterSet, MultiKeywordNameSearchFilter
from job_assistant.crawlers.models import Favourite, JobAd, Category, Profile, Technology, Workplace, Search
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse
from openai import OpenAI, OpenAIError
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from io import BytesIO
import base64
from job_assistant.settings import OPENAI_API_KEY


class JobAdViewSet(ReadOnlyModelViewSet):
    queryset = JobAd.objects.all()
    serializer_class = JobAdSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JobAdFilterSet
    search_fields = ["title", "body"] #This searches with AND, maybe change to OR ?
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
    lookup_field = "id"


class GenerateCVView(APIView):
    def post(self, request):
        jobad_id = request.data.get('jobad_id')
        user_id = request.data.get('user_id')

        job_ad = JobAd.objects.get(id=jobad_id)
        try:
            profile = Profile.objects.get(user=user_id)
        except Profile.DoesNotExist:
            return Response({"error": "Profile is not configured for this user."}, status=status.HTTP_400_BAD_REQUEST)

        prompt = (
            f"""
            Generate a professional CV for a user applying for the position of {job_ad.title}.
            
            Start the CV directly with the personal information and do not include any introductory text or phrases like 'Certainly!' or 'Here is a tailored CV...'.
            The CV should include the following sections: Contact Information, Professional Summary, Skills, Experience, Education, and any other relevant sections.
            If the User Profile data does not match the Job Details, try to think of ways to adapt the user skills to the job ad in the CV text.
            At the end of the CV paragraphs make another one (about a half page) for a letter of motivation, using both the job ad info and the user profile for it.
            
            User Profile:
            Bio: {profile.bio}
            Experience: {profile.work_experience}
            Education: {profile.education}
            Skills: {profile.skills}
            Other Information: {profile.other}

            Job Details:
            Job Title: {job_ad.title}
            Job Description: {job_ad.body}
            """
        )
        client = OpenAI(
            api_key=OPENAI_API_KEY,
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional CV generator."},
                    {"role": "user", "content": prompt}
                ],
            )
            cv_text = response.choices[0].message.content

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            normal_style = styles['Normal']
            paragraphs = cv_text.split('\n')
            
            content = []
            for paragraph in paragraphs:
                p = Paragraph(paragraph, normal_style)
                content.append(p)
                content.append(Spacer(1, 12))
            
            doc.build(content)
            buffer.seek(0)
            pdf = buffer.getvalue()
            buffer.close()

            pdf_base64 = base64.b64encode(pdf).decode('utf-8')

            response_data = {
                "job_title": job_ad.title,
                "pdf_content": pdf_base64
            }

            return JsonResponse(response_data, safe=False)
        except OpenAIError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
