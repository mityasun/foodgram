from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from users.models import Subscribe


def check_request_send_boolean(self, obj, model):
    """Проверяем, что запрос есть и юзер не аноним"""

    request = self.context.get('request')
    if not request or request.user.is_anonymous:
        return False
    if model == Subscribe:
        return model.objects.filter(user=request.user, author=obj.id).exists()
    return model.objects.filter(recipe=obj, user=request.user).exists()


class FavoriteCart:

    add_model = None
    add_serializer = None

    def favorite_and_cart(self, request, obj_id, model, errors):
        """Общая функция для Favorite и Cart для добавления и удаления"""

        user = request.user
        obj = model.objects.filter(user=user, recipe=obj_id)
        if request.method == 'POST':
            if obj.exists():
                return Response(
                    {'errors': errors.get('if_exists')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            obj = get_object_or_404(self.add_model, id=obj_id)
            model.objects.create(user=user, recipe=obj)
            return Response(
                self.add_serializer(obj).data, status=status.HTTP_201_CREATED

            )
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': errors.get('if_deleted')},
            status=status.HTTP_400_BAD_REQUEST
        )
