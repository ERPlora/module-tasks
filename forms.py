from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Task, TaskSettings

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'task_type', 'priority', 'status', 'due_date', 'completed_at', 'assigned_to', 'customer', 'related_lead', 'duration_minutes', 'result', 'location', 'is_recurring', 'recurrence_rule', 'reminder_before_minutes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-sm w-full', 'rows': 3}),
            'task_type': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'priority': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'status': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'due_date': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'datetime-local'}),
            'completed_at': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'datetime-local'}),
            'assigned_to': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'customer': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'related_lead': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'duration_minutes': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
            'result': forms.Textarea(attrs={'class': 'textarea textarea-sm w-full', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'toggle'}),
            'recurrence_rule': forms.Textarea(attrs={'class': 'textarea textarea-sm w-full', 'rows': 3}),
            'reminder_before_minutes': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
        }

class TaskSettingsForm(forms.ModelForm):
    class Meta:
        model = TaskSettings
        fields = ['default_reminder_minutes', 'auto_create_follow_up', 'working_hours_start', 'working_hours_end']
        widgets = {
            'default_reminder_minutes': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
            'auto_create_follow_up': forms.CheckboxInput(attrs={'class': 'toggle'}),
            'working_hours_start': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'time'}),
            'working_hours_end': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'time'}),
        }

