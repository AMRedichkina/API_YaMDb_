import regex as re

from django.db.models import Avg

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Category, Genre, Title, Review, Comments
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Основной сериализатор пользовательской модели. Работает с шестью полями:
    username, email, first_name, last_name, bio, role. Обязательный поля:
    username и email. Осуществляет проверку на уникальность почты (email).
    """

    class Meta:
        fields = ('username', 'email',
                  'first_name', 'last_name', 'bio', 'role')
        model = User
        required_fields = ('username', 'email',)

    def validate_email(self, value):
        if value in User.objects.values_list('email', flat=True):
            raise serializers.ValidationError('Такой адрес уже есть в базе!')
        return value


class SignUpSerializer(serializers.Serializer):
    """
    Сериализатор данных для создания новой учетной записи: работает
    с двумя полями: username и email. Осуществляет проверку на уникальность
    почты (email) и соответствия имени пользователя требованиям.
    """
    username = serializers.CharField(
        max_length=30,
        required=True,
    )
    email = serializers.EmailField()

    class Meta:
        fields = ('username', 'email')
        model = User
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email']
            )
        ]

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def validate_username(self, value):
        if value == 'me' or not re.findall(r'^[\w.\@\+\-]+', value):
            raise serializers.ValidationError(
                'Некорректный username!')
        return value


class EmailVerificationSerializer(serializers.Serializer):
    """
    Сериализатор данных для подтверждения почтового адреса: работает с двумя
    полями: username и confirmation_code.
    """

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate_email(self, value):
        if value not in User.objects.values_list('email', flat=True):
            raise serializers.ValidationError(
                'Такого пользователя не регистрировали!')
        return value


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all())
    rating = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        model = Title
        required_fields = ('name', 'year', 'genre', 'category')


class TitleGetSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        model = Title

    def get_rating(self, obj):
        qs = obj.reviews.all()
        return qs.aggregate(rating=Avg('score')).get('rating')


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name', read_only=True)
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True)

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        user = self.context['request'].user
        title = self.context['view'].kwargs['title_id']
        if Review.objects.filter(author=user, title=title).exists():
            raise serializers.ValidationError(
                'Отзыв уже оставлен!'
            )
        return data

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'author', 'pub_date', 'text')
        model = Comments
        read_only_fields = ('id', 'author', 'pub_date')
