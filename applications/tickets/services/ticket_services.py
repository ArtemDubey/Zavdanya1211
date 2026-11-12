from datetime import timedelta

from django.utils import timezone

from applications.accounts.models import User
from applications.tickets.models import Ticket
from applications.tickets.services.exceptions import TicketError

MAX_OPEN_TICKETS = 5
REOPEN_DAYS = 3

CLOSED_STATUSES = (Ticket.Status.CLOSED, Ticket.Status.REJECTED)

TRANSITIONS = {
    Ticket.Status.NEW: [Ticket.Status.IN_PROGRESS, Ticket.Status.REJECTED],
    Ticket.Status.IN_PROGRESS: [Ticket.Status.WAITING, Ticket.Status.RESOLVED, Ticket.Status.REJECTED],
    Ticket.Status.WAITING: [Ticket.Status.IN_PROGRESS, Ticket.Status.RESOLVED],
    Ticket.Status.RESOLVED: [Ticket.Status.IN_PROGRESS, Ticket.Status.CLOSED],
    Ticket.Status.CLOSED: [],
    Ticket.Status.REJECTED: [],
}


def create_ticket(form, author):
    open_count = Ticket.objects.filter(author=author).exclude(
        status__in=CLOSED_STATUSES
    ).count()
    if open_count >= MAX_OPEN_TICKETS:
        raise TicketError(f'Не можна мати більше {MAX_OPEN_TICKETS} відкритих заявок одночасно')

    ticket = form.save(commit=False)
    ticket.author = author
    ticket.save()
    return ticket


def take_ticket(ticket, user):
    if user.role != User.Role.AGENT:
        raise TicketError('Брати заявки в роботу можуть лише агенти')
    if ticket.author_id == user.id:
        raise TicketError('Не можна обробляти власну заявку')
    if ticket.status in CLOSED_STATUSES:
        raise TicketError('Заявка закрита або відхилена')
    if ticket.assignee_id and ticket.assignee_id != user.id:
        raise TicketError('Заявка вже призначена іншому агенту')
    if ticket.status != Ticket.Status.NEW:
        raise TicketError('Взяти в роботу можна лише нову заявку')

    ticket.assignee = user
    ticket.status = Ticket.Status.IN_PROGRESS
    ticket.save()
    return ticket


def assign_ticket(ticket, manager, agent):
    if manager.role != User.Role.MANAGER:
        raise TicketError('Призначати виконавця може лише менеджер')
    if agent.role != User.Role.AGENT:
        raise TicketError('Виконавцем може бути лише користувач з роллю Agent')
    if ticket.status in CLOSED_STATUSES:
        raise TicketError('Заявка закрита або відхилена')
    if ticket.author_id == agent.id:
        raise TicketError('Агент не може обробляти власну заявку')

    ticket.assignee = agent
    ticket.save()
    return ticket


def change_status(ticket, user, new_status):
    if new_status not in Ticket.Status.values:
        raise TicketError('Невідомий статус')

    if ticket.status in CLOSED_STATUSES:
        raise TicketError('Закриту або відхилену заявку не можна змінювати')

    if new_status not in TRANSITIONS[ticket.status]:
        raise TicketError('Такий перехід статусу неможливий')

    if user.role == User.Role.CLIENT:
        _check_client_status(ticket, user, new_status)
    elif user.role == User.Role.AGENT:
        _check_agent_status(ticket, user)

    if new_status == Ticket.Status.RESOLVED:
        ticket.resolved_at = timezone.now()

    ticket.status = new_status
    ticket.save()
    return ticket


def _check_agent_status(ticket, user):
    if ticket.author_id == user.id:
        raise TicketError('Не можна обробляти власну заявку')
    if ticket.assignee_id != user.id:
        raise TicketError('Це не ваша заявка')


def _check_client_status(ticket, user, new_status):
    if ticket.author_id != user.id:
        raise TicketError('Це не ваша заявка')
    if ticket.status != Ticket.Status.RESOLVED:
        raise TicketError('Клієнт може змінювати статус лише вирішеної заявки')

    if new_status == Ticket.Status.IN_PROGRESS:
        deadline = ticket.resolved_at + timedelta(days=REOPEN_DAYS)
        if timezone.now() > deadline:
            raise TicketError(
                f'Повторно відкрити можна лише протягом {REOPEN_DAYS} днів, тепер тільки закрити')


def change_priority(ticket, user, new_priority):
    if new_priority not in Ticket.Priority.values:
        raise TicketError('Невідомий пріоритет')

    if user.role != User.Role.MANAGER:
        raise TicketError('Змінювати пріоритет може лише менеджер')

    if ticket.status in CLOSED_STATUSES:
        raise TicketError('Закриту або відхилену заявку не можна змінювати')

    ticket.priority = new_priority
    ticket.save()
    return ticket