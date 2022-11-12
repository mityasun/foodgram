from django.contrib import admin

from .models import Tags, Ingredients


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('name', 'measurement_unit')


admin.site.register(Tags, RecipesAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
