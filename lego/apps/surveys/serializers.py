from django.db import transaction
from rest_framework import serializers

from lego.apps.surveys import constants
from lego.apps.surveys.models import Alternative, Answer, Question, Submission, Survey, Template
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer


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
        if question.question_type == value == constants.CHECK_BOX:
            return value
        elif question.question_type == constants.CHECK_BOX\
                and value in [constants.CHECK_BOX, constants.TEXT_BOX]:
            return value
        elif question.question_type == value == constants.TEXT_BOX:
            return value
        raise serializers.ValidationError('This alternative type does not match the question type')


class AlternativeReadSerializer(BasisModelSerializer):
    class Meta:
        model = Alternative
        fields = ('id', 'alternative_text', 'alternative_type')
        extra_kwargs = {'id': {'read_only': False, 'required': False}}


class QuestionReadSerializer(BasisModelSerializer):
    alternatives = AlternativeReadSerializer(many=True)

    class Meta:
        model = Question
        fields = ('id', 'question_type', 'question_text',  'mandatory', 'alternatives')


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
        question = Question.objects.create(
            survey=survey, relative_index=relative_index, **validated_data
        )
        return question


class AnswerSerializer(BasisModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'submission', 'alternative', 'answer_text')


class SubmissionReadSerializer(BasisModelSerializer):
    user = PublicUserSerializer()

    class Meta:
        model = Submission
        fields = ('id', 'user', 'submitted', 'submitted_time')


class SubmissionReadDetailedSerializer(BasisModelSerializer):
    user = PublicUserSerializer()
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Submission
        fields = ('id', 'user', 'survey', 'submitted', 'submitted_time', 'answers')


class SubmissionCreateAndUpdateSerializer(BasisModelSerializer):
    class Meta:
        model = Submission
        fields = ('id', 'user', 'answers')

    def create(self, validated_data):
        survey_id = self.context['view'].kwargs['survey_pk']
        answers = validated_data.pop('answers', [])
        with transaction.atomic():
            submission = Submission.objects.create(survey_id=survey_id, **validated_data)
            for answer in answers:
                Answer.objects.create(submission=submission, **answer)
            return submission


class SurveyReadSerializer(BasisModelSerializer):
    questions = QuestionReadSerializer(many=True)

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'event', 'questions')


class SurveyReadDetailedSerializer(BasisModelSerializer):
    submissions = SubmissionReadDetailedSerializer(many=True)
    questions = QuestionReadSerializer(many=True)

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

        for data in questions:
            alternatives = data.pop('alternatives', [])
            question = Question.objects.create(survey=survey, **data)
            for alternative in alternatives:
                Alternative.objects.create(question=question, **alternative)
        return survey
