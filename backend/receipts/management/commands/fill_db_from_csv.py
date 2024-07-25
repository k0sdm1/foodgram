from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from pathlib import Path
import pandas
from receipts.models import Ingredient


FILES_WITH_DATA = {
    'ingredients': Ingredient,
}


class Command(BaseCommand):
    help = 'Команда заполняет базу данных записями из CSV таблицы'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help='путь к директории где расположен файл CSV',
            required=True
        )

    def handle(self, *args, **options):
        root_path = Path(__file__).resolve().parents[4]
        custom_path = options['path']
        path_with_files = root_path.joinpath(custom_path)

        print(f'Path to CSV files: {path_with_files}')

        for file_name, model in FILES_WITH_DATA.items():
            csv_file_path = path_with_files.joinpath(f'{file_name}.csv')
            if not csv_file_path.exists():
                print(f'File {csv_file_path} does not exist')
                continue

            csv_file = pandas.read_csv(
                csv_file_path,
                header=None,
            )
            items = []
            for row in csv_file.itertuples(index=False):
                dict_items = {
                    'name': row[0],
                    'measurement_unit': row[1]
                }
                items.append(model(**dict_items))

            try:
                model.objects.bulk_create(items)
                print(f'Successfully imported data from {csv_file_path}')
            except IntegrityError as error:
                print(f'Error with file {file_name} -- {error}')
