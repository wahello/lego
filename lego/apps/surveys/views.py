from rest_framework import decorators, viewsets

from lego.apps.surveys.models import Survey
from lego.apps.surveys.serializers import (SurveyCreateAndUpdateSerializer,
                                           SurveyReadDetailedSerializer, SurveyReadSerializer)


class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all().prefetch_related('questions', 'submissions')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SurveyCreateAndUpdateSerializer
        elif self.action in ['retrieve']:
            return SurveyReadDetailedSerializer
        return SurveyReadSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        survey = Survey.objects.get(instance.id)
        survey.delete()

    @decorators.detail_route(methods=['POST'])
    def submit(self, request, *args, **kwargs):
        #TODO
        pass

    @decorators.list_route(methods=['GET'])
    def all(self, request, *args, **kwargs):
        #TODO
        pass

    @decorators.detail_route(methods=['GET'])
    def statistics(self, request, *args,):
        #TODO
        pass