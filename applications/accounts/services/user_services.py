from applications.accounts.models import User


def register_user(form):
    user = form.save(commit=False)
    user.role = User.Role.CLIENT
    user.save()
    return user


def update_profile(form):
    return form.save()