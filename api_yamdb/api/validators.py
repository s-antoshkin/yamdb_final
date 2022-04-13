from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound, ValidationError

User = get_user_model()


class NoUserValidator:
    requires_context = True

    def __call__(self, attrs, serializer):
        username = serializer.initial_data["username"]

        if not User.objects.filter(username=username).exists():
            raise NotFound()


class NotMeValidator:
    requires_context = True

    def __call__(self, attrs, serializer):
        try:
            username = serializer.initial_data["username"]
        except Exception:
            username = None

        if username == "me":
            message = "Зарезервированное имя."
            raise ValidationError(message, code="incorrect_username")
