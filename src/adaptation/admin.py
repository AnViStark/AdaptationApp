from django.contrib import admin

from .models import (
    AdaptationRoute,
    AdaptationTemplate,
    Stage,
    Task,
    UserTaskProgress,
)


class StageInline(admin.TabularInline):
    model = Stage
    extra = 1
    ordering = ['order']


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1
    ordering = ['order']
    fields = ('title', 'description', 'order', 'article', 'trainer_task')


@admin.register(AdaptationTemplate)
class AdaptationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'target_role', 'department', 'project', 'stage_count', 'task_count', 'created_at')
    list_filter = ('target_role', 'department')
    search_fields = ('name',)
    inlines = [StageInline]


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('title', 'template', 'order')
    list_filter = ('template',)
    inlines = [TaskInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'stage', 'order', 'article', 'trainer_task')
    list_filter = ('stage__template',)
    search_fields = ('title',)


@admin.register(AdaptationRoute)
class AdaptationRouteAdmin(admin.ModelAdmin):
    list_display = ('user', 'template', 'mentor', 'started_at', 'is_active', 'progress_percent')
    list_filter = ('is_active', 'template')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user', 'mentor', 'assigned_by')


@admin.register(UserTaskProgress)
class UserTaskProgressAdmin(admin.ModelAdmin):
    list_display = ('route', 'task', 'completed', 'completed_at')
    list_filter = ('completed',)
    search_fields = ('route__user__username',)
