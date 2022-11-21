from django.contrib import admin
from .models import Timeline, Screener, Segment, ScreenerApplication

# Register your models here.

admin.site.register(Screener)


class ScreenerAdmin(admin.ModelAdmin):
    filter_horizontal = ('screener_list',)


class SegmentAdmin(admin.ModelAdmin):
    filter_horizontal = ('asset_list',)


admin.site.register(Timeline, ScreenerAdmin)
admin.site.register(Segment, SegmentAdmin)
admin.site.register(ScreenerApplication)
