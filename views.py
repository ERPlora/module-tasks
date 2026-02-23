"""
Tasks Module Views

Task, call, meeting and activity management: dashboard, list, calendar,
create, update, delete, complete/reopen, bulk actions, and settings.
"""
import json
from datetime import timedelta

from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render as django_render
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.accounts.decorators import login_required
from apps.core.htmx import htmx_view
from apps.modules_runtime.navigation import with_module_nav

from .models import Task, TaskSettings, TYPE_CHOICES, PRIORITY_CHOICES, STATUS_CHOICES


# ============================================================================
# Constants
# ============================================================================

TASK_SORT_FIELDS = {
    'title': 'title',
    'due_date': 'due_date',
    'priority': 'priority',
    'status': 'status',
    'type': 'task_type',
    'created': 'created_at',
}

PER_PAGE_CHOICES = [10, 25, 50, 100]


def _hub_id(request):
    return request.session.get('hub_id')


def _get_customers_for_hub(hub_id):
    """Safely load customers list for dropdowns."""
    try:
        from customers.models import Customer
        return Customer.objects.filter(
            hub_id=hub_id, is_deleted=False, is_active=True,
        ).order_by('name')
    except Exception:
        return []


def _render_task_list(request, hub_id, per_page=10):
    """Render the tasks list partial after a mutation."""
    tasks = Task.objects.filter(hub_id=hub_id, is_deleted=False).order_by('-due_date', '-created_at')
    paginator = Paginator(tasks, per_page)
    page_obj = paginator.get_page(1)
    return django_render(request, 'tasks/partials/tasks_list.html', {
        'tasks': page_obj,
        'page_obj': page_obj,
        'search_query': '',
        'sort_field': 'due_date',
        'sort_dir': 'desc',
        'type_filter': '',
        'status_filter': '',
        'priority_filter': '',
        'per_page': per_page,
    })


# ============================================================================
# Dashboard
# ============================================================================

@login_required
@with_module_nav('tasks', 'dashboard')
@htmx_view('tasks/pages/dashboard.html', 'tasks/partials/dashboard_content.html')
def dashboard(request):
    """Tasks dashboard with stats and upcoming tasks."""
    hub = _hub_id(request)
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    week_start = today_start - timedelta(days=today_start.weekday())
    week_end = week_start + timedelta(days=7)
    next_7_days = today_start + timedelta(days=7)

    base_qs = Task.objects.filter(hub_id=hub, is_deleted=False)

    # Stats
    due_today = base_qs.filter(
        due_date__gte=today_start, due_date__lt=today_end,
    ).exclude(status__in=['completed', 'cancelled']).count()

    overdue = base_qs.filter(
        due_date__lt=now, status__in=['pending', 'in_progress'],
    ).count()

    completed_this_week = base_qs.filter(
        status='completed', completed_at__gte=week_start, completed_at__lt=week_end,
    ).count()

    calls_today = base_qs.filter(
        task_type='call', due_date__gte=today_start, due_date__lt=today_end,
    ).exclude(status__in=['completed', 'cancelled']).count()

    meetings_today = base_qs.filter(
        task_type='meeting', due_date__gte=today_start, due_date__lt=today_end,
    ).exclude(status__in=['completed', 'cancelled']).count()

    # Counts by type
    type_counts = dict(
        base_qs.exclude(status__in=['completed', 'cancelled'])
        .values_list('task_type')
        .annotate(count=Count('id'))
        .values_list('task_type', 'count')
    )

    # Upcoming tasks (next 7 days, not completed/cancelled)
    upcoming_tasks = base_qs.filter(
        due_date__gte=today_start, due_date__lt=next_7_days,
    ).exclude(
        status__in=['completed', 'cancelled'],
    ).select_related('customer').order_by('due_date')[:15]

    # Overdue tasks list
    overdue_tasks = base_qs.filter(
        due_date__lt=now, status__in=['pending', 'in_progress'],
    ).select_related('customer').order_by('due_date')[:10]

    return {
        'due_today': due_today,
        'overdue': overdue,
        'completed_this_week': completed_this_week,
        'calls_today': calls_today,
        'meetings_today': meetings_today,
        'type_counts': type_counts,
        'upcoming_tasks': upcoming_tasks,
        'overdue_tasks': overdue_tasks,
        'now': now,
    }


# ============================================================================
# Task List (Datatable)
# ============================================================================

@login_required
@with_module_nav('tasks', 'list')
@htmx_view('tasks/pages/list.html', 'tasks/partials/tasks_content.html')
def task_list(request):
    """Tasks list with search, sort, filter, pagination."""
    hub = _hub_id(request)
    search_query = request.GET.get('q', '').strip()
    sort_field = request.GET.get('sort', 'due_date')
    sort_dir = request.GET.get('dir', 'desc')
    type_filter = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    per_page = int(request.GET.get('per_page', 10))
    if per_page not in PER_PAGE_CHOICES:
        per_page = 10

    tasks = Task.objects.filter(hub_id=hub, is_deleted=False).select_related('customer')

    # Type filter
    if type_filter:
        tasks = tasks.filter(task_type=type_filter)

    # Status filter
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # Priority filter
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    # Search
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )

    # Sort
    order_by = TASK_SORT_FIELDS.get(sort_field, 'due_date')
    if sort_dir == 'desc':
        order_by = f'-{order_by}'
    tasks = tasks.order_by(order_by)

    # Pagination
    paginator = Paginator(tasks, per_page)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'tasks': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_field': sort_field,
        'sort_dir': sort_dir,
        'type_filter': type_filter,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'per_page': per_page,
        'type_choices': TYPE_CHOICES,
        'status_choices': STATUS_CHOICES,
        'priority_choices': PRIORITY_CHOICES,
        'now': timezone.now(),
    }

    # HTMX partial: swap only datatable body
    if request.htmx and request.htmx.target == 'datatable-body':
        return django_render(request, 'tasks/partials/tasks_list.html', context)

    context.update({
        'current_section': 'tasks',
        'page_title': str(_('Tasks')),
    })
    return context


# ============================================================================
# Task CRUD
# ============================================================================

@login_required
def task_add(request):
    """Add task — renders in side panel via HTMX."""
    hub = _hub_id(request)
    customers = _get_customers_for_hub(hub)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if not title:
            messages.error(request, _('Title is required'))
            return django_render(request, 'tasks/partials/panel_task_add.html', {
                'customers': customers,
                'type_choices': TYPE_CHOICES,
                'priority_choices': PRIORITY_CHOICES,
            })

        due_date_str = request.POST.get('due_date', '').strip()
        due_date = None
        if due_date_str:
            try:
                from django.utils.dateparse import parse_datetime
                due_date = parse_datetime(due_date_str)
                if due_date and timezone.is_naive(due_date):
                    due_date = timezone.make_aware(due_date)
            except (ValueError, TypeError):
                pass

        customer_id = request.POST.get('customer', '').strip() or None

        duration = request.POST.get('duration_minutes', '').strip()
        duration_minutes = int(duration) if duration else None

        reminder = request.POST.get('reminder_before_minutes', '').strip()
        reminder_minutes = int(reminder) if reminder else 30

        Task.objects.create(
            hub_id=hub,
            title=title,
            description=request.POST.get('description', '').strip(),
            task_type=request.POST.get('task_type', 'task'),
            priority=request.POST.get('priority', 'medium'),
            due_date=due_date,
            customer_id=customer_id,
            duration_minutes=duration_minutes,
            location=request.POST.get('location', '').strip(),
            reminder_before_minutes=reminder_minutes,
            created_by=getattr(request.user, 'id', None),
        )

        messages.success(request, _('Task created successfully'))
        return _render_task_list(request, hub)

    return django_render(request, 'tasks/partials/panel_task_add.html', {
        'customers': customers,
        'type_choices': TYPE_CHOICES,
        'priority_choices': PRIORITY_CHOICES,
    })


@login_required
def task_edit(request, task_id):
    """Edit task — renders in side panel via HTMX."""
    hub = _hub_id(request)
    task = get_object_or_404(Task, id=task_id, hub_id=hub, is_deleted=False)
    customers = _get_customers_for_hub(hub)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if not title:
            messages.error(request, _('Title is required'))
            return django_render(request, 'tasks/partials/panel_task_edit.html', {
                'task': task,
                'customers': customers,
                'type_choices': TYPE_CHOICES,
                'priority_choices': PRIORITY_CHOICES,
                'status_choices': STATUS_CHOICES,
            })

        due_date_str = request.POST.get('due_date', '').strip()
        due_date = None
        if due_date_str:
            try:
                from django.utils.dateparse import parse_datetime
                due_date = parse_datetime(due_date_str)
                if due_date and timezone.is_naive(due_date):
                    due_date = timezone.make_aware(due_date)
            except (ValueError, TypeError):
                pass

        customer_id = request.POST.get('customer', '').strip() or None

        duration = request.POST.get('duration_minutes', '').strip()
        duration_minutes = int(duration) if duration else None

        reminder = request.POST.get('reminder_before_minutes', '').strip()
        reminder_minutes = int(reminder) if reminder else 30

        task.title = title
        task.description = request.POST.get('description', '').strip()
        task.task_type = request.POST.get('task_type', 'task')
        task.priority = request.POST.get('priority', 'medium')
        task.status = request.POST.get('status', task.status)
        task.due_date = due_date
        task.customer_id = customer_id
        task.duration_minutes = duration_minutes
        task.location = request.POST.get('location', '').strip()
        task.result = request.POST.get('result', '').strip()
        task.reminder_before_minutes = reminder_minutes
        task.updated_by = getattr(request.user, 'id', None)
        task.save()

        messages.success(request, _('Task updated successfully'))
        return _render_task_list(request, hub)

    # Format due_date for datetime-local input
    due_date_value = ''
    if task.due_date:
        local_dt = timezone.localtime(task.due_date)
        due_date_value = local_dt.strftime('%Y-%m-%dT%H:%M')

    return django_render(request, 'tasks/partials/panel_task_edit.html', {
        'task': task,
        'customers': customers,
        'type_choices': TYPE_CHOICES,
        'priority_choices': PRIORITY_CHOICES,
        'status_choices': STATUS_CHOICES,
        'due_date_value': due_date_value,
    })


@login_required
def task_detail(request, task_id):
    """Task detail — renders in side panel via HTMX."""
    hub = _hub_id(request)
    task = get_object_or_404(
        Task.objects.select_related('customer'),
        id=task_id, hub_id=hub, is_deleted=False,
    )
    return django_render(request, 'tasks/partials/task_detail.html', {
        'task': task,
        'now': timezone.now(),
    })


@login_required
@require_POST
def task_delete(request, task_id):
    """Soft delete task."""
    hub = _hub_id(request)
    task = get_object_or_404(Task, id=task_id, hub_id=hub, is_deleted=False)
    task.is_deleted = True
    task.deleted_at = timezone.now()
    task.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    messages.success(request, _('Task deleted successfully'))
    return _render_task_list(request, hub)


@login_required
@require_POST
def task_complete(request, task_id):
    """Mark task as completed."""
    hub = _hub_id(request)
    task = get_object_or_404(Task, id=task_id, hub_id=hub, is_deleted=False)
    task.mark_complete()

    # Auto-create follow-up if enabled
    try:
        settings = TaskSettings.get_for_hub(hub)
        if settings.auto_create_follow_up and task.task_type in ('call', 'meeting'):
            follow_up_date = timezone.now() + timedelta(days=3)
            Task.objects.create(
                hub_id=hub,
                title=_('Follow-up: %(title)s') % {'title': task.title},
                task_type='follow_up',
                priority='medium',
                due_date=follow_up_date,
                customer=task.customer,
                reminder_before_minutes=settings.default_reminder_minutes,
                created_by=getattr(request.user, 'id', None),
            )
    except Exception:
        pass

    messages.success(request, _('Task completed'))
    return _render_task_list(request, hub)


@login_required
@require_POST
def task_reopen(request, task_id):
    """Reopen a completed/cancelled task."""
    hub = _hub_id(request)
    task = get_object_or_404(Task, id=task_id, hub_id=hub, is_deleted=False)
    task.mark_reopen()

    messages.success(request, _('Task reopened'))
    return _render_task_list(request, hub)


@login_required
@require_POST
def task_bulk_action(request):
    """Bulk complete/delete tasks."""
    hub = _hub_id(request)
    ids_str = request.POST.get('ids', '')
    action = request.POST.get('action', '')

    if not ids_str or not action:
        return _render_task_list(request, hub)

    ids = [uid.strip() for uid in ids_str.split(',') if uid.strip()]
    tasks = Task.objects.filter(hub_id=hub, id__in=ids, is_deleted=False)
    count = tasks.count()

    if action == 'complete':
        now = timezone.now()
        tasks.update(status='completed', completed_at=now)
        messages.success(request, _('%(count)d tasks completed') % {'count': count})
    elif action == 'delete':
        tasks.update(is_deleted=True, deleted_at=timezone.now())
        messages.success(request, _('%(count)d tasks deleted') % {'count': count})

    return _render_task_list(request, hub)


# ============================================================================
# Calendar
# ============================================================================

@login_required
@with_module_nav('tasks', 'calendar')
@htmx_view('tasks/pages/calendar.html', 'tasks/partials/calendar_content.html')
def calendar_view(request):
    """Calendar view for tasks."""
    hub = _hub_id(request)
    now = timezone.now()
    return {
        'current_year': now.year,
        'current_month': now.month,
        'today': now.strftime('%Y-%m-%d'),
    }


@login_required
@require_http_methods(["GET"])
def calendar_data_api(request):
    """API endpoint returning tasks for a given month/year as JSON."""
    hub = _hub_id(request)

    try:
        year = int(request.GET.get('year', timezone.now().year))
        month = int(request.GET.get('month', timezone.now().month))
    except (ValueError, TypeError):
        year = timezone.now().year
        month = timezone.now().month

    # Get first and last day of month (with buffer for calendar display)
    from calendar import monthrange
    _, last_day = monthrange(year, month)

    month_start = timezone.make_aware(
        timezone.datetime(year, month, 1, 0, 0, 0)
    )
    month_end = timezone.make_aware(
        timezone.datetime(year, month, last_day, 23, 59, 59)
    )

    tasks = Task.objects.filter(
        hub_id=hub,
        is_deleted=False,
        due_date__gte=month_start,
        due_date__lte=month_end,
    ).select_related('customer').order_by('due_date')

    # Group tasks by date
    tasks_by_date = {}
    for task in tasks:
        date_key = timezone.localtime(task.due_date).strftime('%Y-%m-%d')
        if date_key not in tasks_by_date:
            tasks_by_date[date_key] = []
        tasks_by_date[date_key].append({
            'id': str(task.id),
            'title': task.title,
            'type': task.task_type,
            'type_icon': task.type_icon,
            'priority': task.priority,
            'priority_color': task.priority_color,
            'status': task.status,
            'status_color': task.status_color,
            'due_time': timezone.localtime(task.due_date).strftime('%H:%M'),
            'customer_name': task.customer_name,
            'is_completed': task.is_completed,
        })

    return JsonResponse({
        'success': True,
        'year': year,
        'month': month,
        'tasks': tasks_by_date,
    })


# ============================================================================
# Settings
# ============================================================================

@login_required
@with_module_nav('tasks', 'settings')
@htmx_view('tasks/pages/settings.html', 'tasks/partials/settings_content.html')
def settings_view(request):
    """Task module settings."""
    hub = _hub_id(request)
    settings = TaskSettings.get_for_hub(hub)

    if request.method == 'POST':
        reminder = request.POST.get('default_reminder_minutes', '30').strip()
        settings.default_reminder_minutes = int(reminder) if reminder else 30
        settings.auto_create_follow_up = request.POST.get('auto_create_follow_up') == 'on'

        start_time = request.POST.get('working_hours_start', '').strip()
        end_time = request.POST.get('working_hours_end', '').strip()
        if start_time:
            settings.working_hours_start = start_time
        if end_time:
            settings.working_hours_end = end_time

        settings.save()
        messages.success(request, _('Settings saved successfully'))

    # Stats
    base_qs = Task.objects.filter(hub_id=hub, is_deleted=False)
    total_tasks = base_qs.count()
    total_completed = base_qs.filter(status='completed').count()
    total_pending = base_qs.filter(status__in=['pending', 'in_progress']).count()

    return {
        'settings': settings,
        'total_tasks': total_tasks,
        'total_completed': total_completed,
        'total_pending': total_pending,
    }
