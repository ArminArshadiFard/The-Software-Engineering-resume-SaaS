from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    UserProfile, SkillCategory, Skill,
    Project, CurrentlyLearning, BlogPost, ProjectScreenshot
)


# ==========================================
# USER PROFILE INLINE ON USER ADMIN
# ==========================================

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'slug', 'display_name', 'headline', 'bio',
        'email', 'github_url', 'linkedin_url',
        'is_active', 'is_featured'
    )


class CustomUserAdmin(UserAdmin):
    """Extended User admin that includes the UserProfile inline."""
    inlines = [UserProfileInline]


# Unregister default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Inline for Project Screenshots
class ProjectScreenshotInline(admin.TabularInline):
    model = ProjectScreenshot
    extra = 1
    fields = ['image', 'caption', 'order']

# ==========================================
# BASE ADMIN FOR USER-FILTERED MODELS
# ==========================================

class UserFilteredAdmin(admin.ModelAdmin):
    """
    Base admin for models owned by a user.
    - Normal users only see their own data.
    - Superusers see everything.
    - When a normal user creates something, it auto-assigns to them.
    - When a superuser creates something, they can choose the owner.
    """

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Only show the user field to superusers
        if not request.user.is_superuser:
            if 'user' in form.base_fields:
                form.base_fields['user'].widget = admin.widgets.HiddenInput()
        return form

    def save_model(self, request, obj, form, change):
        # For non-superusers, always assign to themselves
        if not request.user.is_superuser:
            obj.user = request.user
        # For superusers, use whatever user was selected (or default to themselves)
        elif not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)


# ==========================================
# SKILL CATEGORIES
# ==========================================

@admin.register(SkillCategory)
class SkillCategoryAdmin(UserFilteredAdmin):
    list_display = ['name', 'user', 'order']
    list_filter = ['user']
    search_fields = ['name']


# ==========================================
# SKILLS
# ==========================================

@admin.register(Skill)
class SkillAdmin(UserFilteredAdmin):
    list_display = ['name', 'category', 'user', 'proficiency', 'is_core']
    list_filter = ['category', 'proficiency', 'is_core']
    search_fields = ['name']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Only show categories that belong to the current user."""
        if db_field.name == 'category':
            if request.user.is_superuser:
                kwargs['queryset'] = SkillCategory.objects.all()
            else:
                kwargs['queryset'] = SkillCategory.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ==========================================
# PROJECTS
# ==========================================

@admin.register(Project)
class ProjectAdmin(UserFilteredAdmin):
    list_display = ['title', 'user', 'role', 'featured', 'is_live', 'completed_date']
    list_filter = ['featured', 'is_live', 'role']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'short_description', 'tech_stack']
    inlines = [ProjectScreenshotInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'title', 'slug', 'short_description', 'role')
        }),
        ('Content', {
            'fields': ('problem', 'solution', 'architecture_decision', 'lessons_learned')
        }),
        ('Tech Details', {
            'fields': ('tech_stack', 'duration_weeks', 'completed_date')
        }),
        ('Links', {
            'fields': ('live_demo_url', 'github_url', 'swagger_url', 'video_demo_url')
        }),
        ('Display', {
            'fields': ('featured', 'is_live', 'order')
        }),
    )

# ==========================================
# CURRENTLY LEARNING
# ==========================================

@admin.register(CurrentlyLearning)
class CurrentlyLearningAdmin(UserFilteredAdmin):
    list_display = ['topic', 'user', 'is_active', 'started_date']
    list_filter = ['is_active']


# ==========================================
# BLOG POSTS
# ==========================================

@admin.register(BlogPost)
class BlogPostAdmin(UserFilteredAdmin):
    list_display = ['title', 'user', 'is_published', 'published_date']
    list_filter = ['is_published']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'excerpt']