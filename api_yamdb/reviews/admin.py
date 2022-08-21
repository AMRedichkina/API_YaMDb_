from django.contrib import admin
from .models import Category
from .models import Title
from .models import Review
from .models import Comments
from .models import Genre


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'slug'
    ]


@admin.register(Title)
class TitlesAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'year',
        'category',
        'description'
    ]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'slug'
    ]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'title_id',
        'text',
        'author',
        'score',
        'pub_date'
    ]


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'review_id',
        'text',
        'author',
        'pub_date'
    ]
