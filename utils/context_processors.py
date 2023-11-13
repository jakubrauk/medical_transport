from django.contrib.auth.models import Group


def user_groups_context(request):
    return {'user_groups_names': [group.name for group in request.user.groups.all()]}
