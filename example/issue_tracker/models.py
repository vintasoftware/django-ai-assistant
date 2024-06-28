from django.conf import settings
from django.db import models


class Issue(models.Model):
    id: int  # noqa: A003
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_issues",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Issue"
        verbose_name_plural = "Issues"
        ordering = ("assignee", "created_at")

    def __str__(self):
        return f"{self.title} - {self.assignee}"

    def __repr__(self) -> str:
        return f"<Issue {self.title} #{self.id} of {self.assignee}>"
