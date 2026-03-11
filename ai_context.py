"""
AI context for the Tasks module.
Loaded into the assistant system prompt when this module's tools are active.
"""

CONTEXT = """
## Module Knowledge: Tasks

### Models

**Task**
- `title` (str, required), `description` (text)
- `task_type` choices: task | call | meeting | email | follow_up (default: task)
- `priority` choices: low | medium | high | urgent (default: medium)
- `status` choices: pending | in_progress | completed | cancelled (default: pending)
- `due_date` (datetime, optional), `completed_at` (datetime, set automatically by mark_complete())
- `assigned_to` (UUID, optional — references LocalUser)
- `customer` (FK → customers.Customer, SET_NULL, nullable)
- `related_lead` (UUID, optional — for linking to a lead record)
- Call/Meeting fields: `duration_minutes` (int), `result` (text — outcome), `location` (str)
- Recurrence: `is_recurring` (bool), `recurrence_rule` (JSONField — recurrence config)
- `reminder_before_minutes` (int, default 30)

**TaskSettings** (singleton per hub)
- `default_reminder_minutes` (int, default 30)
- `auto_create_follow_up` (bool) — auto-create follow-up after completing call/meeting
- `working_hours_start`, `working_hours_end` (time fields)
- Use `TaskSettings.get_for_hub(hub_id)` to retrieve or create.

### Key Flows

1. **Create task**: set title, task_type, priority, due_date, and optionally assign to a user or link to a customer.
2. **Schedule call/meeting**: use task_type='call' or 'meeting', set due_date for when it happens, set location for meetings.
3. **Complete**: call `task.mark_complete()` — sets status='completed' and completed_at=now.
4. **Reopen**: call `task.mark_reopen()` — resets status to 'pending'.
5. **Follow-up tasks**: create a new task with task_type='follow_up' linked to the same customer/lead.

### Computed Properties

- `is_overdue`: True if due_date is past and status is pending/in_progress
- `is_due_today`: True if due_date is today
- `priority_order`: numeric (0=urgent, 1=high, 2=medium, 3=low) for sorting

### Relationships

- Task → customers.Customer (SET_NULL; `customer` FK).
- `assigned_to` and `related_lead` are raw UUIDs (no FK constraints).
"""
