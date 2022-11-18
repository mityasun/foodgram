from django.contrib import admin

from .models import Cart, Favorite, Ingredients, Recipes, Tags


class TagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('id', 'name', 'color', 'slug')
    list_filter = ('name', 'color')
    prepopulated_fields = {'slug': ('name',)}


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('id', 'name')
    list_filter = ('measurement_unit',)


class IngredientAmount(admin.TabularInline):
    model = Recipes.ingredients.through


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author')
    search_fields = ('id', 'name', 'tags', 'ingredients')
    list_filter = ('tags', 'author')
    inlines = [IngredientAmount]


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('recipe',)


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('recipe',)


admin.site.register(Tags, TagsAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Cart, CartAdmin)
