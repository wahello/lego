from rest_framework import decorators, mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from lego.apps.surveys.models import Submission, Survey
from lego.apps.surveys.serializers import (SubmissionCreateAndUpdateSerializer,
                                           SurveyCreateAndUpdateSerializer,
                                           SurveyReadDetailedSerializer, SurveyReadSerializer)


class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SurveyCreateAndUpdateSerializer
        elif self.action == 'retrieve':
            return SurveyReadDetailedSerializer
        return SurveyReadSerializer

    def get_queryset(self):
        if self.action in ['create', 'update', 'partial_update']:
            return self.queryset
        elif self.action == 'retrieve':
            return self.queryset.prefetch_related(
                'questions', 'questions__alternatives', 'submissions',
                'submissions__answers', 'submissions__user'
            )
        return self.queryset

    @decorators.detail_route(methods=['POST'])
    def submit(self, request, *args, **kwargs):
        # TODO
        pass

    @decorators.list_route(methods=['GET'])
    def all(self, request, *args, **kwargs):
        # TODO
        pass

    @decorators.detail_route(methods=['GET'])
    def statistics(self, request, *args, **kwargs):
        # TODO
        pass


class SubmissionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionCreateAndUpdateSerializer
