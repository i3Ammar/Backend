from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from afkat_auth.models import User, Profile, Follow
from django.utils.translation import gettext_lazy as _


# Register your models here.
class AfkatUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ('username','role')}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "usable_password", "password1", "password2"),
            },
        ),
    )
    list_display = ("email",  "is_staff")
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(User, AfkatUserAdmin)
admin.site.register(Profile  )
admin.site.register(Follow)
