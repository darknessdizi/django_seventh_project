from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        elif bool(request.user and request.user.is_staff): # проверка является ли пользователь админом
            return True
        else:
            return request.user == obj.creator # проверка является ли пользователь собственником