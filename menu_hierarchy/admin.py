from django.contrib import admin
from .models import MenuItem

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'depth', 'parent_name', 'created_at', 'updated_at')
    list_filter = ('depth', 'created_at', 'updated_at')
    search_fields = ('name', 'parent__name')
    date_hierarchy = 'created_at'
    ordering = ('name', 'depth', 'parent__name')

    def parent_name(self, obj):
        return obj.parent_name()
    
    parent_name.short_description = 'Parent Name'
    parent_name.admin_order_field = 'parent__name'

admin.site.register(MenuItem, MenuItemAdmin)