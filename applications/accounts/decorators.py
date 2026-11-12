from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from applications.accounts.models import User


def manager_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != User.Role.MANAGER:
            messages.error(request, 'Доступ лише для менеджерів')
            return redirect('ticket_list')
        return view(request, *args, **kwargs)
    return wrapper