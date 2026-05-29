from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, View
from django.http import JsonResponse, Http404
from django.contrib.auth.models import User
from .models import (
    UserProfile, SkillCategory, Project,
    CurrentlyLearning, BlogPost
)
import time


class UserMixin:
    """Base mixin that fetches the user profile from the URL slug."""

    def dispatch(self, request, *args, **kwargs):
        username_slug = kwargs.get('username')
        self.profile = get_object_or_404(
            UserProfile.objects.select_related('user'),
            slug=username_slug,
            is_active=True
        )
        self.resume_user = self.profile.user
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        context['resume_user'] = self.resume_user
        return context


class UserHomeView(UserMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.resume_user
        context['featured_projects'] = Project.objects.filter(
            user=user, featured=True
        ).order_by('order')[:3]
        context['skill_categories'] = SkillCategory.objects.filter(
            user=user
        ).prefetch_related('skills')
        context['currently_learning'] = CurrentlyLearning.objects.filter(
            user=user, is_active=True
        )[:3]
        return context


class UserProjectListView(UserMixin, ListView):
    template_name = 'project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.filter(user=self.resume_user)


class UserProjectDetailView(UserMixin, DetailView):
    template_name = 'project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        return Project.objects.filter(user=self.resume_user)


class UserBlogListView(UserMixin, ListView):
    template_name = 'blog_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return BlogPost.objects.filter(
            user=self.resume_user,
            is_published=True
        )


class UserBlogDetailView(UserMixin, DetailView):
    template_name = 'blog_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return BlogPost.objects.filter(
            user=self.resume_user,
            is_published=True
        )


class UserStatsView(UserMixin, TemplateView):
    template_name = 'stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.resume_user
        context['total_projects'] = Project.objects.filter(user=user).count()
        context['total_posts'] = BlogPost.objects.filter(user=user, is_published=True).count()
        return context


class UserAboutView(UserMixin, TemplateView):
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['currently_learning'] = CurrentlyLearning.objects.filter(
            user=self.resume_user,
            is_active=True
        )
        return context


class HealthCheckView(View):
    def get(self, request):
        return JsonResponse({'status': 'healthy'})


class LandingView(TemplateView):
    """Public directory of all resume profiles with featured profile."""
    template_name = 'landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get featured profile (or None)
        context['featured_profile'] = UserProfile.objects.filter(
            is_active=True,
            is_featured=True
        ).first()

        # Get all active profiles except the featured one
        all_profiles = UserProfile.objects.filter(is_active=True).select_related('user')

        if context['featured_profile']:
            context['profiles'] = all_profiles.exclude(pk=context['featured_profile'].pk)
        else:
            context['profiles'] = all_profiles

        return context