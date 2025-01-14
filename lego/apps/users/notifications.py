from lego.apps.notifications.constants import PENALTY_CREATION
from lego.apps.notifications.notification import Notification


class PenaltyNotification(Notification):

    name = PENALTY_CREATION

    def generate_mail(self):
        penalty = self.kwargs["penalty"]

        return self._delay_mail(
            to_email=self.user.email,
            context={
                "first_name": self.user.first_name,
                "weight": penalty.weight,
                "event": penalty.source_event.title,
                "reason": penalty.reason,
            },
            subject="Du har fått en ny prikk",
            plain_template="users/email/penalty.txt",
            html_template="users/email/penalty.html",
        )

    def generate_push(self):
        penalty = self.kwargs["penalty"]

        return self._delay_push(
            template="users/push/penalty.txt",
            context={"weight": penalty.weight, "event": penalty.source_event.title},
            instance=penalty,
        )
