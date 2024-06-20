from django.apps import AppConfig


class MoviesConfig(AppConfig):
    default_auto_field = "example.fields.UUIDAutoField"
    name = "movies"
