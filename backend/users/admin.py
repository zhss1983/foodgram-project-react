from django.contrib import admin

from .models import User

EMPTY = '-пусто-'


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    empty_value_display = EMPTY


admin.site.register(User, UserAdmin)
