from django.urls import path
from . import views
from .views import LandingView

urlpatterns = [
    # User-specific resume pages
    path('', LandingView.as_view(), name='landing'),
    path('<slug:username>/', views.UserHomeView.as_view(), name='user_home'),
    path('<slug:username>/projects/', views.UserProjectListView.as_view(), name='user_project_list'),
    path('<slug:username>/projects/<slug:slug>/', views.UserProjectDetailView.as_view(), name='user_project_detail'),
    path('<slug:username>/blog/', views.UserBlogListView.as_view(), name='user_blog_list'),
    path('<slug:username>/blog/<slug:slug>/', views.UserBlogDetailView.as_view(), name='user_blog_detail'),
    path('<slug:username>/stats/', views.UserStatsView.as_view(), name='user_stats'),
    path('<slug:username>/about/', views.UserAboutView.as_view(), name='user_about'),

    # Health endpoint
    path('health/', views.HealthCheckView.as_view(), name='health'),
]