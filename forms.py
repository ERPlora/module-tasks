from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Task, TaskSettings, TYPE_CHOICES, PRIORITY_CHOICES, STATUS_CHOICES


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'task_type', 'priority', 'status',
            'due_date', 'assigned_to', 'customer', 'duration_minutes',
            'result', 'location', 'reminder_before_minutes',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': _('Task title'),
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': 3,
                'placeholder': _('Description (optional)'),
            }),
            'task_type': forms.Select(attrs={
                'class': 'select',
            }),
            'priority': forms.Select(attrs={
                'class': 'select',
            }),
            'status': forms.Select(attrs={
                'class': 'select',
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'input',
                'type': 'datetime-local',
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'input',
                'min': '0',
                'placeholder': _('Duration in minutes'),
            }),
            'result': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': 2,
                'placeholder': _('Call/meeting outcome'),
            }),
            'location': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': _('Meeting location'),
            }),
            'reminder_before_minutes': forms.NumberInput(attrs={
                'class': 'input',
                'min': '0',
                'placeholder': '30',
            }),
        }


class TaskFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': _('Search by title, customer...'),
        }),
    )
    task_type = forms.ChoiceField(
        required=False,
        choices=[('', _('All Types'))] + list(TYPE_CHOICES),
        widget=forms.Select(attrs={
            'class': 'select',
        }),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', _('All Status'))] + list(STATUS_CHOICES),
        widget=forms.Select(attrs={
            'class': 'select',
        }),
    )
    priority = forms.ChoiceField(
        required=False,
        choices=[('', _('All Priorities'))] + list(PRIORITY_CHOICES),
        widget=forms.Select(attrs={
            'class': 'select',
        }),
    )


class TaskSettingsForm(forms.ModelForm):
    class Meta:
        model = TaskSettings
        fields = [
            'default_reminder_minutes', 'auto_create_follow_up',
            'working_hours_start', 'working_hours_end',
        ]
        widgets = {
            'default_reminder_minutes': forms.NumberInput(attrs={
                'class': 'input',
                'min': '0',
                'placeholder': '30',
            }),
            'auto_create_follow_up': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
            'working_hours_start': forms.TimeInput(attrs={
                'class': 'input',
                'type': 'time',
            }),
            'working_hours_end': forms.TimeInput(attrs={
                'class': 'input',
                'type': 'time',
            }),
        }
