"""Tests for tasks models."""
import pytest
from django.utils import timezone

from tasks.models import Task


@pytest.mark.django_db
class TestTask:
    """Task model tests."""

    def test_create(self, task):
        """Test Task creation."""
        assert task.pk is not None
        assert task.is_deleted is False

    def test_str(self, task):
        """Test string representation."""
        assert str(task) is not None
        assert len(str(task)) > 0

    def test_soft_delete(self, task):
        """Test soft delete."""
        pk = task.pk
        task.is_deleted = True
        task.deleted_at = timezone.now()
        task.save()
        assert not Task.objects.filter(pk=pk).exists()
        assert Task.all_objects.filter(pk=pk).exists()

    def test_queryset_excludes_deleted(self, hub_id, task):
        """Test default queryset excludes deleted."""
        task.is_deleted = True
        task.deleted_at = timezone.now()
        task.save()
        assert Task.objects.filter(hub_id=hub_id).count() == 0


