from django.db import transaction
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer

from authentication.models import GENDER_SELECTION
from authentication.models import User


class CustomRegisterSerializer(RegisterSerializer):
    gender = serializers.ChoiceField(
        choices=GENDER_SELECTION, required=False, allow_null=True)
    phone_number = serializers.CharField(
        max_length=30, required=False, allow_null=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_null=True)
    specialty = serializers.JSONField(required=False)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)

    # Define transaction.atomic to rollback the save operation in case of error
    @transaction.atomic
    def save(self, request):
        user = super().save(request)
        user.gender = self.data.get('gender')
        user.phone_number = self.data.get('phone_number')
        user.birth_date = self.data.get('birth_date')
        user.bio = self.data.get('bio')
        user.specialty = self.data.get('specialty')
        user.price = self.data.get('price')
        user.save()
        return user


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    # score = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'pk',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'gender',
            'birth_date',
            'bio',
            'specialty',
            'price',
        )
        read_only_fields = ('pk', 'email',)

    def get_score(self, obj):
        pass
