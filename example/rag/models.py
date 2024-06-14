from django.db import models

from langchain_core.documents import Document


class DjangoDocPage(models.Model):
    id: int  # noqa: A003
    path = models.CharField(max_length=255, unique=True)
    content = models.TextField()

    def __str__(self):
        return self.path

    def __repr__(self) -> str:
        return f"<DjangoDocPage {self.path}>"

    @property
    def django_docs_url(self):
        # Drop docs/ prefix:
        path = self.path[len("docs/") :]

        if path.endswith("index.txt"):
            # Remove index.txt suffix:
            path = path[: -len("index.txt")]
        else:
            # Remove .txt suffix:
            path = path[: -len(".txt")] + "/"

        return f"https://docs.djangoproject.com/en/stable/{path}"

    def as_langchain_document(self):
        return Document(page_content=self.content, metatags={"id": self.id, "path": self.path})
