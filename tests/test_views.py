"""Tests for tasks views."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestDashboard:
    """Dashboard view tests."""

    def test_dashboard_loads(self, auth_client):
        """Test dashboard page loads."""
        url = reverse('tasks:dashboard')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_dashboard_htmx(self, auth_client):
        """Test dashboard HTMX partial."""
        url = reverse('tasks:dashboard')
        response = auth_client.get(url, HTTP_HX_REQUEST='true')
        assert response.status_code == 200

    def test_dashboard_requires_auth(self, client):
        """Test dashboard requires authentication."""
        url = reverse('tasks:dashboard')
        response = client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestTaskViews:
    """Task view tests."""

    def test_list_loads(self, auth_client):
        """Test list view loads."""
        url = reverse('tasks:tasks_list')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_list_htmx(self, auth_client):
        """Test list HTMX partial."""
        url = reverse('tasks:tasks_list')
        response = auth_client.get(url, HTTP_HX_REQUEST='true')
        assert response.status_code == 200

    def test_list_search(self, auth_client):
        """Test list search."""
        url = reverse('tasks:tasks_list')
        response = auth_client.get(url, {'q': 'test'})
        assert response.status_code == 200

    def test_list_sort(self, auth_client):
        """Test list sorting."""
        url = reverse('tasks:tasks_list')
        response = auth_client.get(url, {'sort': 'created_at', 'dir': 'desc'})
        assert response.status_code == 200

    def test_export_csv(self, auth_client):
        """Test CSV export."""
        url = reverse('tasks:tasks_list')
        response = auth_client.get(url, {'export': 'csv'})
        assert response.status_code == 200
        assert 'text/csv' in response['Content-Type']

    def test_export_excel(self, auth_client):
        """Test Excel export."""
        url = reverse('tasks:tasks_list')
        response = auth_client.get(url, {'export': 'excel'})
        assert response.status_code == 200

    def test_add_form_loads(self, auth_client):
        """Test add form loads."""
        url = reverse('tasks:task_add')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_add_post(self, auth_client):
        """Test creating via POST."""
        url = reverse('tasks:task_add')
        data = {
            'title': 'New Title',
            'description': 'Test description',
            'task_type': 'New Task Type',
            'priority': 'New Priority',
            'status': 'New Status',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200

    def test_edit_form_loads(self, auth_client, task):
        """Test edit form loads."""
        url = reverse('tasks:task_edit', args=[task.pk])
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_edit_post(self, auth_client, task):
        """Test editing via POST."""
        url = reverse('tasks:task_edit', args=[task.pk])
        data = {
            'title': 'Updated Title',
            'description': 'Test description',
            'task_type': 'Updated Task Type',
            'priority': 'Updated Priority',
            'status': 'Updated Status',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200

    def test_delete(self, auth_client, task):
        """Test soft delete via POST."""
        url = reverse('tasks:task_delete', args=[task.pk])
        response = auth_client.post(url)
        assert response.status_code == 200
        task.refresh_from_db()
        assert task.is_deleted is True

    def test_bulk_delete(self, auth_client, task):
        """Test bulk delete."""
        url = reverse('tasks:tasks_bulk_action')
        response = auth_client.post(url, {'ids': str(task.pk), 'action': 'delete'})
        assert response.status_code == 200
        task.refresh_from_db()
        assert task.is_deleted is True

    def test_list_requires_auth(self, client):
        """Test list requires authentication."""
        url = reverse('tasks:tasks_list')
        response = client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestSettings:
    """Settings view tests."""

    def test_settings_loads(self, auth_client):
        """Test settings page loads."""
        url = reverse('tasks:settings')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_settings_requires_auth(self, client):
        """Test settings requires authentication."""
        url = reverse('tasks:settings')
        response = client.get(url)
        assert response.status_code == 302

