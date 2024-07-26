from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth import get_user_model


User = get_user_model()


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm

    list_display = ("username", "email", "first_name", "last_name", "avatar")
    fieldsets = (
        (
            ("Основная информация"),
            {
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "avatar",
                ),
            },
        ),
        (
            ("Разрешения"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (("Даты"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                ),
            },
        ),
    )

    search_fields = ("username", "email")


admin.site.register(User, MyUserAdmin)
