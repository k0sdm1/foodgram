from random import choice

from django.db import IntegrityError

from shortlink.models import ShortLink
from shortlink.exceptions import UnableToCreateLink, ShortLinkDoesNotExist


LINK_LENGTH = 7
LINK_CREATION_ATTEMPTS = 3
ALLOWED_CHARS = 'ABCDEFGHJKLMNOPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz234567890'


def get_random(tries=0) -> str:
    length = LINK_LENGTH + tries
    return ''.join(choice(ALLOWED_CHARS) for _ in range(length))


def get_or_create_short_link(url: str) -> str:
    """Создает или получает объект короткой ссылки по полному url.
    Возвращает короткую ссылку.
    """
    for tries in range(LINK_CREATION_ATTEMPTS):
        try:
            short = get_random(tries)
            link_obj, created = ShortLink.objects.get_or_create(full_url=url)
            if not created:
                return link_obj.short_link
            link_obj.short_link = short
            link_obj.save()
            return link_obj.short_link
        except IntegrityError:
            continue
    raise UnableToCreateLink(
        'Не удалось создать уникальную ссылку.')


def get_full_link(link: str) -> str:
    """Возвращает полную ссылку из короткой."""
    try:
        url = ShortLink.objects.get(short_link__exact=link)
    except ShortLink.DoesNotExist:
        raise ShortLinkDoesNotExist('Такой короткой ссылки не существует.')
    return url.full_url
