from django.urls import path

from . import views

urlpatterns = [
    # This index page was just used for debugging during development. End users will use the admin site.
    #path('', views.index, name='index'),

    # This is the URL used by the IRC component for all chat relay purposes
    path('drfujibot/', views.drfujibot, name='drfujibot'),

    # This is the URL used by the IRC component to poll for timed messages
    path('timed_messages/', views.timed_messages, name='timed_messages'),

    # This is the URL that displays the web console (accessible through the admin site)
    path('console/', views.console, name='console'),

    # This is the URL that completes user access token authorization, and redirects to /save_access_token
    # The extra step is needed because Twitch returns the token in a URL hash fragment, which is only accessible by JavaScript in a web broswer.
    path('authorize/', views.authorize, name='authorize'),

    # This is the URL that saves the access token to the IRC config file
    path('save_access_token/', views.save_access_token, name='save_access_token'),

    # This is the URL that triggers a restart of the DrFujiBot IRC service
    path('restart_drfujibot_service/', views.restart_drfujibot_service, name='restart_drfujibot_service'),
]
