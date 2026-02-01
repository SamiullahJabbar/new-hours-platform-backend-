from rest_framework import viewsets
from .models import User, Subscription, Tip, Result, Performance
from .serializers import UserSerializer, SubscriptionSerializer, TipSerializer, ResultSerializer, PerformanceSerializer

from .serializers import RegisterSerializer, LoginSerializer

import csv, json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Tip, Result
from django.contrib.auth import authenticate



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

class TipViewSet(viewsets.ModelViewSet):
    queryset = Tip.objects.all()
    serializer_class = TipSerializer

class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer



class TipsImportView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        if file.name.endswith('.csv'):
            import csv
            decoded = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded)
            invalid_rows = []
            for row in reader:
                try:
                    Tip.objects.create(
                        race_id=row['race_id'],
                        date=row['date'],
                        track=row['track'].strip().upper(),
                        race_no=row['race_no'],
                        race_name=row['race_name'],
                        region=row['region'],
                        tip_type=row['tip_type'],
                        data={
                            "win_horse_no": row['win_horse_no'],
                            "win_horse_name": row['win_horse_name'],
                            "ranking": row['ranking'].split(',')
                        },
                        uploaded_file=file
                    )
                except Exception as e:
                    invalid_rows.append(row)
            return Response({"success": True, "invalid_rows": invalid_rows})

        elif file.name.endswith('.json'):
            import json
            data = json.load(file)
            invalid = []
            for item in data:
                try:
                    Tip.objects.create(
                        race_id=item['race_id'],
                        date=item['date'],
                        track=item['track'].strip().upper(),
                        race_no=item['race_no'],
                        race_name=item['race_name'],
                        region=item['region'],
                        tip_type=item['tip_type'],
                        data=item['data'],
                        uploaded_file=file
                    )
                except Exception:
                    invalid.append(item)
            return Response({"success": True, "invalid": invalid})

        return Response({"error": "Unsupported format"}, status=400)


class ResultsImportView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        import json
        data = json.load(file)
        for item in data:
            result = Result.objects.create(
                race_id=item['race_id'],
                date=item['date'],
                winner=item['winner'],
                quinella_result=item.get('quinella_result'),
                scratched=item.get('scratched', []),
                grading_result={},
                uploaded_file=file
            )
            # Auto-grading logic
            tips = Tip.objects.filter(race_id=result.race_id)
            for tip in tips:
                grading = {}
                if tip.data.get("win_horse_no") == result.winner:
                    grading['status'] = "WIN"
                elif tip.data.get("win_horse_no") in result.scratched:
                    grading['status'] = "SCRATCHED"
                else:
                    grading['status'] = "LOSE"
                result.grading_result = grading
                result.save()

        return Response({"success": True, "message": "Results imported and graded"})



from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"success": True, "message": "Registration successful"}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # 1. Email ke zariye user ko find karo
            try:
                user_obj = User.objects.get(email=email)
                # 2. Django ke authenticate ko username aur password pass karo
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

            if user is not None:
                if user.is_active:
                    # Token generate karo
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        "success": True,
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "username": user.username,
                            "role": user.role,
                            "email_verified": user.email_verified
                        }
                    })
                return Response({"error": "Account is disabled"}, status=status.HTTP_403_FORBIDDEN)
            
            # Agar password galat ho ya user na mile
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






from rest_framework import viewsets, permissions
from .models import Plan, Subscription
from .serializers import PlanSerializer, SubscriptionSerializer

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAdminUser]  # only admin can create/update plans
    # GET allowed for all users
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Subscription.objects.all()
        return Subscription.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)





from django.db.models import Count, Q, F
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Tip, Result

class PerformanceView(APIView):
    def get(self, request):
        stats = []

        # group by region
        regions = Result.objects.values_list('region', flat=True).distinct()
        for region in regions:
            tips = Tip.objects.filter(region=region)
            results = Result.objects.filter(region=region)

            wins = 0
            losses = 0
            scratched = 0

            for tip in tips:
                result = results.filter(race_id=tip.race_id).first()
                if result:
                    horse = tip.data.get("horse")
                    if horse == result.winner:
                        wins += 1
                    elif horse in result.scratched:
                        scratched += 1
                    else:
                        losses += 1

            hit_rate = (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0

            stats.append({
                "region": region,
                "wins": wins,
                "losses": losses,
                "scratched": scratched,
                "hit_rate": hit_rate
            })

        return Response(stats)



from rest_framework import generics, permissions
from .serializers import ProfileSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Logged-in user ka object return karega
        return self.request.user

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        # Patch allow karta hai ke agar sirf username bhejo toh email update na ho
        return self.partial_update(request, *args, **kwargs)