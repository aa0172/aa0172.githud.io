from django.contrib import admin
from .models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'interest', 'created_at', 'get_user_count')
    list_filter = ('district', 'interest', 'created_at')
    search_fields = ('name', 'district', 'interest')
    readonly_fields = ('created_at',)

    def get_user_count(self, obj):
        return obj.active_users.count()

    get_user_count.short_description = 'Активных пользователей'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'content_preview', 'timestamp')
    list_filter = ('room', 'timestamp', 'user')
    search_fields = ('user__username', 'content', 'room__name')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    content_preview.short_description = 'Сообщение'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'room')