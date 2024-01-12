from django.contrib import admin

from announcement.models import House, Photo

# Register your models here.

class PhotoInline(admin.TabularInline):

    model = Photo


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):

    inlines = (PhotoInline,)

    fieldsets = (
        (
            "Basic Info",
            {"fields": ("type", "prix", "disponibilité", "pour", "ville", "address", )},
        ),
        
    )

    ordering = ("type", "prix")

    list_display = (
        "type",
        "pour",
        "ville",
        "prix",
        
        "count_photos",
    )

    list_filter = (
        "type",
        "pour",
        "ville",
        "prix",
    )

    search_fields = ("=city", "^host__username")




    def count_photos(self, obj):
        return obj.photos.count()

    count_photos.short_disponibilité = "Photo Count"