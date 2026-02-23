from django.contrib import admin

from .models import Task, TaskSettings


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task_type', 'priority', 'status', 'due_date', 'assigned_to', 'created_at']
    list_filter = ['task_type', 'priority', 'status', 'is_deleted']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'hub_id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    ordering = ['-created_at']


@admin.register(TaskSettings)
class TaskSettingsAdmin(admin.ModelAdmin):
    list_display = ['hub_id', 'default_reminder_minutes', 'auto_create_follow_up']
    readonly_fields = ['id', 'hub_id', 'created_at', 'updated_at']
