from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Task List
    path('list/', views.task_list, name='list'),

    # Calendar
    path('calendar/', views.calendar_view, name='calendar'),

    # Task CRUD
    path('add/', views.task_add, name='add'),
    path('<uuid:task_id>/', views.task_detail, name='detail'),
    path('<uuid:task_id>/edit/', views.task_edit, name='edit'),
    path('<uuid:task_id>/delete/', views.task_delete, name='delete'),

    # Task Actions
    path('<uuid:task_id>/complete/', views.task_complete, name='complete'),
    path('<uuid:task_id>/reopen/', views.task_reopen, name='reopen'),

    # Bulk Actions
    path('bulk/', views.task_bulk_action, name='bulk_action'),

    # Settings
    path('settings/', views.settings_view, name='settings'),

    # API
    path('api/calendar-data/', views.calendar_data_api, name='calendar_data'),
]
