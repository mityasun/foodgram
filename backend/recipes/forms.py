from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet


class ValidateFormSet(BaseInlineFormSet):
    """Валидируем наличие ингредиентов в рецепте"""

    def clean(self):
        super(ValidateFormSet, self).clean()
        for cleaned_data in self.cleaned_data:
            if not cleaned_data:
                raise ValidationError(
                    'Нужен хотя бы один ингредиент для рецепта'
                )
