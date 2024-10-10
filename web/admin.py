from django.contrib import admin

# create admin for the models
from .models import House, Appliance, Program


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Appliance)
class ApplianceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'house')
    raw_id_fields = 'house',

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'time_in_minutes', 'appliance', 'appliance__house')

    raw_id_fields = 'appliance',
