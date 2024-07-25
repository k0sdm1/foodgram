import platform
from io import BytesIO

from django.http import HttpResponse

if platform.system() == 'Linux':
    from weasyprint import HTML


def generate_html(result_list):
    """HTML шаблон для списка покупок."""
    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Список покупок</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { text-align: center; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>Список покупок</h1>
        <table>
            <tr>
                <th>#</th>
                <th>Ингредиент</th>
                <th>Единица измерения</th>
                <th>Количество</th>
            </tr>
    """
    for i, item in enumerate(result_list, start=1):
        html += f"""
            <tr>
                <td>{i}</td>
                <td>{item['name']}</td>
                <td>{item['measurement_unit']}</td>
                <td>{item['total_ingredients']}</td>
            </tr>
        """
    html += """
        </table>
    </body>
    </html>
    """
    return html


def generate_file(html_content):
    """Возвращает PDF файл или html текст в зависимости от платформы."""
    if platform.system() == 'Linux':
        pdf_file = BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)
        pdf_file.seek(0)
        return pdf_file
    return html_content


def get_file(file):
    """Возвращает ответ с файлом PDF или HTML в зависимости от платформы."""
    if platform.system() == 'Linux':
        response = HttpResponse(file, content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.pdf"')
        return response
    response = HttpResponse(file, content_type='text/html')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_list.html"')
    return response
