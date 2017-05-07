from django.contrib import admin

from .models import Team, TeamInvitation


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'description', 'owner')


@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):

    list_display = ('id', 'email', 'invited_by', 'status')

