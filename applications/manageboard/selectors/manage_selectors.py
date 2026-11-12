from django.db.models import Count, Q

from applications.accounts.models import User
from applications.tickets.models import Category, Ticket


def get_status_stats():
    counts = dict(
        Ticket.objects.values_list('status').annotate(c=Count('id'))
    )
    return [
        {'value': value, 'label': label, 'count': counts.get(value, 0)}
        for value, label in Ticket.Status.choices
    ]


def get_agent_stats():
    return User.objects.filter(role=User.Role.AGENT).annotate(
        total=Count('assigned_tickets'),
        resolved=Count(
            'assigned_tickets',
            filter=Q(assigned_tickets__status=Ticket.Status.RESOLVED),
        ),
    ).order_by('username')


def get_unassigned_count():
    return Ticket.objects.filter(assignee__isnull=True).exclude(
        status__in=(Ticket.Status.CLOSED, Ticket.Status.REJECTED)
    ).count()


def get_categories():
    return Category.objects.annotate(tickets_count=Count('tickets')).order_by('name')


def get_category(category_id):
    return Category.objects.get(id=category_id)