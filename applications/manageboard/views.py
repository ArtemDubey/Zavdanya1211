from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from applications.accounts.decorators import manager_required
from applications.accounts.models import User
from applications.accounts.selectors.user_selectors import get_all_users
from applications.manageboard.forms import CategoryForm
from applications.manageboard.selectors.manage_selectors import (
    get_status_stats,
    get_agent_stats,
    get_unassigned_count,
    get_categories,
    get_category,
)
from applications.manageboard.services.manage_services import (
    change_user_role,
    save_category,
    delete_category,
)
from applications.tickets.services.exceptions import TicketError


@manager_required
def dashboard_view(request):
    context = {
        'status_stats': get_status_stats(),
        'agent_stats': get_agent_stats(),
        'unassigned_count': get_unassigned_count(),
    }
    return render(request, 'manageboard/dashboard.html', context)


@manager_required
def users_view(request):
    context = {'users': get_all_users(), 'roles': User.Role.choices}
    return render(request, 'manageboard/users.html', context)


@manager_required
@require_POST
def user_role_view(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        change_user_role(request.user, user, request.POST.get('role'))
        messages.success(request, 'Роль змінено')
    except User.DoesNotExist:
        messages.error(request, 'Користувача не знайдено')
    except TicketError as e:
        messages.error(request, str(e))
    return redirect('manage_users')


@manager_required
def categories_view(request):
    return render(request, 'manageboard/categories.html', {'categories': get_categories()})


@manager_required
def category_create_view(request):
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        save_category(form)
        messages.success(request, 'Категорію створено')
        return redirect('manage_categories')
    return render(request, 'manageboard/category_form.html', {'form': form, 'title': 'Нова категорія'})


@manager_required
def category_edit_view(request, category_id):
    try:
        category = get_category(category_id)
    except Exception:
        messages.error(request, 'Категорію не знайдено')
        return redirect('manage_categories')

    form = CategoryForm(request.POST or None, instance=category)
    if request.method == 'POST' and form.is_valid():
        save_category(form)
        messages.success(request, 'Категорію оновлено')
        return redirect('manage_categories')
    return render(request, 'manageboard/category_form.html', {'form': form, 'title': 'Редагування категорії'})


@manager_required
@require_POST
def category_delete_view(request, category_id):
    try:
        delete_category(get_category(category_id))
        messages.success(request, 'Категорію видалено')
    except TicketError as e:
        messages.error(request, str(e))
    except Exception:
        messages.error(request, 'Категорію не знайдено')
    return redirect('manage_categories')