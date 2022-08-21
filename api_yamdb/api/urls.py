from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views, views

router = SimpleRouter()
router.register(r'users', views.UserViewSet)
router.register(r'categories', views.CategoriesViewSet)
router.register(r'genres', views.GenresViewSet)
router.register(r'titles', views.TitleViewSet)
router.register(r'titles/(?P<title_id>\d+)/reviews',
                views.ReviewViewSet, basename='reviews')
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)'
                r'/comments', views.CommentViewSet, basename='comments')


urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', views.signup),
    path('v1/auth/token/', views.TokenGetView.as_view()),
]
