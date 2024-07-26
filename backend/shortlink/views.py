from django.shortcuts import redirect, render

from shortlink import short_link
from shortlink.exceptions import ShortLinkDoesNotExist


def reverse_short(request, link):
    try:
        print(link, "\n", short_link.get_full_link(link))
        return redirect(short_link.get_full_link(link))
    except ShortLinkDoesNotExist:
        return render(request, "404.html", status=404)
