from django.db.models import Q
from django.shortcuts import get_object_or_404

from applications.accounts.models import User
from applications.tickets.models import Ticket


def get_tickets_for_user(user):
    tickets = Ticket.objects.select_related('category', 'author', 'assignee')

    if user.role == User.Role.MANAGER:
        return tickets

    if user.role == User.Role.AGENT:
        return tickets.filter(Q(status=Ticket.Status.NEW) | Q(assignee=user))

    return tickets.filter(author=user)


def get_ticket_for_user(user, ticket_id):
    return get_object_or_404(get_tickets_for_user(user), id=ticket_id)