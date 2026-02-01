from django.db import models
from django.contrib.auth.models import AbstractUser

# User model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('CONTENT_EDITOR', 'Content Editor'),
        ('SUPPORT', 'Support'),
        ('USER', 'User'),
    ]
    # Email ko unique rakha hai taaki login logic fail na ho
    email = models.EmailField(unique=True) 
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER')
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"

from django.db import models
from django.conf import settings

class Plan(models.Model):
    PLAN_CHOICES = [
        ('FREE', 'Free'),
        ('BASIC', 'Basic'),
        ('PREMIUM', 'Premium'),
        ('TR', 'Track Region'),
        ('INT', 'International'),
    ]
    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)  # monthly price
    duration_days = models.IntegerField(default=30)  # plan validity

    def __str__(self):
        return f"{self.name} ({self.price})"


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('CANCELED', 'Canceled'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey('Plan', on_delete=models.SET_NULL, null=True, blank=True, related_name="subscriptions")
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')

    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'No Plan'} ({self.status})"



# Tips model
class Tip(models.Model):
    race_id = models.CharField(max_length=100)
    date = models.DateField()
    track = models.CharField(max_length=100)
    race_no = models.IntegerField()
    race_name = models.CharField(max_length=200)
    region = models.CharField(max_length=10)
    tip_type = models.CharField(max_length=20)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    # NEW FIELD: uploaded file reference
    uploaded_file = models.FileField(upload_to='uploads/tips/', null=True, blank=True)

    def __str__(self):
        return f"{self.race_name} ({self.date})"


# Results model
from django.db import models

class Result(models.Model):
    race_id = models.CharField(max_length=100)
    date = models.DateField()
    region = models.CharField(max_length=100, null=True, blank=True)  # 👈 Added field
    track = models.CharField(max_length=100, null=True, blank=True)   # 👈 Optional, useful for race info
    race_name = models.CharField(max_length=150, null=True, blank=True)  # 👈 Optional descriptive name

    winner = models.CharField(max_length=50)
    quinella_result = models.CharField(max_length=50, null=True, blank=True)

    scratched = models.JSONField(default=list)  # list of scratched horses
    grading_result = models.JSONField(null=True, blank=True)  # race grading/classification

    processed_at = models.DateTimeField(auto_now_add=True)

    # NEW FIELD: uploaded file reference
    uploaded_file = models.FileField(upload_to='uploads/results/', null=True, blank=True)

    def __str__(self):
        return f"{self.race_id} - {self.date} ({self.region})"

# Performance model
class Performance(models.Model):
    date = models.DateField()
    region = models.CharField(max_length=10)
    tip_type = models.CharField(max_length=20)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    scratched = models.IntegerField(default=0)
    hit_rate = models.FloatField(default=0.0)

# Admin Logs
class AdminLog(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)






