import random
from http import HTTPStatus

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, F

from rest_framework import mixins, viewsets, filters, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action, api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.decorators import action


from .serializers import (CategorySerializer, GenreSerializer,
                          TitleSerializer, TitleGetSerializer,
                          ReviewSerializer, CommentSerializer)
from reviews.models import Category, Genre, Title, Review
from .permissions import (IsAdminOrReadOnly,
                          IsModeratorAdminOrReadOnly)
from .filters import TitlesFilter
from users.models import User, EmailVerification
from .serializers import (UserSerializer,
                          EmailVerificationSerializer, SignUpSerializer)
from .permissions import IsAdminOrSuperuser


class UserViewSet(viewsets.ModelViewSet):
    """
    Основной вьюсет для представления данных о пользователях.
    Работает с основной моделью User. В зависимости от типа URL
    имеет два уровня доступа: только для админов и суперюзеров
    для просмотра и изменения учетных записей других пользователей
    (IsAdminOrSuperuser) и для авторизованных пользователей - в
    случае работы со своей учетной записью по ссылкам вида /users/me/.
    Не позволяет пользователям изменять свою роль на сайте PATCH-запросом.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'username'
    permission_classes = (IsAdminOrSuperuser,)

    @action(detail=False,
            methods=['GET', 'PATCH'],
            permission_classes=[permissions.IsAuthenticated, ])
    def me(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = UserSerializer(
            user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def signup(request):
    """
    View-функция для создания учетных записей. Обладает следующим функционалом:
    1. Принимает на вход и передаёт в сериализатор данные для создания учетной
    записи
    2. Создаёт проверочный код для подтверждения почтового адреса.
    3. Отправляет код на указанный почтовый адрес.
    4. В случае повторного запроса по username отправляет новый код на почту.
    """

    confirmation_code = str(random.randint(1000, 9999))
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    valid_name = serializer.validated_data.get('username')
    valid_email = serializer.validated_data.get('email')

    confirmation_entry, created = EmailVerification.objects.get_or_create(
        username=valid_name)

    confirmation_entry.confirmation_code = confirmation_code
    confirmation_entry.save()

    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения: {confirmation_code}',
        'mail@yamdb.com',
        (serializer.validated_data.get('email'),),
        fail_silently=True,
    )

    if valid_name in User.objects.values_list(
        'username', flat=True) or valid_email in User.objects.values_list(
            'email', flat=True):
        return Response(serializer.data, status=HTTPStatus.BAD_REQUEST)
    else:
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.OK)


class TokenGetView(APIView):
    """
    View-функция для создания токена пользователя. Осуществляет:
    1. Приём и передачу сериализатору данных запроса: имя пользователя
    (username) и код подтверждения (confirmation_code). На входе проверяет
    регистрировали ли ранее пользователя с таким именем.
    2. Проверяет соответствие проверочного кода выданному пользователю.
    3. Возвращает токен.
    """

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = get_object_or_404(User, username=data['username'])

        if data.get('confirmation_code') == EmailVerification.objects.get(
                username=user.username).confirmation_code:

            token = RefreshToken.for_user(user).access_token
            return Response({'token': str(token)},
                            status=HTTPStatus.CREATED)
        return Response(
            {'confirmation_code': 'Неверный код подтверждения!'},
            status=HTTPStatus.BAD_REQUEST)


class ModelMixinSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                    mixins.DestroyModelMixin, GenericViewSet):
    pass


class CategoriesViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с категориями.
    Выдаёт информацию в сериализатор с пагинацией (по 5 записей).
    Администратор может управлять категориями, другие могут только читать
    /categories/ - получить все категории
    /categories/{id}/ - получить категорию с идентификатором
    /categories/{slug}/ - удалить категорию с помощью slug
    /categories/?search=name - поиск категории по названию
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    @action(
        detail=False, methods=['delete'],
        url_path=r'(?P<slug>\w+)',
        lookup_field='slug', url_name='category_slug'
    )
    def delete_category_slug(self, request, slug):
        category = self.get_object()
        serializer = CategorySerializer(category)
        category.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class GenresViewSet(ModelMixinSet):
    """
    Вьюсет для работы с жанрами.
    Выдаёт информацию в сериализатор с пагинацией (по 5 записей).
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с тайтлами.
    Выдаёт информацию в сериализатор с пагинацией (по 5 записей).
    """
    queryset = Title.objects.annotate(
        rating=Avg(F('reviews__score'))
    ).order_by('name')
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleGetSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с ревью, привязан к модели Title по id.
    Выдаёт информацию в сериализатор с пагинацией (по 5 записей).
    """
    serializer_class = ReviewSerializer
    permission_classes = (IsModeratorAdminOrReadOnly,)
    pagination_class = PageNumberPagination

    def title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.title())


class CommentViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с комментариями, привязан к модели Review по id.
    Выдаёт информацию в сериализатор с пагинацией (по 5 записей).
    """
    serializer_class = CommentSerializer
    permission_classes = (IsModeratorAdminOrReadOnly,)
    pagination_class = PageNumberPagination

    def review_id(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'),
                                 title_id__id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.review_id().review_id.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review_id=self.review_id())
