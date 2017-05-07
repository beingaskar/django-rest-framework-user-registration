from django.conf.urls import url


from . import views

urlpatterns = [

    url(r'^create/$',
        views.CreateTeamAPIView.as_view(),
        name='login'),

    url(r'^(?P<pk>[0-9]+)/invite/$',
        views.InviteToTeamAPIView.as_view(),
        name='invite_to_team'),

]
