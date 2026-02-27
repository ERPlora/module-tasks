"""
Tasks Module Views
"""
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, render as django_render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from apps.accounts.decorators import login_required, permission_required
from apps.core.htmx import htmx_view
from apps.core.services import export_to_csv, export_to_excel
from apps.modules_runtime.navigation import with_module_nav

from .models import Task, TaskSettings

PER_PAGE_CHOICES = [10, 25, 50, 100]


# ======================================================================
# Dashboard
# ======================================================================

@login_required
@with_module_nav('tasks', 'dashboard')
@htmx_view('tasks/pages/index.html', 'tasks/partials/dashboard_content.html')
def dashboard(request):
    hub_id = request.session.get('hub_id')
    return {
        'total_tasks': Task.objects.filter(hub_id=hub_id, is_deleted=False).count(),
    }


# ======================================================================
# Task
# ======================================================================

TASK_SORT_FIELDS = {
    'title': 'title',
    'task_type': 'task_type',
    'priority': 'priority',
    'status': 'status',
    'customer': 'customer',
    'is_recurring': 'is_recurring',
    'created_at': 'created_at',
}

def _build_tasks_context(hub_id, per_page=10):
    qs = Task.objects.filter(hub_id=hub_id, is_deleted=False).order_by('title')
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(1)
    return {
        'tasks': page_obj,
        'page_obj': page_obj,
        'search_query': '',
        'sort_field': 'title',
        'sort_dir': 'asc',
        'current_view': 'table',
        'per_page': per_page,
    }

def _render_tasks_list(request, hub_id, per_page=10):
    ctx = _build_tasks_context(hub_id, per_page)
    return django_render(request, 'tasks/partials/tasks_list.html', ctx)

@login_required
@with_module_nav('tasks', 'list')
@htmx_view('tasks/pages/tasks.html', 'tasks/partials/tasks_content.html')
def tasks_list(request):
    hub_id = request.session.get('hub_id')
    search_query = request.GET.get('q', '').strip()
    sort_field = request.GET.get('sort', 'title')
    sort_dir = request.GET.get('dir', 'asc')
    page_number = request.GET.get('page', 1)
    current_view = request.GET.get('view', 'table')
    per_page = int(request.GET.get('per_page', 10))
    if per_page not in PER_PAGE_CHOICES:
        per_page = 10

    qs = Task.objects.filter(hub_id=hub_id, is_deleted=False)

    if search_query:
        qs = qs.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query) | Q(task_type__icontains=search_query) | Q(priority__icontains=search_query))

    order_by = TASK_SORT_FIELDS.get(sort_field, 'title')
    if sort_dir == 'desc':
        order_by = f'-{order_by}'
    qs = qs.order_by(order_by)

    export_format = request.GET.get('export')
    if export_format in ('csv', 'excel'):
        fields = ['title', 'task_type', 'priority', 'status', 'customer', 'is_recurring']
        headers = ['Title', 'Task Type', 'Priority', 'Status', 'customers.Customer', 'Is Recurring']
        if export_format == 'csv':
            return export_to_csv(qs, fields=fields, headers=headers, filename='tasks.csv')
        return export_to_excel(qs, fields=fields, headers=headers, filename='tasks.xlsx')

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page_number)

    if request.htmx and request.htmx.target == 'datatable-body':
        return django_render(request, 'tasks/partials/tasks_list.html', {
            'tasks': page_obj, 'page_obj': page_obj,
            'search_query': search_query, 'sort_field': sort_field,
            'sort_dir': sort_dir, 'current_view': current_view, 'per_page': per_page,
        })

    return {
        'tasks': page_obj, 'page_obj': page_obj,
        'search_query': search_query, 'sort_field': sort_field,
        'sort_dir': sort_dir, 'current_view': current_view, 'per_page': per_page,
    }

@login_required
def task_add(request):
    hub_id = request.session.get('hub_id')
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        task_type = request.POST.get('task_type', '').strip()
        priority = request.POST.get('priority', '').strip()
        status = request.POST.get('status', '').strip()
        due_date = request.POST.get('due_date') or None
        completed_at = request.POST.get('completed_at') or None
        assigned_to = request.POST.get('assigned_to', '').strip()
        related_lead = request.POST.get('related_lead', '').strip()
        duration_minutes = int(request.POST.get('duration_minutes', 0) or 0)
        result = request.POST.get('result', '').strip()
        location = request.POST.get('location', '').strip()
        is_recurring = request.POST.get('is_recurring') == 'on'
        recurrence_rule = request.POST.get('recurrence_rule', '').strip()
        reminder_before_minutes = int(request.POST.get('reminder_before_minutes', 0) or 0)
        obj = Task(hub_id=hub_id)
        obj.title = title
        obj.description = description
        obj.task_type = task_type
        obj.priority = priority
        obj.status = status
        obj.due_date = due_date
        obj.completed_at = completed_at
        obj.assigned_to = assigned_to
        obj.related_lead = related_lead
        obj.duration_minutes = duration_minutes
        obj.result = result
        obj.location = location
        obj.is_recurring = is_recurring
        obj.recurrence_rule = recurrence_rule
        obj.reminder_before_minutes = reminder_before_minutes
        obj.save()
        return _render_tasks_list(request, hub_id)
    return django_render(request, 'tasks/partials/panel_task_add.html', {})

@login_required
def task_edit(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(Task, pk=pk, hub_id=hub_id, is_deleted=False)
    if request.method == 'POST':
        obj.title = request.POST.get('title', '').strip()
        obj.description = request.POST.get('description', '').strip()
        obj.task_type = request.POST.get('task_type', '').strip()
        obj.priority = request.POST.get('priority', '').strip()
        obj.status = request.POST.get('status', '').strip()
        obj.due_date = request.POST.get('due_date') or None
        obj.completed_at = request.POST.get('completed_at') or None
        obj.assigned_to = request.POST.get('assigned_to', '').strip()
        obj.related_lead = request.POST.get('related_lead', '').strip()
        obj.duration_minutes = int(request.POST.get('duration_minutes', 0) or 0)
        obj.result = request.POST.get('result', '').strip()
        obj.location = request.POST.get('location', '').strip()
        obj.is_recurring = request.POST.get('is_recurring') == 'on'
        obj.recurrence_rule = request.POST.get('recurrence_rule', '').strip()
        obj.reminder_before_minutes = int(request.POST.get('reminder_before_minutes', 0) or 0)
        obj.save()
        return _render_tasks_list(request, hub_id)
    return django_render(request, 'tasks/partials/panel_task_edit.html', {'obj': obj})

@login_required
@require_POST
def task_delete(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(Task, pk=pk, hub_id=hub_id, is_deleted=False)
    obj.is_deleted = True
    obj.deleted_at = timezone.now()
    obj.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
    return _render_tasks_list(request, hub_id)

@login_required
@require_POST
def tasks_bulk_action(request):
    hub_id = request.session.get('hub_id')
    ids = [i.strip() for i in request.POST.get('ids', '').split(',') if i.strip()]
    action = request.POST.get('action', '')
    qs = Task.objects.filter(hub_id=hub_id, is_deleted=False, id__in=ids)
    if action == 'delete':
        qs.update(is_deleted=True, deleted_at=timezone.now())
    return _render_tasks_list(request, hub_id)


# ======================================================================
# Settings
# ======================================================================

@login_required
@permission_required('tasks.manage_settings')
@with_module_nav('tasks', 'settings')
@htmx_view('tasks/pages/settings.html', 'tasks/partials/settings_content.html')
def settings_view(request):
    hub_id = request.session.get('hub_id')
    config, _ = TaskSettings.objects.get_or_create(hub_id=hub_id)
    if request.method == 'POST':
        config.default_reminder_minutes = request.POST.get('default_reminder_minutes', config.default_reminder_minutes)
        config.auto_create_follow_up = request.POST.get('auto_create_follow_up') == 'on'
        config.working_hours_start = request.POST.get('working_hours_start', '').strip()
        config.working_hours_end = request.POST.get('working_hours_end', '').strip()
        config.save()
    return {'config': config}

