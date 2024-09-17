"""
URL configuration for WaveText project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from chatcenter import views

app_name = 'chatcenter'

urlpatterns = [
    path('',views.chatcenter,name='chatcenter'),
    # path('add-contact/', views.add_contact, name='add_contact'),
    path('update-contacts/', views.update_contacts, name='update_contacts'),
    path('history/<str:receiver_username>/', views.chat_history, name='chat_history'),
    path('users/', views.get_users, name='get_users'),
    path('groupchat/create-group/', views.create_group, name='create-group'),
    path('group-chat-history/<str:group_name>/', views.group_chat_history, name='group_chat_history'),
    path('groupchat/',views.group_chat_view,name='groupchat'),
    path('groupchat/chatcenter/send-message/', views.group_send_message, name='send_message'),
    path('notifications/recent-messages/', views.get_recent_messages, name='get_recent_messages'),

]