from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import (
    UserProfile,
    ContactMessage,
    FriendList,
    FriendRequest,
    Notification,
    Message,
    QuizQuestion,
    QuizUserResponse,
    ChatMessage,
    GlobalChatMessage,
)


class QuizAdmin(TranslationAdmin):
    pass


admin.site.register(QuizQuestion, QuizAdmin)
admin.site.register(QuizUserResponse, QuizAdmin)
admin.site.register(UserProfile)
admin.site.register(ContactMessage)
admin.site.register(FriendList)
admin.site.register(FriendRequest)
admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(ChatMessage)
admin.site.register(GlobalChatMessage)
