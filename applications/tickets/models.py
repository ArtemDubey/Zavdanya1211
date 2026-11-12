from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Назва',
    )

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

    def __str__(self):
        return self.name


class Ticket(models.Model):

    class Priority(models.TextChoices):
        LOW = 'low', 'Низький'
        MEDIUM = 'medium', 'Середній'
        HIGH = 'high', 'Високий'
        CRITICAL = 'critical', 'Критичний'

    class Status(models.TextChoices):
        NEW = 'new', 'Нова'
        IN_PROGRESS = 'in_progress', 'В роботі'
        WAITING = 'waiting', 'Очікує відповіді клієнта'
        RESOLVED = 'resolved', 'Вирішена'
        CLOSED = 'closed', 'Закрита'
        REJECTED = 'rejected', 'Відхилена'

    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
    )
    description = models.TextField(
        verbose_name='Опис',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='tickets',
        verbose_name='Категорія',
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name='Пріоритет',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        verbose_name='Статус',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tickets',
        verbose_name='Автор',
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name='Виконавець',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата створення',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата оновлення',
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата вирішення',
    )

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.id} {self.title}'