from rest_framework import serializers

from teams.models import Team
from django.contrib.auth import get_user_model

User = get_user_model()


class TeamCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ['name', 'description']

    def validate(self, data):
        user = self.context.get('user', None)
        if not user:
            raise serializers.ValidationError("User not found.")
        if not Team.objects.has_create_permission(user):
            raise serializers.ValidationError("User not allowed to create team.")
        return data


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ['id', 'name', 'description']


class TeamInvitationCreateSerializer(serializers.Serializer):

    MAXIMUM_EMAILS_ALLOWED = 5

    emails = serializers.ListField(
        write_only=True
    )

    def validate(self, data):
        emails = data.get('emails')
        if len(emails) > self.MAXIMUM_EMAILS_ALLOWED:
            raise serializers.ValidationError("Not more than %s email ID's are allowed." % self.MAXIMUM_EMAILS_ALLOWED)

        team_pk = self.context.get('team_pk')
        user = self.context.get('user')

        try:
            team = Team.objects.get(pk=team_pk)
        except Team.DoesNotExist:
            raise serializers.ValidationError("Team does not exist.")

        if team.has_invite_permissions(user):
            email_ids_existing = User.objects.filter(email__in=emails).values_list('email', flat=True)
            if email_ids_existing:
                raise serializers.ValidationError(
                    "One or more of the email ID's provided is already associated with accounts. (%s)"
                    % ",".join(email_ids_existing))
            return data

        raise serializers.ValidationError("Operation not allowed.")
