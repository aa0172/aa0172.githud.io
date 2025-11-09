from django.contrib import admin
from .models import TrainingSession


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'time', 'gym_name', 'district', 'created_at')
    list_filter = ('district', 'date', 'created_at')
    search_fields = ('user__username', 'gym_name', 'description')
    date_hierarchy = 'date'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')