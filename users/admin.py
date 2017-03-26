from django.contrib import admin
from users import models


class AppUserAdmin(admin.ModelAdmin):
    list_display = ('_id', 'fbid',)


class ReadingAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'calories', 'timestamp')
    list_filter = ('product', 'user',)
    ordering = ('calories',)
    list_per_page = 200
    date_hierarchy = 'timestamp'
    search_fields = ('user', 'product',)


admin.site.register(models.AppUser, AppUserAdmin)
admin.site.register(models.Reading, ReadingAdmin)
