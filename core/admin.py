from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Subscription, Tip, Result, Performance, AdminLog

# Custom User admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'role', 'email_verified', 'is_staff', 'is_superuser')
    list_filter = ('role', 'email_verified', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'email_verified')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'email_verified')}),
    )

from django.contrib import admin
from .models import Plan, Subscription

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days')
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('price',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date')
    search_fields = ('user__username', 'plan__name')
    list_filter = ('status', 'plan__name')
    ordering = ('-start_date',)



@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = ('race_id', 'date', 'track', 'race_no', 'race_name', 'region', 'tip_type', 'uploaded_file')

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('race_id', 'date', 'winner', 'quinella_result', 'processed_at', 'uploaded_file')


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'region', 'tip_type', 'wins', 'losses', 'scratched', 'hit_rate')

@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action', 'entity_type', 'entity_id', 'timestamp')
