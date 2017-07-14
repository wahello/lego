from rest_framework import serializers

from lego.apps.events.serializers.events import EventReadSerializer
from lego.apps.surveys import constants
from lego.apps.surveys.models import Alternative, Answer, Question, Submission, Survey, Template
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer


class QuestionReadSerializer(BasisModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'question_type', 'question_text',  'mandatory')


class AlternativeCreateAndUpdateSerializer(BasisModelSerializer):
    alternative_type = serializers.ChoiceField(choices=constants.ALTERNATIVE_TYPES)

    class Meta:
        model = Alternative
        fields = ('id', 'alternative_text', 'alternative_type')
        extra_kwargs = {'id': {'read_only': False, 'required': False}}

    def create(self, validated_data):
        question = Question.objects.get(pk=self.context['view'].kwargs['question_pk'])
        alternative = Alternative.objects.create(question=question, **validated_data)
        return alternative

    def validate_alternative_type(self, value):
        question = Question.objects.get(pk=self.context['view'].kwargs['question_pk'])
        if question.question_type == 1 and value == 1:
            return value
        elif question.question_type == 2 and value in [2, 3]:
            return value
        elif question.question_type == 3 and value == 3:
            return value
        raise serializers.ValidationError('This alternative type does not match the question type')


class QuestionCreateAndUpdateSerializer(BasisModelSerializer):
    alternatives = AlternativeCreateAndUpdateSerializer(many=True)
    question_type = serializers.ChoiceField(choices=constants.ALTERNATIVE_TYPES)

    class Meta:
        model = Question
        fields = ('id', 'question_type', 'question_text',  'mandatory', 'alternatives')
        extra_kwargs = {'id': {'read_only': False, 'required': False}}

    def create(self, validated_data):
        survey = Survey.objects.get(pk=self.context['view'].kwargs['survey_pk'])
        relative_index = survey.question.count() + 1
        question = Question.objects.create(survey=survey, relative_index=relative_index, **validated_data)
        return question


class AnswerSerializer(BasisModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'submission', 'alternative', 'answer_text')


class SurveyReadSerializer(BasisModelSerializer):
    event = EventReadSerializer()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'event')


class SubmissionReadSerializer(BasisModelSerializer):
    user = PublicUserSerializer()
    survey = SurveyReadSerializer()

    class Meta:
        model = Submission
        fields = ('id', 'user', 'survey', 'submitted', 'submitted_time')


class SurveyReadDetailedSerializer(BasisModelSerializer):
    submissions = SubmissionReadSerializer(many=True)
    questions = QuestionReadSerializer(many=True)
    event = EventReadSerializer()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'questions',
                  'submissions', 'event', 'template_type')


class SurveyCreateAndUpdateSerializer(BasisModelSerializer):
    clone_id = serializers.IntegerField(required=False)
    questions = QuestionCreateAndUpdateSerializer(many=True)

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'clone_id', 'event', 'questions')

    def create(self, validated_data):
        clone_id = validated_data.get('clone_id', None)
        event = validated_data.get('event', None)
        questions = validated_data.pop('questions', [])
        if clone_id:
            template = Template.objects.get(pk=clone_id)
            survey = template.generate_survey(event, validated_data)
        else:
            survey = super().create(validated_data)

        for question in questions:
            alternatives = question.pop('alternatives', [])
            Question.objects.create(survey=survey, **question)
            for alternative in alternatives:
                Alternative.objects.create(question=question, **alternative)
        return survey


class SubmissionReadDetailedSerializer(BasisModelSerializer):
    user = PublicUserSerializer()
    survey = SurveyReadSerializer()
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Submission
        fields = ('id', 'user', 'survey', 'submitted', 'submitted_time', 'answers')


class SubmissionCreateAndUpdateSerializer(BasisModelSerializer):
    class Meta:
        model = Submission
        fields = ('id', 'user', 'survey')
