from django.contrib.auth.models import Group
from base_app.models import Settings


def user_groups_context(request):
    return {
        'user_groups_names': [group.name for group in request.user.groups.all()],
        'user_id': request.user.id,
        'settings': Settings.objects.get_or_create()[0].get_dict(),
    }
