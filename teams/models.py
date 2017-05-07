import base64
import uuid
import datetime
from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.utils import timezone

from base import models as base_models

User = get_user_model()


class TeamManager(models.Manager):
    """
    Custom manager for Team model.

    The methods defined here provide shortcuts on a team level
    such as checking if user has permission to create team.

    """

    def has_create_permission(self, user):
        """
        Logic for user permissions to create a team.
        Returns a boolean ``True`` if user is not in a team, otherwise ``False``.

        """

        return False if user.team.all().exists() else True


class Team(base_models.TimeStampedModel):
    """
    A model that stores the team related data such as name,
    description, owner, members.

    """

    name = models.CharField(
        max_length=255
    )

    description = models.TextField()

    owner = models.ForeignKey(
        User,
        related_name='owned_teams',
        null=True,
        blank=False,
        on_delete=models.SET_NULL
    )

    members = models.ManyToManyField(
        User,
        related_name='team'
    )

    objects = TeamManager()

    class Meta:
        verbose_name = u'team'
        verbose_name_plural = u'teams'

    def __str__(self):
        return str(self.name)

    def has_invite_permissions(self, user):
        """
        Logic to check whether give user has invite permissions on team.
        Returns a boolean ``True`` if user is owner of team, otherwise ``False``.

        """

        if self.owner == user:
            return True
        return False


def generate_invite_code():
    """
    Generates a referral code for inviting people to team.

    """

    return base64.urlsafe_b64encode(uuid.uuid1().bytes.encode("base64").rstrip())[:25]


class TeamInvitationManager(models.Manager):
    """
    Custom manager for the ``TeamInvitation`` model.

    The methods defined here provide shortcuts for validating
    invite code, accept/ decline invitations etc.

    """

    def validate_code(self, email, value):
        """
        Validates the invite code with the email address.
        Returns the ``TeamInvitation`` on success, otherwise ``None``.

        """

        try:
            invitation = self.get(
                email=email, code=value, status=TeamInvitation.PENDING
            )
        except ObjectDoesNotExist:
            return None
        return invitation

    def accept_invitation(self, invitation):
        """
        Accepts the invitation.
        Returns a boolean ``True`` on success, otherwise ``False``.

        """

        if invitation.status == TeamInvitation.PENDING:
            invitation.status = TeamInvitation.ACCEPTED
            invitation.save()
            return True
        return False

    def decline_pending_invitations(self, email_ids):
        """
        Declines all pending invitations for given email addresses.

        """

        self.filter(
            email__in=email_ids,
            status=TeamInvitation.PENDING
        ).update(
            status=TeamInvitation.DECLINED
        )

    def expired(self):
        """
        Returns the list of expired ``TeamInvitation``

        """

        now = timezone.now() if settings.USE_TZ else datetime.datetime.now()

        return self.filter(
            models.Q(status=TeamInvitation.PENDING)
        ).filter(
            timestamp_created__lt=now - datetime.timedelta(
                getattr(settings, 'INVITATION_VALIDITY_DAYS', 7)
            )
        )

    def expire_invitations(self):
        """
        Deletes all the instances of expired ``TeamInvitation``.

        """

        invitations = self.expired()
        invitations.update(status=TeamInvitation.EXPIRED)


class TeamInvitation(base_models.TimeStampedModel):
    """
    A model that stores the team invitation related data such as
    email, invite_code, invited_by, status etc.
    """

    PENDING = 0
    ACCEPTED = 1
    DECLINED = 2
    EXPIRED = 4

    STATUS_CHOICES = (
        (PENDING, 'PENDING'),
        (ACCEPTED, 'ACCEPTED'),
        (DECLINED, 'DECLINED'),
        (EXPIRED, 'EXPIRED'),
        )

    invited_by = models.ForeignKey(
        User,
        related_name='invitations_sent',
        null=True,
        blank=False,
        on_delete=models.SET_NULL
    )

    email = models.EmailField()

    code = models.CharField(
        max_length=25,
        default=generate_invite_code
    )

    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=0
    )

    objects = TeamInvitationManager()

    class Meta:
        unique_together = ('email', 'code',)
        verbose_name = u'team invitation'
        verbose_name_plural = u'team invitations'

    def __str__(self):
        return "To : %s | From %s" % (self.email, self.invited_by)

    def send_email_invite(self, site):
        """
        Send a team invitation email to person referred by ``email``
        """

        context = {
            'site': site,
            'site_name': getattr(settings, 'SITE_NAME', None),
            'code': self.code,
            'invited_by': self.invited_by,
            'team': self.invited_by.team.last(),
            'email': self.email
        }

        subject = render_to_string(
            'invitation_team/invitation_team_subject.txt', context
        )

        subject = ''.join(subject.splitlines())

        message = render_to_string(
            'invitation_team/invitation_team_content.txt', context
        )

        msg = EmailMultiAlternatives(subject, "", settings.DEFAULT_FROM_EMAIL, [self.email])
        msg.attach_alternative(message, "text/html")
        msg.send()
