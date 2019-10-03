from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('drfujibot/', views.drfujibot, name='drfujibot'),
    path('timed_messages/', views.timed_messages, name='timed_messages')
]
