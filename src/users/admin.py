from django.contrib import admin

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
)


admin.site.register(QuizQuestion)
admin.site.register(QuizUserResponse)
admin.site.register(UserProfile)
admin.site.register(ContactMessage)
admin.site.register(FriendList)
admin.site.register(FriendRequest)
admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(ChatMessage)
