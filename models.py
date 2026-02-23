from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models.base import HubBaseModel


# ============================================================================
# Choices
# ============================================================================

TYPE_CHOICES = [
    ('task', _('Task')),
    ('call', _('Call')),
    ('meeting', _('Meeting')),
    ('email', _('Email')),
    ('follow_up', _('Follow-up')),
]

PRIORITY_CHOICES = [
    ('low', _('Low')),
    ('medium', _('Medium')),
    ('high', _('High')),
    ('urgent', _('Urgent')),
]

STATUS_CHOICES = [
    ('pending', _('Pending')),
    ('in_progress', _('In Progress')),
    ('completed', _('Completed')),
    ('cancelled', _('Cancelled')),
]

PRIORITY_ORDER = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}


# ============================================================================
# Task
# ============================================================================

class Task(HubBaseModel):
    title = models.CharField(
        max_length=255,
        verbose_name=_('Title'),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description'),
    )
    task_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='task',
        db_index=True,
        verbose_name=_('Type'),
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        db_index=True,
        verbose_name=_('Priority'),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        verbose_name=_('Status'),
    )

    # Dates
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('Due Date'),
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Completed At'),
    )

    # Assignment
    assigned_to = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('Assigned To'),
        help_text=_('UUID of the user assigned to this task'),
    )

    # Customer link
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name=_('Customer'),
    )

    # Generic reference for leads or other entities
    related_lead = models.UUIDField(
        null=True,
        blank=True,
        verbose_name=_('Related Lead'),
        help_text=_('UUID of a related lead or entity'),
    )

    # Call/Meeting specific fields
    duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Duration (minutes)'),
        help_text=_('Duration for calls and meetings'),
    )
    result = models.TextField(
        blank=True,
        verbose_name=_('Result'),
        help_text=_('Outcome of call or meeting'),
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Location'),
        help_text=_('Location for meetings'),
    )

    # Recurrence
    is_recurring = models.BooleanField(
        default=False,
        verbose_name=_('Recurring'),
    )
    recurrence_rule = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_('Recurrence Rule'),
        help_text=_('JSON recurrence configuration'),
    )

    # Reminder
    reminder_before_minutes = models.IntegerField(
        default=30,
        verbose_name=_('Reminder Before (minutes)'),
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'tasks_task'
        ordering = ['-due_date', '-created_at']
        indexes = [
            models.Index(fields=['hub_id', 'status', 'due_date']),
            models.Index(fields=['hub_id', 'task_type']),
            models.Index(fields=['hub_id', 'assigned_to']),
            models.Index(fields=['hub_id', 'priority']),
            models.Index(fields=['hub_id', 'customer']),
        ]

    def __str__(self):
        return self.title

    # --- Properties ---

    @property
    def is_overdue(self):
        """Check if task is overdue (past due date and not completed/cancelled)."""
        if self.due_date and self.status in ('pending', 'in_progress'):
            return timezone.now() > self.due_date
        return False

    @property
    def is_due_today(self):
        """Check if task is due today."""
        if self.due_date:
            now = timezone.now()
            return self.due_date.date() == now.date()
        return False

    @property
    def is_completed(self):
        return self.status == 'completed'

    @property
    def priority_order(self):
        """Numeric priority for sorting (lower = more urgent)."""
        return PRIORITY_ORDER.get(self.priority, 2)

    @property
    def type_icon(self):
        """Return an icon name for the task type."""
        icons = {
            'task': 'checkbox-outline',
            'call': 'call-outline',
            'meeting': 'people-outline',
            'email': 'mail-outline',
            'follow_up': 'arrow-redo-outline',
        }
        return icons.get(self.task_type, 'checkbox-outline')

    @property
    def priority_color(self):
        """Return a color class for the priority level."""
        colors = {
            'low': 'success',
            'medium': 'primary',
            'high': 'warning',
            'urgent': 'error',
        }
        return colors.get(self.priority, 'primary')

    @property
    def status_color(self):
        """Return a color class for the status."""
        colors = {
            'pending': 'warning',
            'in_progress': 'primary',
            'completed': 'success',
            'cancelled': '',
        }
        return colors.get(self.status, '')

    @property
    def due_date_color(self):
        """Return a color class based on due date proximity."""
        if not self.due_date:
            return ''
        if self.status in ('completed', 'cancelled'):
            return 'success' if self.status == 'completed' else ''
        if self.is_overdue:
            return 'error'
        if self.is_due_today:
            return 'warning'
        return ''

    @property
    def customer_name(self):
        """Return customer name or empty string."""
        if self.customer:
            return self.customer.name
        return ''

    # --- Methods ---

    def mark_complete(self):
        """Mark task as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

    def mark_reopen(self):
        """Reopen a completed/cancelled task."""
        self.status = 'pending'
        self.completed_at = None
        self.save(update_fields=['status', 'completed_at', 'updated_at'])


# ============================================================================
# Task Settings
# ============================================================================

class TaskSettings(HubBaseModel):
    default_reminder_minutes = models.IntegerField(
        default=30,
        verbose_name=_('Default Reminder (minutes)'),
        help_text=_('Default reminder time before task due date'),
    )
    auto_create_follow_up = models.BooleanField(
        default=False,
        verbose_name=_('Auto-create Follow-up'),
        help_text=_('Automatically create a follow-up task after completing a call or meeting'),
    )
    working_hours_start = models.TimeField(
        default='09:00',
        verbose_name=_('Working Hours Start'),
    )
    working_hours_end = models.TimeField(
        default='18:00',
        verbose_name=_('Working Hours End'),
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'tasks_settings'
        verbose_name = _('Task Settings')
        verbose_name_plural = _('Task Settings')

    def __str__(self):
        return f'Task Settings ({self.hub_id})'

    @classmethod
    def get_for_hub(cls, hub_id):
        """Get or create settings for a hub."""
        settings, _ = cls.objects.get_or_create(hub_id=hub_id)
        return settings
