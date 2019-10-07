from django.urls import path

from . import views

urlpatterns = [
    # This index page was just used for debugging during development. End users will use the admin site.
    #path('', views.index, name='index'),
    path('drfujibot/', views.drfujibot, name='drfujibot'),
    path('timed_messages/', views.timed_messages, name='timed_messages')
]
