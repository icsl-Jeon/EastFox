from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    is_admin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'is_admin']

    def get_name(self, obj: User):
        name = obj.first_name
        if name == '':
            name = obj.email
        return name

    def get_is_admin(self, obj: User):
        return obj.is_staff


class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ['token']

    def get_token(self, obj: User):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)
