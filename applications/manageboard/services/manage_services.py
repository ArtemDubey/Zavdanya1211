from django.db.models import ProtectedError

from applications.accounts.models import User
from applications.tickets.services.exceptions import TicketError


def change_user_role(manager, user, new_role):
    if manager.role != User.Role.MANAGER:
        raise TicketError('Керувати ролями може лише менеджер')
    if new_role not in User.Role.values:
        raise TicketError('Невідома роль')
    if manager.id == user.id:
        raise TicketError('Не можна змінити власну роль')

    user.role = new_role
    user.save()
    return user


def save_category(form):
    return form.save()


def delete_category(category):
    try:
        category.delete()
    except ProtectedError:
        raise TicketError('Не можна видалити категорію, у якій є заявки')