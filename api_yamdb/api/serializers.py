from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import PasswordField, RefreshToken
from rest_framework_simplejwt.settings import api_settings
from reviews.models import Category, Comment, Genre, Review, Title

from .validators import NotMeValidator, NoUserValidator

User = get_user_model()


class UserSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "username")
        validators = (NotMeValidator(),)


class AdminUserManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        validators = (NotMeValidator(),)


class ChangingUserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        read_only_fields = ("role",)


class CustomTokenObtainPairSerializer(serializers.Serializer):
    username_field = get_user_model().USERNAME_FIELD

    default_error_messages = {
        "no_active_account": _(
            "No active account found with the given credentials"
        )
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField()
        self.fields["confirmation_code"] = PasswordField()

    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            "password": attrs["confirmation_code"],
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise ValidationError()

        data = {}

        refresh = RefreshToken.for_user(self.user)
        data["token"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data

    class Meta:
        validators = (NoUserValidator(),)


# Вторая часть
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Category
        lookup_field = "slug"


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Genre
        lookup_field = "slug"


class TitleListSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = (
            "id",
            "name",
            "year",
            "genre",
            "category",
            "description",
            "rating",
        )
        model = Title


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True, slug_field="slug", queryset=Genre.objects.all()
    )

    class Meta:
        fields = "__all__"
        model = Title


# Третья часть
class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )
    score = serializers.IntegerField(max_value=10, min_value=1)
    title = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = ("id", "text", "score", "title", "author", "pub_date")
        model = Review

    def validate(self, data):
        title = get_object_or_404(
            Title,
            id=self.context["request"].parser_context["kwargs"]["title_id"],
        )
        author = self.context["request"].user
        if (
            self.context["request"].method == "POST"
            and Review.objects.filter(author=author, title=title).exists()
        ):
            raise serializers.ValidationError("Error")
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )

    class Meta:
        fields = ("id", "text", "author", "pub_date")
        model = Comment
