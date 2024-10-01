import json

from django.contrib.auth.models import User

from django_ai_assistant import AIAssistant, method_tool
from issue_tracker.models import Issue


class IssueTrackerAIAssistant(AIAssistant):
    id = "issue_tracker_assistant"  # noqa: A003
    name = "Issue Tracker Assistant"
    instructions = (
        "You are a issue tracker assistant. "
        "Interact with the issue DB by using the provided tools. "
        "Always refer to issue IDs as #<id>. "
        "Make sure to include issue IDs in your responses, "
        "to know which issue you or the user are referring to. "
    )
    model = "gpt-4o-mini"
    _user: User

    @method_tool
    def get_current_assignee_email(self) -> str:
        """Get the current user's email"""
        return self._user.email

    @method_tool
    def list_issues(self) -> str:
        """List all issues"""
        return json.dumps(
            {
                "issues": list(
                    Issue.objects.values("id", "title", "description", "assignee__email")
                ),
            }
        )

    @method_tool
    def list_assigned_issues(self, assignee_email: str) -> str:
        """List the issues assigned to the user with the email from `assignee_email` param."""
        return json.dumps(
            {
                "issues": list(
                    Issue.objects.filter(
                        assignee__email=assignee_email,
                    ).values("id", "title", "description", "assignee__email")
                ),
            }
        )

    @method_tool
    def assign_user_to_issue(self, issue_id: int, assignee_email: str) -> str:
        """Assign a user to an issue. Set the `assignee_email` param to an user's email.
        Or pass an empty string to remove the issue assignment."""
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
        return f"Assigned {assignee_email} to issue #{issue.id} - {issue.title}"

    @method_tool
    def create_issue(self, title: str, description: str = "", assignee_email: str = "") -> str:
        """Create a new issue.
        Assign it to a user by passing the `assignee_email` param."""
        if assignee_email:
            try:
                assignee = User.objects.get(email=assignee_email)
            except User.DoesNotExist:
                return f"ERROR: User {assignee_email} does not exist"
        else:
            assignee = None
        issue = Issue.objects.create(title=title, description=description, assignee=assignee)
        return f"Created issue #{issue.id} - {issue.title}"

    @method_tool
    def update_issue(self, issue_id: int, title: str, description: str = "") -> str:
        """Update an issue."""
        try:
            issue = Issue.objects.get(id=issue_id)
        except Issue.DoesNotExist:
            return f"ERROR: Issue {issue_id} does not exist"
        issue.title = title
        issue.description = description
        issue.save()
        return f"Updated issue #{issue_id} - {issue.title}"

    @method_tool
    def delete_issue(self, issue_id: int) -> str:
        """Delete an issue"""
        try:
            issue = Issue.objects.get(id=issue_id)
        except Issue.DoesNotExist:
            return f"ERROR: Issue {issue_id} does not exist"
        issue.delete()
        return f"Deleted issue #{issue_id} - {issue.title}"
