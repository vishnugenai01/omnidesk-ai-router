from typing import Literal

from langchain_core.tools import tool

from business_logic.todo_logic import (
    list_tasks as _list_tasks,
    create_task as _create_task,
    complete_task as _complete_task,
    delete_task as _delete_task,
)


@tool
def list_tasks() -> str:
    """
    Get all todo tasks.

    Use this when the user wants to see their tasks,
    todo list, pending tasks, or remaining tasks.
    """
    return _list_tasks()


@tool
def create_task(
    title: str,
    priority: Literal["low", "medium", "high"] = "medium",
) -> str:
    """
    Create a new todo task.

    Use this when the user wants to add or create a task.

    Args:
        title: The task description.
        priority: Task priority: low, medium, or high.
    """
    return _create_task(title, priority)


@tool
def complete_task(task_id: int) -> str:
    """
    Mark an existing todo task as completed.

    Use this when the user wants to finish or complete a task.

    Args:
        task_id: Numeric ID of the task.
    """
    return _complete_task(task_id)


@tool
def delete_task(task_id: int) -> str:
    """
    Permanently delete a todo task.

    Use this only when the user explicitly wants
    the task removed.

    Args:
        task_id: Numeric ID of the task.
    """
    return _delete_task(task_id)