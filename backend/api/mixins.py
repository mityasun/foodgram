from users.models import Subscribe


def check_request_user(self):
    """Проверяем, что запрос есть и юзер не аноним"""
    request = self.context.get('request')
    if request is None or request.user.is_anonymous:
        return False
    return True


def is_subscribed(self, obj):
    """Получаем статус подписки на автора"""

    return Subscribe.objects.filter(
        user__follower__author=obj.id
    ).exists()
