from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .serializers import UserSerializer, UserSerializerWithToken


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # In addition to tokens, the belows included in login response
        data = super().validate(attrs)
        serializer = UserSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v
        return data


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    return Response(UserSerializer(request.user).data)
