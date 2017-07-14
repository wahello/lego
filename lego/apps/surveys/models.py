from django.db import models
from django.utils import timezone

from lego.apps.events.constants import EVENT_TYPES
from lego.apps.surveys import constants
from lego.apps.users.models import User
from lego.utils.models import BasisModel


class Survey(BasisModel):
    title = models.CharField(max_length=100)
    active_from = models.DateTimeField(default=timezone.now)
    template_type = models.CharField(max_length=30, choices=EVENT_TYPES, null=True, blank=True)
    is_clone = models.BooleanField(default=False)
    event = models.OneToOneField('events.Event')

    @property
    def is_template(self):
        return self.template_type is not None

    def number_of_submissions(self):
        return self.submissions.filter(submitted=True).count()

    def is_answered_by_someone(self):
        if self.number_of_submissions():
            return True
        return False


class Question(BasisModel):
    class Meta:
        ordering = ['relative_index']

    survey = models.ForeignKey(Survey, related_name='questions')
    question_type = models.CharField(max_length=255, choices=constants.ALTERNATIVE_TYPES)
    question_text = models.TextField(max_length=255)
    mandatory = models.BooleanField(default=False)
    relative_index = models.IntegerField(null=True)


class Alternative(BasisModel):
    question = models.ForeignKey(Question, related_name='alternatives')
    alternative_text = models.TextField(max_length=255)
    alternative_type = models.CharField(max_length=255, choices=constants.ALTERNATIVE_TYPES)


class Submission(BasisModel):
    user = models.ForeignKey(User, related_name='surveys')
    survey = models.ForeignKey(Survey, related_name='submissions')
    submitted_time = models.DateTimeField(null=True)
    submitted = models.BooleanField(default=False)

    def submit(self):
        self.submitted = True
        self.submitted_time = timezone.now()
        self.save()


class Answer(BasisModel):
    submission = models.ForeignKey(Submission, related_name='answers')
    question = models.ForeignKey(Question, related_name='answers')


class ChoiceAnswer(BasisModel):
    answer = models.ForeignKey(Answer, related_name='choice_answer')
    selected_answer = models.PositiveSmallIntegerField()


class TextAnswer(BasisModel):
    answer = models.ForeignKey(Answer, related_name='text_answer')
    answer_text = models.TextField(max_length=255, blank=True)


class Template(Survey):

    def generate_survey(self, event, validated_data):
        survey = Survey.objects.create(event=event, **validated_data)

        for question in self.questions.all():
            copied_q = question
            copied_q.pk = None
            question = Question.objects.create(survey=survey, **copied_q)

            for alternative in question.alternatives.all().reverse():
                copied_a = alternative
                copied_a.pk = None
                Alternative.objects.create(question=question, **copied_a)
