from rest_framework import serializers

from lego.apps.events.serializers.events import EventReadSerializer
from lego.apps.surveys import constants
from lego.apps.surveys.models import Alternative, Answer, Question, Submission, Survey, Template
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer


class QuestionSerializer(BasisModelSerializer):
    question_type = serializers.ChoiceField(choices=constants.ALTERNATIVE_TYPES)

    class Meta:
        model = Question
        fields = ('id', 'question_type', 'question_text',  'mandatory')

    def create(self, validated_data):
        survey = Survey.objects.get(pk=self.context['view'].kwargs['survey_pk'])
        question = Question.objects.create(survey=survey, **validated_data)
        question.relative_index = question.survey.questions.count() + 1
        question.save()
        return question


class AlternativeSerializer(BasisModelSerializer):

    class Meta:
        model = Alternative
        fields = ('id', 'alternative_text', 'alternative_type')

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
    questions = QuestionSerializer(many=True)
    event = EventReadSerializer()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'questions',
                  'submissions', 'event', 'template_type')


class SurveyCreateAndUpdateSerializer(BasisModelSerializer):
    clone_id = serializers.IntegerField()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'clone_id', 'event', 'questions')

    def create(self, validated_data):
        clone_id = validated_data.pop('clone_id', None)
        event = validated_data.pop('event', None)
        questions = validated_data.pop('questions', None)
        if clone_id:
            template = Template.objects.get(pk=clone_id)
            survey = template.generate_survey(event, validated_data)
        else:
            survey = Survey.objects.create(**validated_data)

        if questions:
            for question in questions:
                alternatives = questions.pop('alternatives', None)
                Question.objects.create(**question)
                for alternative in alternatives:
                    Alternative.objects.create(**alternative)
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
