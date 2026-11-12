from applications.accounts.models import User


def get_agents():
    return User.objects.filter(role=User.Role.AGENT)


def get_all_users():
    return User.objects.all().order_by('username')


def get_user_by_id(user_id):
    return User.objects.get(id=user_id)