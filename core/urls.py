from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    UserViewSet, SubscriptionViewSet, TipViewSet, ResultViewSet, PerformanceViewSet,
    RegisterView, LoginView, PerformanceView, ProfileView,PlanViewSet
)

router = DefaultRouter()
# User-facing endpoints
router.register(r'users', UserViewSet)
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'tips', TipViewSet)
router.register(r'results', ResultViewSet)
# router.register(r'performance', PerformanceViewSet)

urlpatterns = [
    # CRUD endpoints via router
    path('', include(router.urls)),

    # Auth endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User profile
    path('auth/profile/', ProfileView.as_view(), name='user-profile'),

    # Performance summary endpoint (user-facing)
    path('performance-summary/', PerformanceView.as_view(), name='performance-summary'),
    path('plans/', PlanViewSet.as_view({'get': 'list'}), name='plan-list'),
]
