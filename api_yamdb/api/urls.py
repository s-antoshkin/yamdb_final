from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "api"

router_v1 = routers.DefaultRouter()

router_v1.register(r"users", views.UsersViewSet)
# Вторая часть
router_v1.register("titles", views.TitlesViewSet, basename="title")
router_v1.register("genres", views.GenreViewSet, basename="genre")
router_v1.register("categories", views.CategoryViewSet, basename="category")
# Третья часть
router_v1.register(
    r"titles/(?P<title_id>\d+)/reviews",
    views.ReviewViewSet,
    basename="reviews",
)
router_v1.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    views.CommentViewSet,
    basename="comments",
)

urlpatterns = [
    path("v1/", include(router_v1.urls)),
    # Первая часть
    path("v1/auth/signup/", views.SignupAPIView.as_view(), name="signup"),
    path(
        "v1/auth/token/",
        views.CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
]
