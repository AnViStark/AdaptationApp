from django.contrib import admin

from .models import Review, TrainerSubmission, TrainerTask


@admin.register(TrainerTask)
class TrainerTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'points_reward', 'is_active')
    list_filter = ('is_active',)


@admin.register(TrainerSubmission)
class TrainerSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'status', 'submitted_at')
    list_filter = ('status',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('submission', 'mentor', 'result', 'reviewed_at')
