from typing import Sequence

from django.contrib.auth.models import User

from django_ai_assistant import AIAssistant, method_tool
from issue_tracker.models import Issue


class IssueTrackerAIAssistant(AIAssistant):
    id = "issue_tracker_assistant"  # noqa: A003
    name = "Issue Tracker Assistant"
    instructions = (
        "You are a issue tracker assistant. "
        "Help the user manage issues using the provided tools. "
        "Issue IDs are unique and auto-incremented, they are represented as #<id>. "
        "Make sure to include it in your responses, "
        "to know which issue you or the user are referring to. "
    )
    model = "gpt-4o"
    _user: User

    @method_tool
    def get_current_assignee_email(self) -> str:
        """Get the current user's email"""
        return self._user.email

    def _format_issues(self, issues: Sequence[Issue]) -> str:
        if not issues:
            return "No issues found"
        return "\n\n".join(
            [f"- {issue.title} #{issue.id}\n{issue.description}" for issue in issues]
        )

    @method_tool
    def list_issues(self) -> str:
        """List all issues"""
        return self._format_issues(list(Issue.objects.all()))

    @method_tool
    def list_user_assigned_issues(self, assignee_email: str) -> str:
        """List the issues assigned to the provided user"""
        return self._format_issues(list(Issue.objects.filter(assignee__email=assignee_email)))

    @method_tool
    def assign_user_to_issue(self, issue_id: int, assignee_email: str = "") -> str:
        """Assign a user to an issue. When assignee_email is empty, the issue assignment is removed."""
        try:
            issue = Issue.objects.get(id=issue_id)
            if assignee_email:
                assignee = User.objects.get(email=assignee_email)
            else:
                assignee = None
        except Issue.DoesNotExist:
            return f"ERROR: Issue {issue_id} does not exist"
        except User.DoesNotExist:
            return f"ERROR: User {assignee_email} does not exist"
        issue.assignee = assignee
        issue.save()
        return f"Assigned {assignee_email} to issue {issue.title} #{issue.id}"

    @method_tool
    def create_issue(self, title: str, description: str = "", assignee_email: str = "") -> str:
        """Create a new issue. Title is required. Description is optional. Assignee is optional."""
        if assignee_email:
            try:
                assignee = User.objects.get(email=assignee_email)
            except User.DoesNotExist:
                return f"ERROR: User {assignee_email} does not exist"
        else:
            assignee = None
        issue = Issue.objects.create(title=title, description=description, assignee=assignee)
        return f"Created issue {issue.title} #{issue.id}"

    @method_tool
    def update_issue(self, issue_id: int, title: str, description: str = "") -> str:
        """Update an issue"""
        try:
            issue = Issue.objects.get(id=issue_id)
        except Issue.DoesNotExist:
            return f"ERROR: Issue {issue_id} does not exist"
        issue.title = title
        issue.description = description
        issue.save()
        return f"Updated issue {issue.title} #{issue.id}"

    @method_tool
    def delete_issue(self, issue_id: int) -> str:
        """Delete an issue"""
        try:
            issue = Issue.objects.get(id=issue_id)
        except Issue.DoesNotExist:
            return f"ERROR: Issue {issue_id} does not exist"
        issue.delete()
        return f"Deleted issue {issue.title} #{issue.id}"
