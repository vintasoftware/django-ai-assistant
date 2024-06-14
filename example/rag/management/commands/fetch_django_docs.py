import tempfile
from typing import Any, cast

from django.conf import settings
from django.core.management.base import BaseCommand

from git import Repo

from rag.models import DjangoDocPage


class Command(BaseCommand):
    help = "Fill the database with Django docs"  # noqa: A003
    django_repo_url = "https://github.com/django/django.git"

    def handle(self, *args, **options):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.stdout.write(self.style.NOTICE("Cloning Django repo to a temporary directory..."))
            repo = Repo.clone_from(self.django_repo_url, temp_dir)
            repo.git.checkout(settings.DJANGO_DOCS_BRANCH)
            self.stdout.write(self.style.NOTICE("Saving docs..."))
            head = repo.heads[settings.DJANGO_DOCS_BRANCH].checkout()
            tree = head.commit.tree
            tree = cast(Any, tree)
            for blob in tree["docs"].traverse(visit_once=True):
                if blob.path.startswith("docs/_ext/"):
                    continue
                if blob.path.startswith("docs/_theme/"):
                    continue
                if blob.path.startswith("docs/man/"):
                    continue
                if blob.path.startswith("docs/README.rst"):
                    continue
                if blob.path.startswith("docs/requirements.txt"):
                    continue

                if blob.path.endswith(".txt"):
                    DjangoDocPage.objects.update_or_create(
                        path=blob.path,
                        defaults={"content": blob.data_stream.read().decode("utf-8")},
                    )

        self.stdout.write(self.style.SUCCESS("Success in saving Django docs to DB"))
