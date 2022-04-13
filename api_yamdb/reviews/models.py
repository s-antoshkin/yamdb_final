from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USERS_ROLE = (
        ("user", "user"),
        ("moderator", "moderator"),
        ("admin", "admin"),
    )

    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(max_length=254, unique=True)
    bio = models.CharField(max_length=400, blank=True, null=True)
    role = models.CharField(max_length=9, choices=USERS_ROLE, default="user")

    @property
    def is_admin(self):
        if self.role == "admin" or self.is_superuser:
            return True
        return False

    @property
    def is_moderator(self):
        if self.role == "moderator":
            return True
        return False

    class Meta:
        ordering = ["date_joined"]


# Вторая часть
class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название категории")
    slug = models.SlugField(unique=True, verbose_name="Краткое название")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название жанра")
    slug = models.SlugField(unique=True, verbose_name="Краткое название")

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=200, verbose_name="Название произведения"
    )
    year = models.IntegerField(
        null=True, verbose_name="Год издания", db_index=True
    )
    genre = models.ManyToManyField(Genre, blank=True, related_name="titles")
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        related_name="titles",
        on_delete=models.SET_NULL,
    )
    description = models.CharField(max_length=200, null=True)

    class Meta:
        verbose_name = "Произведене"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name


# Третья часть
class Review(models.Model):
    text = models.TextField()
    score = models.IntegerField(null=True, blank=True)
    title = models.ForeignKey(
        Title,
        related_name="reviews",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name="reviews",
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        constraints = [
            models.UniqueConstraint(
                fields=["author", "title"], name="unique_author_title"
            )
        ]
        ordering = ["pub_date"]

    def __str__(self):
        return f"{self.title} {self.author} {self.score}"


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата комментария"
    )
    text = models.TextField(
        max_length=400,
        verbose_name="Комментарий",
    )

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.text[:15]
