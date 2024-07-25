from django.contrib import admin

from django.db.models import Count
from receipts.models import Receipt, IngredientInRecipe


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1
    autocomplete_fields = ['ingredient']
    fields = ['ingredient', 'amount']


class ReceiptAdmin(admin.ModelAdmin):
    inlines = (IngredientInRecipeInline,)
    list_display = (
        'name',
        'id',
        'author',
        'short_text',
        'cooking_time',
        'image',
        'total_favorites'
    )
    readonly_fields = ('total_favorites',)  # Make total_favorites read-only
    fields = (
        'name',
        'author',
        'text',
        'cooking_time',
        'image',
        'tags',
        'total_favorites'
    )
    search_fields = ('name', 'authot__username')
    filter_horizontal = ('tags',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(favorites_count=Count("favorites"))

    def total_favorites(self, instance):
        return instance.favorites_count

    def short_text(self, instance):
        return ((instance.text[:50] + '...')
                if len(instance.text) > 50 else instance.text)

    short_text.short_description = 'Описание'
    total_favorites.short_description = 'Добавлено в избранное раз'
    total_favorites.admin_order_field = 'favorites_count'


admin.site.register(Receipt, ReceiptAdmin)
