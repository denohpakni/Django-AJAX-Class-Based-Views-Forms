from django.contrib import admin
from halls.models import Hall, Video
# Register your models here.

class HallName(admin.ModelAdmin):
    list_display = ('title', 'user')

admin.site.register(Hall, HallName)
admin.site.register(Video)
