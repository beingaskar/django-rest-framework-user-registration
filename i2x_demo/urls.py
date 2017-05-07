from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [

    url(r'^admin/', admin.site.urls),

    url(r'^api/accounts/', include('accounts.api.urls')),

    url(r'^api/teams/', include('teams.api.urls')),
]
