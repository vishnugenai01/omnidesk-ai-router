import requests
import os
from dotenv import load_dotenv
load_dotenv()

todo_url = os.getenv("todo_URL")
TIMEOUT = 60

def list_tasks() -> str:
    """Get all Todo tasks."""
    try:
        response = requests.get(
            f"{todo_url}/tasks",
            timeout=TIMEOUT
        )

        if not response.ok:
            return f"ERROR {response.status_code}: {response.text}"

        return response.text

    except requests.exceptions.RequestException as e:
        return f"Unable to retrieve tasks: {e}"


def create_task(title: str, priority: str = "medium") -> str:
    """Create a new Todo task."""

    if not title or not title.strip():
        return "Error: a task title is required."

    if priority not in ["low", "medium", "high"]:
        return "Error: priority must be low, medium, or high."

    try:
        response = requests.post(
            f"{todo_url}/tasks",
            json={
                "title": title,
                "priority": priority
            },
            timeout=TIMEOUT
        )

        if not response.ok:
            return f"ERROR {response.status_code}: {response.text}"

        return response.text

    except requests.exceptions.RequestException as e:
        return f"Unable to create task: {e}"


def complete_task(task_id: int) -> str:
    """Mark a Todo task as completed."""

    if task_id is None:
        return "Error: task_id is required."

    try:
        response = requests.patch(
            f"{todo_url}/tasks/{task_id}/complete",
            timeout=TIMEOUT
        )

        if not response.ok:
            return f"ERROR {response.status_code}: {response.text}"

        return response.text

    except requests.exceptions.RequestException as e:
        return f"Unable to complete task: {e}"


def delete_task(task_id: int) -> str:
    """Delete a Todo task."""

    if task_id is None:
        return "Error: task_id is required."

    try:
        response = requests.delete(
            f"{todo_url}/tasks/{task_id}",
            timeout=TIMEOUT
        )

        if not response.ok:
            return f"ERROR {response.status_code}: {response.text}"

        return response.text

    except requests.exceptions.RequestException as e:
        return f"Unable to delete task: {e}"