from django.contrib import admin

from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task_type', 'priority', 'status', 'created_at']
    search_fields = ['title', 'description', 'task_type', 'priority']
    readonly_fields = ['created_at', 'updated_at']

