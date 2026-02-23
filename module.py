from django.utils.translation import gettext_lazy as _

MODULE_ID = 'tasks'
MODULE_NAME = _('Tasks')
MODULE_VERSION = '1.0.0'
MODULE_ICON = 'checkbox-outline'
MODULE_DESCRIPTION = _('Task management, calls, meetings and activities')
MODULE_AUTHOR = 'ERPlora'
MODULE_CATEGORY = 'productivity'

MENU = {
    'label': _('Tasks'),
    'icon': 'checkbox-outline',
    'order': 25,
}

NAVIGATION = [
    {'label': _('Dashboard'), 'icon': 'speedometer-outline', 'id': 'dashboard'},
    {'label': _('Tasks'), 'icon': 'checkbox-outline', 'id': 'list'},
    {'label': _('Calendar'), 'icon': 'calendar-outline', 'id': 'calendar'},
    {'label': _('Settings'), 'icon': 'settings-outline', 'id': 'settings'},
]

DEPENDENCIES = ['customers']

PERMISSIONS = [
    'tasks.view_task',
    'tasks.add_task',
    'tasks.change_task',
    'tasks.delete_task',
    'tasks.complete_task',
    'tasks.manage_settings',
]
