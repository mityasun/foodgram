from api.views import (CustomUserViewSet, IngredientsViewSet, RecipesViewSet,
                       TagsViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router_v1 = DefaultRouter()
router_v1.register(r'tags', TagsViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router_v1.register(r'recipes', RecipesViewSet, basename='recipes')
router_v1.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
]
