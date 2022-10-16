from django.contrib import admin
from .models import Strategist, Filter, Segment, FilterApplication

# Register your models here.

admin.site.register(Filter)


class StrategistAdmin(admin.ModelAdmin):
    filter_horizontal = ('filter_list',)


class SegmentAdmin(admin.ModelAdmin):
    filter_horizontal = ('asset_list',)


admin.site.register(Strategist, StrategistAdmin)
admin.site.register(Segment, SegmentAdmin)
admin.site.register(FilterApplication)
