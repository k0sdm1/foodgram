import django_filters
from django.db.models import Q

from receipts.models import Ingredient, Receipt, Tag


class IngredientsFilter(django_filters.FilterSet):
    """Класс фильтров для ингредиентов."""

    name = django_filters.CharFilter(
        field_name="name", lookup_expr="istartswith"
    )

    class Meta:
        model = Ingredient
        fields = ("name",)


class RecipesFilter(django_filters.FilterSet):
    """Класс фильтров для рецептов."""

    author = django_filters.CharFilter(field_name="author_id")
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
        method="filter_tags",
    )
    is_favorited = django_filters.NumberFilter(method="filter_is_favorited")
    is_in_shopping_cart = django_filters.NumberFilter(
        method="filter_is_in_shopping_cart"
    )

    class Meta:
        model = Receipt
        fields = ("author", "tags", "is_favorited", "is_in_shopping_cart")

    def filter_tags(self, queryset, name, value):
        """Фильтр для тэгов с использованием OR логики."""
        if value:
            query = Q()
            for tag in value:
                query |= Q(tags=tag)
            return queryset.filter(query).distinct()
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        """Фильтр для избранных рецептов."""
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(favorites__user=user)
        elif user.is_authenticated and not value:
            return queryset.exclude(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр рецептов в списке покупок."""
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(shopping_lists__user=user)
        elif user.is_authenticated and not value:
            return queryset.exclude(shopping_lists__user=user)
        return queryset
