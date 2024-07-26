from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from api.views import (
    TagViewSet,
    IngredientRetrieveList,
    UserViewSet,
    RecipeViewSet,
    ShoppingListDownload,
)


router = DefaultRouter()
router.register("tags", TagViewSet)
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("ingredients", IngredientRetrieveList)
router.register(r"users", UserViewSet)

urlpatterns = [
    path("recipes/download_shopping_cart/", ShoppingListDownload.as_view()),
    path("", include(router.urls)),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path(
        "docks/",
        TemplateView.as_view(template_name="redoc.html"),
        name="redoc",
    ),
]
