from django.contrib import admin

from chatcenter.models import *

admin.site.register(Profile)
admin.site.register(Contact)
admin.site.register(Group)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(GroupMessage)
