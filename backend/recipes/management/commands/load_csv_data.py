import datetime
from csv import DictReader

from django.core.management import BaseCommand

from recipes.models import Ingredients


def import_csv_data():
    start_time = datetime.datetime.now()

    csv_files = (
        (Ingredients, '../data/ingredients.csv'),
    )

    for model, file in csv_files:
        print(f"Загрузка данных таблицы {file} началась.")
        for row in DictReader(open(file, encoding='utf-8')):
            data = model(
                name=row['name'],
                measurement_unit=row['measurement_unit']
            )
            data.save()
        print(
            f"Загрузка данных таблицы {file} завершена успешно.")

    print(f"Загрузка данных завершена за"
          f" {(datetime.datetime.now() - start_time).total_seconds()} "
          f"сек.")


class Command(BaseCommand):
    help = ("Загрузка data из data/*.csv."
            "Запуск: python manage.py load_csv_data."
            "Подробнее об импорте в README.md.")

    def handle(self, *args, **options):
        print("Старт импорта")

        try:
            import_csv_data()

        except Exception as error:
            print(f"Сбой в работе импорта: {error}.")

        finally:
            print("Завершена работа импорта.")
