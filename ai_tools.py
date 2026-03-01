"""AI tools for the Tasks module."""
from assistant.tools import AssistantTool, register_tool


@register_tool
class ListTasks(AssistantTool):
    name = "list_tasks"
    description = "List tasks with filters (status, priority, type, assigned_to, overdue)."
    module_id = "tasks"
    required_permission = "tasks.view_task"
    parameters = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "description": "pending, in_progress, completed, cancelled"},
            "priority": {"type": "string", "description": "low, medium, high, urgent"},
            "task_type": {"type": "string", "description": "task, call, meeting, email, follow_up"},
            "assigned_to": {"type": "string"}, "customer_id": {"type": "string"},
            "overdue": {"type": "boolean", "description": "Only show overdue tasks"},
            "limit": {"type": "integer"},
        },
        "required": [],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from tasks.models import Task
        from django.utils import timezone
        qs = Task.objects.all()
        if args.get('status'):
            qs = qs.filter(status=args['status'])
        if args.get('priority'):
            qs = qs.filter(priority=args['priority'])
        if args.get('task_type'):
            qs = qs.filter(task_type=args['task_type'])
        if args.get('assigned_to'):
            qs = qs.filter(assigned_to=args['assigned_to'])
        if args.get('customer_id'):
            qs = qs.filter(customer_id=args['customer_id'])
        if args.get('overdue'):
            qs = qs.filter(status__in=['pending', 'in_progress'], due_date__lt=timezone.now())
        limit = args.get('limit', 20)
        return {
            "tasks": [
                {"id": str(t.id), "title": t.title, "task_type": t.task_type, "priority": t.priority, "status": t.status, "due_date": str(t.due_date) if t.due_date else None, "description": t.description[:100]}
                for t in qs.order_by('-priority', 'due_date')[:limit]
            ]
        }


@register_tool
class CreateTask(AssistantTool):
    name = "create_task"
    description = "Create a task (task, call, meeting, email, follow_up)."
    module_id = "tasks"
    required_permission = "tasks.add_task"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "title": {"type": "string"}, "description": {"type": "string"},
            "task_type": {"type": "string", "description": "task, call, meeting, email, follow_up"},
            "priority": {"type": "string", "description": "low, medium, high, urgent"},
            "due_date": {"type": "string"}, "assigned_to": {"type": "string"},
            "customer_id": {"type": "string"}, "location": {"type": "string"},
            "duration_minutes": {"type": "integer"},
        },
        "required": ["title"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from tasks.models import Task
        t = Task.objects.create(
            title=args['title'], description=args.get('description', ''),
            task_type=args.get('task_type', 'task'), priority=args.get('priority', 'medium'),
            due_date=args.get('due_date'), assigned_to=args.get('assigned_to'),
            customer_id=args.get('customer_id'), location=args.get('location', ''),
            duration_minutes=args.get('duration_minutes', 0),
        )
        return {"id": str(t.id), "title": t.title, "created": True}


@register_tool
class UpdateTaskStatus(AssistantTool):
    name = "update_task_status"
    description = "Update a task's status or priority."
    module_id = "tasks"
    required_permission = "tasks.change_task"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "task_id": {"type": "string"}, "status": {"type": "string"},
            "priority": {"type": "string"}, "result": {"type": "string"},
        },
        "required": ["task_id"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from tasks.models import Task
        from django.utils import timezone
        t = Task.objects.get(id=args['task_id'])
        if 'status' in args:
            t.status = args['status']
            if args['status'] == 'completed':
                t.completed_at = timezone.now()
        if 'priority' in args:
            t.priority = args['priority']
        if 'result' in args:
            t.result = args['result']
        t.save()
        return {"id": str(t.id), "status": t.status, "updated": True}
