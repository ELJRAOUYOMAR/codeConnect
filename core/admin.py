from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, Problem, Solution, Comment, Vote, Tag

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'reputation', 'location', 'show_avatar')
    search_fields = ('user__username', 'location')
    list_filter = ('reputation',)

    def show_avatar(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.photo.url)
        return "No avatar"
    show_avatar.short_description = 'Avatar'

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'difficulty', 'created_by', 'created_at', 'views', 'is_solved')
    list_filter = ('language', 'difficulty', 'is_solved', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags', 'bookmarked_by')
    date_hierarchy = 'created_at'

@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ('problem', 'created_by', 'votes', 'is_accepted', 'created_at')
    list_filter = ('is_accepted', 'created_at')
    search_fields = ('content', 'problem__title', 'created_by__username')
    date_hierarchy = 'created_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('created_by', 'get_target', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'created_by__username')
    date_hierarchy = 'created_at'

    def get_target(self, obj):
        if obj.problem:
            return f"Problem: {obj.problem.title}"
        return f"Solution to: {obj.solution.problem.title}"
    get_target.short_description = 'Target'

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'solution', 'value', 'created_at')
    list_filter = ('value', 'created_at')
    search_fields = ('user__username', 'solution__problem__title')
    date_hierarchy = 'created_at'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'problem_count')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

    def problem_count(self, obj):
        return obj.problems.count()
    problem_count.short_description = 'Problems'