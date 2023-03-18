from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Advertisement, AdvertisementFavorites
from .serializers import AdvertisementSerializer
from .permissions import IsOwnerOrReadOnly
from .filters import AdvertisementFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User


class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""

    # TODO: настройте ViewSet, укажите атрибуты для кверисета,
    #   сериализаторов и фильтров
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdvertisementFilter
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_permissions(self):
        """Получение прав для действий."""

        print('*****1', self.action)
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        elif self.action in ["favorites"]:
            return [IsAuthenticated()]
        return []

    @action(methods=['get'], detail=False)
    def favorites(self, request):
        """Выводит список избранных объявлений."""

        queryset = Advertisement.objects.prefetch_related('users').filter(users=request.user.id)
        serializer = AdvertisementSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def add(self, request, pk=None):
        """Добавляет объявление в список избранных."""

        ads = Advertisement.objects.get(pk=pk)
        if ads.creator.id == request.user.id:
            return Response({'Ошибка! Нельзя добавлять собственные объявления в избранное'})
        else:
            user = User.objects.get(pk=request.user.id)
            if AdvertisementFavorites.objects.filter(advertisement=ads, user=user):
                return Response({'Ошибка! Объявление уже добавлено в избранное'})
            else:
                AdvertisementFavorites(advertisement=ads, user=user).save()
            return Response({f'Объявление id:{pk} добавлено в избранное для user:{request.user.id}'})

    def get_queryset(self):
        """Перезадает queryset. Анонимные пользователи не видят объявлений со статусом DRAFT.
        Авторизованные пользователи не видят сообщения со статусом DRAFT других пользователей,
        но видят свои."""

        user = self.request.user.id
        if user != None:
            return Advertisement.objects.exclude(status='DRAFT', creator_id__lt=user).exclude(status='DRAFT', creator_id__gt=user)
        return Advertisement.objects.all().exclude(status='DRAFT')        