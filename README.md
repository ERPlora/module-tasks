# Tasks

## Overview

| Property | Value |
|----------|-------|
| **Module ID** | `tasks` |
| **Version** | `1.0.0` |
| **Icon** | `checkbox-outline` |
| **Dependencies** | `customers` |

## Dependencies

This module requires the following modules to be installed:

- `customers`

## Models

### `Task`

Task(id, hub_id, created_at, updated_at, created_by, updated_by, is_deleted, deleted_at, title, description, task_type, priority, status, due_date, completed_at, assigned_to, customer, related_lead, duration_minutes, result, location, is_recurring, recurrence_rule, reminder_before_minutes)

| Field | Type | Details |
|-------|------|---------|
| `title` | CharField | max_length=255 |
| `description` | TextField | optional |
| `task_type` | CharField | max_length=20, choices: task, call, meeting, email, follow_up |
| `priority` | CharField | max_length=20, choices: low, medium, high, urgent |
| `status` | CharField | max_length=20, choices: pending, in_progress, completed, cancelled |
| `due_date` | DateTimeField | optional |
| `completed_at` | DateTimeField | optional |
| `assigned_to` | UUIDField | max_length=32, optional |
| `customer` | ForeignKey | → `customers.Customer`, on_delete=SET_NULL, optional |
| `related_lead` | UUIDField | max_length=32, optional |
| `duration_minutes` | PositiveIntegerField | optional |
| `result` | TextField | optional |
| `location` | CharField | max_length=255, optional |
| `is_recurring` | BooleanField |  |
| `recurrence_rule` | JSONField | optional |
| `reminder_before_minutes` | IntegerField |  |

**Methods:**

- `mark_complete()` — Mark task as completed.
- `mark_reopen()` — Reopen a completed/cancelled task.

**Properties:**

- `is_overdue` — Check if task is overdue (past due date and not completed/cancelled).
- `is_due_today` — Check if task is due today.
- `is_completed`
- `priority_order` — Numeric priority for sorting (lower = more urgent).
- `type_icon` — Return an icon name for the task type.
- `priority_color` — Return a color class for the priority level.
- `status_color` — Return a color class for the status.
- `due_date_color` — Return a color class based on due date proximity.
- `customer_name` — Return customer name or empty string.

### `TaskSettings`

TaskSettings(id, hub_id, created_at, updated_at, created_by, updated_by, is_deleted, deleted_at, default_reminder_minutes, auto_create_follow_up, working_hours_start, working_hours_end)

| Field | Type | Details |
|-------|------|---------|
| `default_reminder_minutes` | IntegerField |  |
| `auto_create_follow_up` | BooleanField |  |
| `working_hours_start` | TimeField |  |
| `working_hours_end` | TimeField |  |

**Methods:**

- `get_for_hub()` — Get or create settings for a hub.

## Cross-Module Relationships

| From | Field | To | on_delete | Nullable |
|------|-------|----|-----------|----------|
| `Task` | `customer` | `customers.Customer` | SET_NULL | Yes |

## URL Endpoints

Base path: `/m/tasks/`

| Path | Name | Method |
|------|------|--------|
| `(root)` | `dashboard` | GET |
| `list/` | `list` | GET |
| `calendar/` | `calendar` | GET |
| `tasks/` | `tasks_list` | GET |
| `tasks/add/` | `task_add` | GET/POST |
| `tasks/<uuid:pk>/edit/` | `task_edit` | GET |
| `tasks/<uuid:pk>/delete/` | `task_delete` | GET/POST |
| `tasks/bulk/` | `tasks_bulk_action` | GET/POST |
| `settings/` | `settings` | GET |

## Permissions

| Permission | Description |
|------------|-------------|
| `tasks.view_task` | View Task |
| `tasks.add_task` | Add Task |
| `tasks.change_task` | Change Task |
| `tasks.delete_task` | Delete Task |
| `tasks.complete_task` | Complete Task |
| `tasks.manage_settings` | Manage Settings |

**Role assignments:**

- **admin**: All permissions
- **manager**: `add_task`, `change_task`, `complete_task`, `view_task`
- **employee**: `add_task`, `complete_task`, `view_task`

## Navigation

| View | Icon | ID | Fullpage |
|------|------|----|----------|
| Dashboard | `speedometer-outline` | `dashboard` | No |
| Tasks | `checkbox-outline` | `list` | No |
| Calendar | `calendar-outline` | `calendar` | No |
| Settings | `settings-outline` | `settings` | No |

## AI Tools

Tools available for the AI assistant:

### `list_tasks`

List tasks with filters (status, priority, type, assigned_to, overdue).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | pending, in_progress, completed, cancelled |
| `priority` | string | No | low, medium, high, urgent |
| `task_type` | string | No | task, call, meeting, email, follow_up |
| `assigned_to` | string | No |  |
| `customer_id` | string | No |  |
| `overdue` | boolean | No | Only show overdue tasks |
| `limit` | integer | No |  |

### `create_task`

Create a task (task, call, meeting, email, follow_up).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | string | Yes |  |
| `description` | string | No |  |
| `task_type` | string | No | task, call, meeting, email, follow_up |
| `priority` | string | No | low, medium, high, urgent |
| `due_date` | string | No |  |
| `assigned_to` | string | No |  |
| `customer_id` | string | No |  |
| `location` | string | No |  |
| `duration_minutes` | integer | No |  |

### `update_task_status`

Update a task's status or priority.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string | Yes |  |
| `status` | string | No |  |
| `priority` | string | No |  |
| `result` | string | No |  |

## File Structure

```
README.md
__init__.py
admin.py
ai_tools.py
apps.py
forms.py
locale/
  en/
    LC_MESSAGES/
      django.po
  es/
    LC_MESSAGES/
      django.po
migrations/
  0001_initial.py
  __init__.py
models.py
module.py
static/
  tasks/
    css/
      calendar.css
    js/
templates/
  tasks/
    pages/
      calendar.html
      dashboard.html
      index.html
      list.html
      settings.html
      task_add.html
      task_edit.html
      tasks.html
    partials/
      calendar_content.html
      dashboard_content.html
      panel_task_add.html
      panel_task_edit.html
      settings_content.html
      task_add_content.html
      task_detail.html
      task_edit_content.html
      tasks_content.html
      tasks_list.html
tests/
  __init__.py
  conftest.py
  test_models.py
  test_views.py
urls.py
views.py
```
