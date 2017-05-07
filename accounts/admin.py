from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'email', 'is_active', 'has_email_verified', 'team')

    def email(self, profile):
        return profile.user.email

    def name(self, profile):
        return profile.user.first_name + " " + profile.user.last_name

    def is_active(self, profile):
        return profile.user.is_active

    def team(self, profile):
        return profile.user.team

