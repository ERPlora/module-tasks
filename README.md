# Tasks Module

Task management, calls, meetings and activities.

## Features

- Create and manage tasks, calls, meetings, emails, and follow-ups
- Priority levels (low, medium, high, urgent) with color-coded indicators
- Status workflow: pending, in progress, completed, cancelled
- Due date tracking with overdue and due-today detection
- Assign tasks to staff members and link to customers or leads
- Calendar view for scheduling and time-based planning
- Call and meeting specific fields: duration, result, and location
- Recurring tasks with JSON-based recurrence rules
- Configurable reminders before due dates
- Auto-create follow-up tasks after completing calls or meetings
- Configurable working hours for scheduling context
- Dashboard with task metrics and activity overview

## Installation

This module is installed automatically via the ERPlora Marketplace.

**Dependencies**: Requires `customers` module.

## Configuration

Access settings via: **Menu > Tasks > Settings**

Configurable options include:
- Default reminder time (minutes before due date)
- Auto-create follow-up tasks after calls/meetings
- Working hours start and end times

## Usage

Access via: **Menu > Tasks**

### Views

| View | URL | Description |
|------|-----|-------------|
| Dashboard | `/m/tasks/dashboard/` | Task metrics and activity overview |
| Tasks | `/m/tasks/list/` | List, create and manage tasks and activities |
| Calendar | `/m/tasks/calendar/` | Calendar view of scheduled tasks, calls, and meetings |
| Settings | `/m/tasks/settings/` | Module configuration |

## Models

| Model | Description |
|-------|-------------|
| `Task` | Task or activity with title, description, type (task/call/meeting/email/follow-up), priority, status, due date, assignment, customer link, lead reference, duration, result, location, recurrence rules, and reminder settings |
| `TaskSettings` | Singleton settings per hub for default reminder time, auto-follow-up creation, and working hours |

## Permissions

| Permission | Description |
|------------|-------------|
| `tasks.view_task` | View tasks |
| `tasks.add_task` | Create new tasks |
| `tasks.change_task` | Edit existing tasks |
| `tasks.delete_task` | Delete tasks |
| `tasks.complete_task` | Mark tasks as completed |
| `tasks.manage_settings` | Manage module settings |

## Integration with Other Modules

- **customers**: Tasks can be linked to a customer record via the `customer` foreign key.

## License

MIT

## Author

ERPlora Team - support@erplora.com
