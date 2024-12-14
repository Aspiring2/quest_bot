from django.contrib import admin
from bot.models import User, Location, Task, Scenario, ScenarioStep, UserProgress, Hint


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'telegram_id', 'coins', 'current_scenario')
    search_fields = ('username', 'telegram_id')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'hint_cost', 'order')
    search_fields = ('name',)
    ordering = ('order',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_type', 'location', 'reward', 'text', 'answer', 'order')
    search_fields = ('text', 'answer')
    list_filter = ('task_type', 'location')
    ordering = ('order',)


@admin.register(Hint)
class HintAdmin(admin.ModelAdmin):
    list_display = ('task', 'text', 'cost', 'order')
    search_fields = ('text',)
    list_filter = ('task',)
    ordering = ('order',)


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(ScenarioStep)
class ScenarioStepAdmin(admin.ModelAdmin):
    list_display = ('scenario', 'location', 'order')
    list_filter = ('scenario', 'location')
    ordering = ('order',)


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'scenario', 'current_step', 'is_completed')
    list_filter = ('scenario', 'is_completed')
