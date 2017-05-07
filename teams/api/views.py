from django.contrib.sites.shortcuts import get_current_site
from rest_framework import generics, permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

from . import serializers
from teams.models import Team, TeamInvitation


class CreateTeamAPIView(generics.CreateAPIView):
    """
    Endpoint to create a team.

    """

    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )
    serializer_class = serializers.TeamCreateSerializer
    queryset = Team.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'user': request.user}
                                           )
        if serializer.is_valid(raise_exception=True):
            team = serializer.save(owner=request.user)
            team.members.add(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InviteToTeamAPIView(generics.CreateAPIView):
    """
    Endpoint to invite people to a team.

    """

    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )
    serializer_class = serializers.TeamInvitationCreateSerializer
    queryset = TeamInvitation.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={
                                               'user': request.user,
                                               'team_pk': kwargs['pk']
                                           })
        if serializer.is_valid(raise_exception=True):
            email_ids = serializer.validated_data.get('emails')
            self.create_invitations(email_ids=email_ids, invited_by=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create_invitations(self, email_ids, invited_by):
        invitations = [TeamInvitation(email=email_id, invited_by=invited_by)
                       for email_id in email_ids]
        invitations = TeamInvitation.objects.bulk_create(invitations)
        self.send_email_invites(invitations)

    def send_email_invites(self, invitations):
        # Sending email expected to be done asynchronously in production environment.
        for invitation in invitations:
            invitation.send_email_invite(get_current_site(self.request))


