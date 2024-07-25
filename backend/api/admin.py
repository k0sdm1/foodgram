from django.contrib import admin

from receipts.models import Tag, Ingredient, ShoppingList, Follow, Favorite


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'id'
    )
    search_fields = ('name', 'slug',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
        'id',
    )
    search_fields = ('name',)


admin.site.register(ShoppingList)
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
