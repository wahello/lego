from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.db import models

from lego.apps.comments.models import Comment
from lego.apps.companies.permissions import (CompanyContactPermissionHandler,
                                             CompanyInterestPermissionHandler,
                                             CompanyPermissionHandler,
                                             NestedCompanyPermissionHandler)
from lego.apps.files.models import FileField
from lego.apps.users.models import User
from lego.utils.models import BasisModel, TimeStampModel

from .constants import (AUTUMN, COMPANY_EVENTS, SEMESTER, SEMESTER_STATUSES, SPRING,
                        TRANSLATED_EVENTS)


class Semester(BasisModel):
    year = models.PositiveIntegerField()
    semester = models.CharField(max_length=64, choices=SEMESTER)

    class Meta:
        unique_together = ('year', 'semester')
        permission_handler = CompanyPermissionHandler()


class Company(BasisModel):
    name = models.CharField(max_length=100)
    student_contact = models.ForeignKey(User, related_name='companies', null=True)
    previous_contacts = models.ManyToManyField(User)

    description = models.CharField(max_length=500, blank=True)
    phone = models.CharField(max_length=100, blank=True)
    company_type = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=100, blank=True)
    admin_comment = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)
    payment_mail = models.EmailField(max_length=100, blank=True)
    comments = GenericRelation(Comment)

    logo = FileField(related_name='company_logos')

    class Meta:
        permission_handler = CompanyPermissionHandler()

    @property
    def comment_target(self):
        return '{0}.{1}-{2}'.format(self._meta.app_label, self._meta.model_name, self.pk)

    def __str__(self):
        return self.name


class CompanyFile(models.Model):
    company = models.ForeignKey(Company, related_name='files')
    file = FileField()


class SemesterStatus(TimeStampModel):
    company = models.ForeignKey(Company, related_name='semester_statuses')
    semester = models.ForeignKey(Semester)
    contacted_status = ArrayField(models.CharField(choices=SEMESTER_STATUSES, max_length=64))
    contract = FileField()

    class Meta:
        unique_together = ('semester', 'company')
        permission_handler = NestedCompanyPermissionHandler()


class CompanyContact(BasisModel):
    company = models.ForeignKey(Company, related_name='company_contacts')
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    mail = models.EmailField(blank=True)
    phone = models.CharField(max_length=100, blank=True)
    mobile = models.CharField(max_length=100, blank=True)
    public = models.BooleanField(default=False)

    class Meta:
        permission_handler = CompanyContactPermissionHandler()


class CompanyInterest(BasisModel):
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    mail = models.EmailField()
    semesters = models.ManyToManyField(Semester, blank=True)
    events = ArrayField(models.CharField(max_length=64, choices=COMPANY_EVENTS))
    readme = models.BooleanField(default=False)
    collaboration = models.BooleanField(default=False)
    itdagene = models.BooleanField(default=False)
    comment = models.TextField(blank=True)

    class Meta:
        permission_handler = CompanyInterestPermissionHandler()

    def generate_mail_context(self):
        readme = 'Ja' if self.readme else 'Nei'
        collaboration = 'Ja' if self.collaboration else 'Nei'
        itdagene = 'Ja' if self.itdagene else 'Nei'

        semesters = []
        for semester in self.semesters.all():
            if semester.semester == SPRING:
                semesters.append(f'Vår {semester.year}')
            elif semester.semester == AUTUMN:
                semesters.append(f'Høst {semester.year}')

        events = []
        for event in self.events:
            events.append(TRANSLATED_EVENTS[event])

        return {
            'company_name': self.company_name,
            'contact_person': self.contact_person,
            'mail': self.mail,
            'semesters': ', '.join(semesters),
            'events': ', '. join(events),
            'readme': readme,
            'collaboration': collaboration,
            'itdagene': itdagene,
            'comment': self.comment
        }
