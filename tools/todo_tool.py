from langchain_core.tools import tool
import requests

BASE_URL = "https://to-do-api-10.onrender.com"

@tool
def todo_tool(
    action: str,
    title: str = "",
    priority: str = "medium",
    task_id: int = None
) -> str:
    """
    Tool for managing Todo tasks.

    Actions:
    - create: Create a new task
    - list: List all tasks
    - complete: Mark a task as completed
    - delete: Delete a task
    """

    try:
        if action == "create":
            if not title:
                return "Task title is required."

            response = requests.post(
                f"{BASE_URL}/tasks",
                json={
                    "title": title,
                    "priority": priority
                },
                timeout=60
            )

        elif action == "list":
            response = requests.get(
                f"{BASE_URL}/tasks",
                timeout=60
            )

        elif action == "complete":
            if task_id is None:
                return "Task ID is required."

            response = requests.patch(
                f"{BASE_URL}/tasks/{task_id}",
                json={"completed": True},
                timeout=60
            )

        elif action == "delete":
            if task_id is None:
                return "Task ID is required."

            response = requests.delete(
                f"{BASE_URL}/tasks/{task_id}",
                timeout=60
            )

        else:
            return (
                "Invalid action. Use create, list, complete, or delete."
            )

        if response.ok:
            return response.text

        return f"API Error {response.status_code}: {response.text}"

    except requests.exceptions.Timeout:
        return "Todo API request timed out."

    except requests.exceptions.RequestException as e:
        return f"Todo API connection error: {str(e)}"

    except Exception as e:
        return f"Unexpected error: {str(e)}"