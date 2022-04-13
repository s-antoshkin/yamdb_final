import random

from api.filters import TitleFilter
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase
from reviews.models import Category, Comment, Genre, Review, Title

from .pagination import PageNumberPagination5
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorModeratorAdminOrReadOnly)
from .serializers import (AdminUserManagementSerializer, CategorySerializer,
                          ChangingUserDataSerializer, CommentSerializer,
                          CustomTokenObtainPairSerializer, GenreSerializer,
                          ReviewSerializer, TitleCreateSerializer,
                          TitleListSerializer, UserSignUpSerializer)

User = get_user_model()


def create_password(length=25):
    # user friendly password
    # symbols = string.ascii_letters + string.digits + string.punctuation
    # for ch in "Il1O0\"`'\\":
    #     symbols = symbols.replace(ch, "")
    symbols = (
        "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRST"
        "UVWXYZ23456789!#$%&()*+,-./:;<=>?@[]^_{|}~"
    )
    password_list = random.choices(symbols, k=length)
    return "".join(password_list)


class SignupAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        # get_or_create попытается создать объект в обход валидации
        instance = User.objects.filter(
            username=request.data.get("username"),
            email=request.data.get("email"),
        ).first()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        password = create_password()
        user.set_password(password)
        user.save()
        send_mail(
            "Your confirmation code",
            f"{password}",
            "from@example.com",
            (user.email,),
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminUserManagementSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    pagination_class = PageNumberPagination5
    lookup_field = "username"
    search_fields = ("username",)

    def get_instance(self):
        return self.request.user

    def get_ch_us_d_serializer(self):
        return ChangingUserDataSerializer

    @action(
        methods=("get", "patch"),
        permission_classes=(IsAuthenticated,),
        detail=False,
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        self.get_serializer_class = self.get_ch_us_d_serializer
        if request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)
        return self.retrieve(request, *args, **kwargs)


class CustomTokenObtainPairView(TokenViewBase):
    serializer_class = CustomTokenObtainPairSerializer


# Вторая часть
class CreateListDestroyViewSet(
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg("reviews__score")).order_by(
        "id"
    )
    pagination_class = PageNumberPagination5
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return TitleCreateSerializer
        return TitleListSerializer


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination5
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination5
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


# Третья часть
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination5
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, id=title_id)
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        serializer.save(
            title=get_object_or_404(Title, id=self.kwargs.get("title_id")),
            author=self.request.user,
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination5
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(Review, id=review_id)
        return Comment.objects.filter(review=review)

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=get_object_or_404(Review, id=self.kwargs.get("review_id")),
        )
