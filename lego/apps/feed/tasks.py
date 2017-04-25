from smtplib import SMTPException

from django.conf import settings
from django.template import loader
from structlog import get_logger

from lego import celery_app
from lego.apps.feed.registry import get_handler
from lego.apps.users.models import User
from lego.utils.content_types import string_to_instance

log = get_logger()


@celery_app.task(serializer='pickle')
def add_to_feeds(instance, action='update'):
    """
    Add action to feed and notificationfeed of appropriate users
    """

    handler = get_handler(instance._meta.model)
    if handler is None:
        # No handler registered for model
        return

    handler.handle_event(instance, action)


@celery_app.task(serializer='pickle', bind=True)
def mail_penalty_create(self, activity, recipients):
    event = string_to_instance(activity.actor)
    user = User.objects.get(id=recipients[0])
    message = loader.get_template('email/penalty_email.html')
    reason = activity.extra_context.get('reason')
    weight = activity.extra_context.get('reason')
    total_weight = activity.extra_context.get('reason')

    context = {
        'name': user.get_short_name(),
        'event': event.title,
        'reason': reason,
        'weight': weight,
        'total': total_weight,
        'settings': settings
    }

    try:
        user.email_user(
            subject='Abakus.no - Ny prikk',
            message=message.render(context),
        )
    except SMTPException as e:
        log.error(
            'penalty_notification_send_email_error',
            exception=e,
            reg=event.registrations.get(user=user),
            user_id=user.id
        )
        raise self.retry(exc=e, max_retries=3)


@celery_app.task(serializer='pickle', bind=True)
def mail_registration_bump(self, activity, recipients):
    event = string_to_instance(activity.actor)
    user = User.objects.get(id=recipients[0])
    message = loader.get_template('email/bump_email.html')

    context = {
        'name': user.get_short_name(),
        'event': event.title,
        'slug': event.slug,
        'settings': settings
    }

    try:
        user.email_user(
            subject='Abakus.no - Flyttet opp fra venteliste',
            message=message.render(context),
        )
    except SMTPException as e:
        log.error(
            'bump_notification_send_email_error',
            exception=e,
            reg=event.registrations.get(user=user),
            user_id=user.id
        )
        raise self.retry(exc=e, max_retries=3)


@celery_app.task(serializer='pickle', bind=True)
def mail_admin_registration(self, activity, recipients):
    event = string_to_instance(activity.actor)
    user = User.objects.get(id=recipients[0])
    message = loader.get_template('email/admin_reg_email.html')
    reason = event.registrations.get(user=user).reason

    context = {
        'name': user.get_short_name(),
        'event': event.title,
        'reason': reason,
        'slug': event.slug,
        'settings': settings
    }

    try:
        user.email_user(
            subject='Abakus.no - Du har blitt adminpåmeldt',
            message=message.render(context),
        )
    except SMTPException as e:
        log.error(
            'bump_notification_send_email_error',
            exception=e,
            reg=event.registrations.get(user=user),
            user_id=user.id
        )
        raise self.retry(exc=e, max_retries=3)


@celery_app.task(serializer='pickle', bind=True)
def mail_payment_overdue(self, activity, recipients):
    event = string_to_instance(activity.actor)
    user = User.objects.get(id=recipients[0])
    message = loader.get_template('email/payment_overdue_user_email.html')

    context = {
        'name': user.get_short_name(),
        'event': event.title,
        'slug': event.slug,
        'settings': settings
    }

    try:
        user.email_user(
            subject='Abakus.no - Manglende betaling for arrangement',
            message=message.render(context),
        )
    except SMTPException as e:
        log.error(
            'payment_overdue_user_send_mail_error',
            exception=e,
            reg=event.registrations.get(user=user),
            user_id=user.id
        )
        raise self.retry(exc=e, max_retries=3)