from django.contrib import admin

from shortlink.models import ShortLink


class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ("full_url", "short_link")


admin.site.register(ShortLink, ShortLinkAdmin)
