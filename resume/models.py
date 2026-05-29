from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)
    display_name = models.CharField(max_length=200)
    headline = models.CharField(max_length=300, blank=True)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(
        default=False,
        help_text="Only one profile can be featured at a time. This profile will appear first and largest on the landing page."
    )
    photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        help_text="Square photo, 400x400px recommended. Leave blank to use initial avatar."
    )

    def save(self, *args, **kwargs):
        # Ensure only one featured profile at a time
        if self.is_featured:
            UserProfile.objects.filter(is_featured=True).exclude(pk=self.pk).update(is_featured=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name


class SkillCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Skill Categories'

    def __str__(self):
        return self.name


class Skill(models.Model):
    PROFICIENCY_CHOICES = [
        (1, 'Familiar'),
        (2, 'Comfortable'),
        (3, 'Proficient'),
        (4, 'Expert'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='skills')
    proficiency = models.IntegerField(choices=PROFICIENCY_CHOICES, default=2)
    is_core = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['category', 'order']

    def __str__(self):
        return f"{self.name}"


class Project(models.Model):
    """Enhanced project model with screenshots and rich metadata."""

    PROJECT_ROLE_CHOICES = [
        ('SOLO', 'Solo Developer'),
        ('LEAD', 'Lead Developer'),
        ('BACKEND', 'Backend Developer'),
        ('FRONTEND', 'Frontend Developer'),
        ('FULLSTACK', 'Full Stack Developer'),
        ('TEAM', 'Team Member'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    short_description = models.CharField(max_length=300)
    key_skills = models.CharField(
        max_length=300,
        blank=True,
        help_text="3-4 key skills demonstrated by this project: Django, PostgreSQL, Redis"
    )
    result = models.TextField(
        blank=True,
        help_text="What was the measurable outcome? Faster load times? More users? Saved hours?"
    )

    # Rich description fields
    problem = models.TextField(help_text="What problem does this solve?")
    solution = models.TextField(help_text="How did you solve it?")
    architecture_decision = models.TextField(
        blank=True,
        help_text="One key technical decision and why you made it"
    )
    lessons_learned = models.TextField(blank=True)

    # Metadata
    tech_stack = models.CharField(max_length=300, help_text="Comma-separated: Django, PostgreSQL, Redis")
    role = models.CharField(max_length=20, choices=PROJECT_ROLE_CHOICES, default='SOLO')
    completed_date = models.DateField(null=True, blank=True)
    duration_weeks = models.PositiveIntegerField(null=True, blank=True, help_text="How many weeks did it take?")

    # Links
    live_demo_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    swagger_url = models.URLField(blank=True, help_text="API documentation URL if applicable")
    video_demo_url = models.URLField(blank=True, help_text="YouTube or Loom walkthrough URL")

    # Display
    featured = models.BooleanField(default=False)
    is_live = models.BooleanField(default=False, help_text="Is this currently deployed and running?")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-completed_date']
        unique_together = ['user', 'slug']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def tech_list(self):
        return [t.strip() for t in self.tech_stack.split(',')]

    def has_screenshots(self):
        return self.screenshots.exists()

    def primary_screenshot(self):
        return self.screenshots.first()


class ProjectScreenshot(models.Model):
    """Multiple screenshots per project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='screenshots')
    image = models.ImageField(upload_to='project_screenshots/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Screenshot for {self.project.title}"


class CurrentlyLearning(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resource = models.URLField(blank=True)
    started_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-started_date']
        verbose_name_plural = 'Currently Learning'

    def __str__(self):
        return self.topic


class Experience(models.Model):
    EXPERIENCE_TYPES = [
        ('WORK', 'Work Experience'),
        ('FREELANCE', 'Freelance'),
        ('EDUCATION', 'Education'),
        ('VOLUNTEER', 'Volunteer'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=EXPERIENCE_TYPES, default='WORK')
    title = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank if current")
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-start_date']

    def __str__(self):
        return f"{self.title} at {self.organization}"


class BlogPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    excerpt = models.TextField(max_length=500)
    content = models.TextField()
    published_date = models.DateField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    tags = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ['-published_date']
        unique_together = ['user', 'slug']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def tag_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]
