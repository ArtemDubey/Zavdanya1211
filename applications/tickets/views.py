from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from applications.tickets.services.exceptions import TicketError
from applications.accounts.selectors.user_selectors import get_agents

from applications.accounts.models import User
from applications.tickets.forms import TicketForm
from applications.tickets.selectors.ticket_selectors import (
    get_tickets_for_user,
    get_ticket_for_user,
)
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST

from applications.tickets.models import Ticket
from applications.tickets.services.ticket_services import (
    create_ticket,
    take_ticket,
    assign_ticket,
    change_status,
    change_priority,
)
from applications.tickets.services.ticket_services import create_ticket


@login_required
def ticket_list_view(request):
    tickets = get_tickets_for_user(request.user)
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})


@login_required
def ticket_detail_view(request, ticket_id):
    ticket = get_ticket_for_user(request.user, ticket_id)
    context = {
        'ticket': ticket,
        'agents': get_agents() if request.user.role == User.Role.MANAGER else None,
        'priorities': Ticket.Priority.choices,
    }
    return render(request, 'tickets/ticket_detail.html', context)


@login_required
def ticket_create_view(request):
    if request.user.role != User.Role.CLIENT:
        return redirect('ticket_list')

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            try:
                ticket = create_ticket(form, request.user)
            except TicketError as e:
                messages.error(request, str(e))
            else:
                return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketForm()
    return render(request, 'tickets/ticket_form.html', {'form': form})
@login_required
@require_POST
def ticket_take_view(request, ticket_id):
    ticket = get_ticket_for_user(request.user, ticket_id)
    try:
        take_ticket(ticket, request.user)
        messages.success(request, 'Заявку взято в роботу')
    except TicketError as e:
        messages.error(request, str(e))
    return redirect('ticket_detail', ticket_id=ticket.id)


@login_required
@require_POST
def ticket_status_view(request, ticket_id):
    ticket = get_ticket_for_user(request.user, ticket_id)
    try:
        change_status(ticket, request.user, request.POST.get('status'))
        messages.success(request, 'Статус змінено')
    except TicketError as e:
        messages.error(request, str(e))
    return redirect('ticket_detail', ticket_id=ticket.id)


@login_required
@require_POST
def ticket_priority_view(request, ticket_id):
    ticket = get_ticket_for_user(request.user, ticket_id)
    try:
        change_priority(ticket, request.user, request.POST.get('priority'))
        messages.success(request, 'Пріоритет змінено')
    except TicketError as e:
        messages.error(request, str(e))
    return redirect('ticket_detail', ticket_id=ticket.id)


@login_required
@require_POST
def ticket_assign_view(request, ticket_id):
    ticket = get_ticket_for_user(request.user, ticket_id)
    User = get_user_model()
    try:
        agent = User.objects.get(id=request.POST.get('agent'))
        assign_ticket(ticket, request.user, agent)
        messages.success(request, 'Виконавця призначено')
    except (User.DoesNotExist, ValueError):
        messages.error(request, 'Агента не знайдено')
    except TicketError as e:
        messages.error(request, str(e))
    return redirect('ticket_detail', ticket_id=ticket.id)