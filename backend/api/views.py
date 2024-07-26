import os

from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from djoser import views as djoser_views
from rest_framework.response import Response
from rest_framework import viewsets, generics
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly)

from api.paginators import LimitPagination
from api.permissions import IsAuthorOrReadOnly
from receipts.models import (
    Tag,
    Receipt,
    Ingredient,
    Follow,
    ShoppingList,
    Favorite)
from api.filters import IngredientsFilter, RecipesFilter
from api.serializers import (
    TagSerializer,
    IngredientSerializer,
    IngredientInRecipeSerializer,
    RecipeSerializer,
    RecipeSerializerGetRequest,
    UserAvatarSerializer,
    SubscribeUserSerializer,
    RecipeSerializerGetRequestBasic)

from shortlink import short_link
from api.shopping_list import generate_html, generate_file, get_file


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientRetrieveList(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientsFilter
    filterset_fields = ('name', )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipesFilter
    filterset_fields = (
        'author', 'tags', 'is_favorited', 'is_in_shopping_cart')
    pagination_class = LimitPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_serializer_class(self):
        """Определяет какой сериализатор будет использоваться
        для разных типов запроса."""
        if self.request.method == 'GET':
            return RecipeSerializerGetRequest
        return RecipeSerializer

    @action(
        detail=True,
        url_path='favorite',
        methods=('post', 'delete')
    )
    def post_delete_favorite_recipe(self, request, pk):
        this_recipe = get_object_or_404(Receipt, pk=pk)
        if request.method == 'POST':
            favorited, created = Favorite.objects.get_or_create(
                user=request.user, receipt=this_recipe)
            if not created:
                return Response(
                    {'favorite':
                     (f'Рецепт {this_recipe} уже в избранном '
                      f'у пользователя {request.user}')},
                    status=status.HTTP_400_BAD_REQUEST)
            return Response(RecipeSerializerGetRequestBasic(this_recipe).data,
                            status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            favorited = request.user.favorites.filter(receipt=this_recipe)
            if not favorited.exists():
                return Response(
                    {'favorite':
                     (f'Рецепта {this_recipe} нет в избранном '
                      f'у пользователя {request.user}')},
                    status=status.HTTP_400_BAD_REQUEST)
            favorited.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        url_path='shopping_cart',
        methods=('post', 'delete')
    )
    def shopping_list_add_remove_recipe(self, request, pk):
        this_recipe = get_object_or_404(Receipt, pk=pk)
        if request.method == 'POST':
            shopping, created = ShoppingList.objects.get_or_create(
                user=request.user, receipt=this_recipe)
            if not created:
                return Response(
                    {'shopping_cart':
                     (f'Рецепт {this_recipe} уже в списке покупок '
                      f'у пользователя {request.user}')},
                    status=status.HTTP_400_BAD_REQUEST)
            return Response(
                RecipeSerializerGetRequestBasic(this_recipe).data,
                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            shopping = request.user.shopping_lists.filter(receipt=this_recipe)
            if not shopping.exists():
                return Response(
                    {'shopping_cart':
                     (f'Рецепта {this_recipe} нет в списке покупок '
                      f'у пользователя {request.user}')},
                    status=status.HTTP_400_BAD_REQUEST)
            shopping.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('get',),
        url_path='get-link',
        url_name='get_short_link'
    )
    def get_short_link(self, request, pk):
        get_object_or_404(Receipt, pk=pk)
        short = short_link.get_or_create_short_link(f'/recipes/{pk}')
        return Response(
            {'short-link': request.build_absolute_uri(f'/s/{short}')},
            status=status.HTTP_200_OK
        )


class RecipeEdit(generics.RetrieveAPIView):
    serializer_class = RecipeSerializerGetRequest
    permission_classes = (IsAuthorOrReadOnly, )

    def get_object(self):
        return get_object_or_404(Receipt, self.kwargs.get('pk'))


class UserViewSet(djoser_views.UserViewSet):
    """Класс работы с объектами пользователя."""

    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitPagination

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def pagination_for_query(self, request, queryset, serializer_to_use):
        """Вспомогательный метод пагинации списка объектов query."""
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page:
            serializer = serializer_to_use(
                context={"request": request},
                instance=page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializer_to_use(queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def list(self, request, *args, **kwargs):
        return self.pagination_for_query(
            request=request, queryset=User.objects.all(),
            serializer_to_use=self.get_serializer().__class__)

    @action(
        detail=False,
        methods=('get',),
        url_path=r'subscriptions',
        url_name='all_user_subscriptions',
        permission_classes=(IsAuthenticated, )
    )
    def get_my_subscriptions(self, request):
        return self.pagination_for_query(
            request=request,
            queryset=User.objects.filter(followings__user=request.user).all(),
            serializer_to_use=SubscribeUserSerializer)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='subscribe',
        url_name='user_subscription_handler',
        permission_classes=(IsAuthenticated, )
    )
    def subscribe_unsubscribe(self, request, id):
        user_to_subscribe = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            if user_to_subscribe == request.user:
                return Response(
                    {'subscription': 'Нельзя подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST)
            subscription, created = Follow.objects.get_or_create(
                user=request.user, following=user_to_subscribe)
            if not created:
                return Response(
                    {'subscription':
                     (f'Пользователь {request.user} уже подписан '
                      f'на пользователя {user_to_subscribe}')},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscribeUserSerializer(
                context={"request": request}, instance=user_to_subscribe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription = Follow.objects.filter(
                user=request.user, following=user_to_subscribe)
            if not subscription.exists():
                return Response(
                    {'subscription': (f'Пользователь {request.user} не был '
                                      f'подписан на {user_to_subscribe}')},
                    status=status.HTTP_400_BAD_REQUEST)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('put', 'delete'),
        url_path='me/avatar',
        url_name='user_avatar',
        permission_classes=(IsAuthenticated,)
    )
    def put_delete_user_avatar(self, request):
        if request.method == 'PUT':
            serializer = UserAvatarSerializer(request.user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            if request.user.avatar:
                avatar_path = os.path.join(
                    settings.MEDIA_ROOT, str(request.user.avatar))
                if default_storage.exists(avatar_path):
                    default_storage.delete(avatar_path)
                request.user.avatar = None
                request.user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ShoppingListDownload(generics.ListAPIView):
    """Возвращает вайл со списком покупок.
    PDF для Linux и HTML для остальных платформ."""

    serializer_class = IngredientInRecipeSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return self.request.user.shopping_lists.select_related(
            'receipt__ingredientinrecipe__ingredient').values(
            'receipt__ingredientinrecipe__ingredient__pk',
            'receipt__ingredientinrecipe__ingredient__name',
            'receipt__ingredientinrecipe__ingredient__measurement_unit'
        ).annotate(total_ingredients=Sum('receipt__ingredientinrecipe__amount')
                   ).order_by('receipt__ingredientinrecipe__ingredient__name')

    def get(self, request, *args, **kwargs):
        summ_list = self.get_queryset()
        result_list = []
        for summ in summ_list:
            result_list.append({
                'name': summ[
                    'receipt__ingredientinrecipe__ingredient__name'],
                'measurement_unit': summ[
                    ('receipt__ingredientinrecipe__'
                     'ingredient__measurement_unit')],
                'total_ingredients': summ['total_ingredients'],
            })
        return get_file(generate_file(generate_html(result_list)))
