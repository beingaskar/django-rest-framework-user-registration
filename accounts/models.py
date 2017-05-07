import re
import hashlib
import datetime

from django.conf import settings
from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator

from base import utils as base_utils
from base import models as base_models

User = get_user_model()

token_generator = default_token_generator

SHA1_RE = re.compile('^[a-f0-9]{40}$')


class Verification(models.Model):
    """
    An abstract model that provides fields related to user
    verification.

    """

    has_email_verified = models.BooleanField(
        default=False
    )

    class Meta:
        abstract = True


class UserProfileRegistrationManager(models.Manager):
    """
    Custom manager for ``UserProfile`` model.

    The methods defined here provide shortcuts for user profile creation
    and activation (including generation and emailing of activation
    keys), and for cleaning out expired inactive accounts.

    """

    @transaction.atomic
    def create_user_profile(self, data, is_active=False, site=None, send_email=True):
        """
        Create a new user and its associated ``UserProfile``.
        Also, send user account activation (verification) email.

        """

        password = data.pop('password')
        user = User(**data)
        user.is_active = is_active
        user.set_password(password)
        user.save()

        user_profile = self.create_profile(user)

        if send_email:
            user_profile.send_activation_email(site)  # To be made asynchronous in production

        return user

    def create_profile(self, user):
        """
        Create UserProfile for give user.
        Returns created user profile on success.

        """

        username = str(getattr(user, User.USERNAME_FIELD))
        hash_input = (get_random_string(5) + username).encode('utf-8')
        verification_key = hashlib.sha1(hash_input).hexdigest()

        profile = self.create(
            user=user,
            verification_key=verification_key
        )

        return profile

    def activate_user(self, verification_key):
        """
        Validate an verification key and activate the corresponding user
        if valid. Returns the user account on success, ``None`` on
        failure.

        """

        if SHA1_RE.search(verification_key.lower()):
            try:
                user_profile = self.get(verification_key=verification_key)
            except ObjectDoesNotExist:
                return None
            if not user_profile.verification_key_expired():
                user = user_profile.user
                user.is_active = True
                user.save()
                user_profile.verification_key = UserProfile.ACTIVATED
                user_profile.has_email_verified = True
                user_profile.save()
                return user
        return None

    def expired(self):
        """
        Returns the list of inactive expired users.

        """

        now = timezone.now() if settings.USE_TZ else datetime.datetime.now()

        return self.exclude(
            models.Q(user__is_active=True) |
            models.Q(verification_key=UserProfile.ACTIVATED)
            ).filter(
                user__date_joined__lt=now - datetime.timedelta(
                    getattr(settings, 'VERIFICATION_KEY_EXPIRY_DAYS', 4)
                )
            )

    @transaction.atomic
    def delete_expired_users(self):
        """
        Deletes all instances of inactive expired users.

        """

        for profile in self.expired():
            user = profile.user
            profile.delete()
            user.delete()


class UserProfile(base_models.TimeStampedModel, Verification):
    """
    A model for user profile that also stores verification key.
    Any methods under User will reside here.

    """

    ACTIVATED = "ALREADY ACTIVATED"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL
    )

    verification_key = models.CharField(
        max_length=40
    )

    objects = UserProfileRegistrationManager()

    class Meta:
        verbose_name = u'user profile'
        verbose_name_plural = u'user profiles'

    def __str__(self):
        return str(self.user)

    def verification_key_expired(self):
        """
        Validate whether the user's verification key has been expired
        or not. Returns ``True`` if expired, otherwise ``False``.

        """

        expiration_date = datetime.timedelta(
            days=getattr(settings, 'VERIFICATION_KEY_EXPIRY_DAYS', 4)
        )

        return self.verification_key == self.ACTIVATED or \
               (self.user.date_joined + expiration_date <= timezone.now())

    def send_activation_email(self, site):
        """
        Sends an activation (verification) email to user.
        """

        context = {
            'verification_key': self.verification_key,
            'expiration_days': getattr(settings, 'VERIFICATION_KEY_EXPIRY_DAYS', 4),
            'user': self.user,
            'site': site,
            'site_name': getattr(settings, 'SITE_NAME', None)
        }

        subject = render_to_string(
            'registration/activation_email_subject.txt', context
        )

        subject = ''.join(subject.splitlines())

        message = render_to_string(
            'registration/activation_email_content.txt', context
        )

        msg = EmailMultiAlternatives(subject, "", settings.DEFAULT_FROM_EMAIL, [self.user.email])
        msg.attach_alternative(message, "text/html")
        msg.send()

    def send_password_reset_email(self, site):
        """
        Sends a password reset email to user.

        """

        context = {
            'email': self.user.email,
            'site': site,
            'site_name': getattr(settings, 'SITE_NAME', None),
            'uid': base_utils.base36encode(self.user.pk),
            'user': self.user,
            'token': token_generator.make_token(self.user)
        }
        subject = render_to_string(
            'password_reset/password_reset_email_subject.txt', context
        )

        subject = ''.join(subject.splitlines())

        message = render_to_string(
            'password_reset/password_reset_email_content.txt', context
        )

        msg = EmailMultiAlternatives(subject, "", settings.DEFAULT_FROM_EMAIL, [self.user.email])
        msg.attach_alternative(message, "text/html")
        msg.send()
