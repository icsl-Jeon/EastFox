from django.contrib import admin
from .models import Strategist, Filter

# Register your models here.

admin.site.register(Filter)


class StrategistAdmin(admin.ModelAdmin):
    filter_horizontal = ('filter_list',)


admin.site.register(Strategist, StrategistAdmin)
