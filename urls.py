from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Navigation tab aliases
    path('list/', views.tasks_list, name='list'),
    path('calendar/', views.dashboard, name='calendar'),


    # Task
    path('tasks/', views.tasks_list, name='tasks_list'),
    path('tasks/add/', views.task_add, name='task_add'),
    path('tasks/<uuid:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<uuid:pk>/delete/', views.task_delete, name='task_delete'),
    path('tasks/bulk/', views.tasks_bulk_action, name='tasks_bulk_action'),

    # Settings
    path('settings/', views.settings_view, name='settings'),
]
