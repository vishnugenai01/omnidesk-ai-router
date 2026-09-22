from typing import Optional

from langchain_core.tools import tool
import requests
import os
from dotenv import load_dotenv
load_dotenv()

expense_url = os.getenv("expense_URL")

# ============================================================
# EXPENSE TOOL
# ============================================================

@tool
def add_expense(
    title: str,
    amount: float,
    category: str,
    date: str,
    user_id: int,
    user_name: str,
    id: Optional[int] = None
) -> str:
    """
    Create a new expense.

    Args:
        title: Title or name of the expense.
        amount: Amount spent.
        category: Expense category.
        date: Date of the expense.
        user_id: ID of the user.
        user_name: Name of the user.
        id: Optional expense ID. Omit it to let the service assign one automatically.
    """

    if not title:
        return "Please provide the expense title."

    if amount <= 0:
        return "Please provide a valid expense amount."

    if not category:
        return "Please provide the expense category."

    if not date:
        return "Please provide the expense date."

    if user_id <= 0:
        return "Please provide a valid user_id."

    if not user_name:
        return "Please provide the user_name."

    data = {
        "title": title,
        "amount": amount,
        "category": category,
        "date": date,
        "user_id": user_id,
        "user_name": user_name
    }

    if id is not None:
        data["id"] = id

    try:
        response = requests.post(
            f"{expense_url}/tracker/expenses",
            json=data,
            timeout=30
        )

        if response.status_code == 422:
            return f"Validation error: {response.text}"

        response.raise_for_status()

        return response.text

    except requests.exceptions.RequestException as e:
        return f"Failed to add expense: {str(e)}"

          
@tool
def list_expenses() -> str:
    """Get all expenses."""

    response = requests.get(
        f"{expense_url}/tracker/expenses",
        timeout=30
    )

    return response.text

@tool
def get_expense(expense_id: int) -> str:
    """Get an expense by its ID.

    Args:
        expense_id: ID of the expense
    """

    response = requests.get(
        f"{expense_url}/tracker/expenses/{expense_id}",
        timeout=30
    )

    return response.text

@tool
def update_expense(
    expense_id: int,
    title: str = "",
    amount: float = 0.0,
    category: str = "",
    date: str = "",
    user_id: int = 0,
    user_name: str = ""
) -> str:
    """
    Update an existing expense.

    Args:
        expense_id: ID of the existing expense.
        title: Updated expense title.
        amount: Updated expense amount.
        category: Updated expense category.
        date: Updated expense date in YYYY-MM-DD format.
        user_id: User ID.
        user_name: User name.
    """

    if expense_id <= 0:
        return "Please provide a valid expense ID."

    data = {}

    if title:
        data["title"] = title

    if amount > 0:
        data["amount"] = amount

    if category:
        data["category"] = category

    if date:
        data["date"] = date

    if user_id > 0:
        data["user_id"] = user_id

    if user_name:
        data["user_name"] = user_name

    if not data:
        return "Please provide at least one field to update."

    try:
        response = requests.put(
            f"{expense_url}/tracker/expenses/{expense_id}",
            json=data,
            timeout=30
        )

        response.raise_for_status()

        return response.text

    except requests.exceptions.RequestException as e:
        return f"Failed to update expense: {str(e)}"

@tool
def delete_expense(expense_id: int) -> str:
    """Delete an expense by its ID.

    Args:
        expense_id: ID of the expense to delete
    """

    response = requests.delete(
        f"{expense_url}/tracker/expenses/{expense_id}",
        timeout=60
    )

    return response.text

@tool
def get_expenses_by_category(category: str) -> str:
    """Get expenses by category.

    Args:
        category: Category to search for
        Treat all text comparisons as case-insensitive
    """

    response = requests.get(
        f"{expense_url}/tracker/expenses/category/{category}",
        timeout=60
    )

    return response.text

@tool
def get_expenses_by_date(date: str) -> str:
    """Get expenses for a specific date.

    Args:
        date: Date to search for
    """

    response = requests.get(
        f"{expense_url}/tracker/expenses/date/{date}",
        timeout=60
    )

    return response.text

@tool
def get_expenses_by_user(user_id: int) -> str:
    """Get expenses for a specific user.

    Args:
        user_id: ID of the user
    """

    response = requests.get(
        f"{expense_url}/tracker/expenses/user/{user_id}",
        timeout=60
    )

    return response.text


@tool
def check_expense_service_health() -> str:
    """Check the health of the expense service."""

    response = requests.get(
        f"{expense_url}/tracker/health",
        timeout=60
    )

    return response.text


# ------------------------------------------------------------
# BUDGET TOOL
# ------------------------------------------------------------

@tool
def add_budget(
    budget_amount: float,
    total_spent: float = 0.0,
    remaining_amt: float = 0.0,
    month: str = "",
    user_id: int = 1,
    user_name: str = "",
    budget_id: Optional[int] = None
) -> str:
    """Create a new monthly budget.

    budget_id is optional — omit it to let the service assign one automatically.
    """

    print(
        f"Request body is budget: {budget_amount}, "
        f"month: {month}, "
        f"user_id: {user_id}, "
        f"user_name: {user_name}, "
        f"total_spent: {total_spent}, "
        f"remaining_amt: {remaining_amt}"
    )

    if budget_amount <= 0:
        return "Please provide a valid budget amount."

    if not month:
        return "Please provide the budget month."

    if user_id <= 0:
        return "Please provide a valid user_id."

    if not user_name:
        return "Please provide the user_name."

    # Calculate remaining amount automatically
    if remaining_amt <= 0:
        remaining_amt = budget_amount - total_spent

    data = {
        "budget_amount": budget_amount,
        "total_spent": total_spent,
        "remaining_amt": remaining_amt,
        "month": month,
        "user_id": user_id,
        "user_name": user_name
    }

    if budget_id is not None:
        data["budget_id"] = budget_id

    print(f"Passing data is {data}")

    try:
        res = requests.post(
            f"{expense_url}/budget/budget",
            json=data
        )

        print(f"API response is {res.text}")
        print(f"API response code is {res.status_code}")

        if res.status_code >= 400:
            return f"Unable to create budget: {res.text}"

        return res.text

    except requests.exceptions.RequestException as e:
        return (
            "Budget service is waking up or unreachable. "
            f"Please try again in a moment. ({e})"
        )

@tool
def get_budget_status() -> str:
    """Get all existing monthly budgets.

    Use this tool whenever the user asks to:
    - show all budgets
    - get all budgets
    - list all budgets
    - show my budgets
    - display all budgets
    - see all monthly budgets
    - get the complete budget list

    This tool returns all budget records, including:
    budget ID, budget amount, total spent, remaining amount,
    month, and status.

    Do NOT use this tool when the user asks for one specific
    budget by ID. For a specific budget ID, use get_budget.
    """

    try:
        res = requests.get(
            f"{expense_url}/budget/status",
            timeout=60
        )

        return res.text

    except requests.exceptions.RequestException as e:
        return (
            "Budget service is waking up or unreachable. "
            f"Please try again in a moment. ({e})"
        )

@tool
def get_budget(budget_id: int) -> str:
    """Get a specific budget using its budget ID.

    Use this tool when the user asks for one specific budget
    by ID, such as "get budget with id 5".
    """

    if budget_id <= 0:
        return "Please provide a valid budget_id."

    try:
        res = requests.get(
            f"{expense_url}/budget/budget/{budget_id}",
            timeout=60
        )

        print(f"GET BUDGET URL: {expense_url}/budget/budget/{budget_id}")
        print(f"GET BUDGET STATUS: {res.status_code}")
        print(f"GET BUDGET RESPONSE: {res.text}")

        if res.status_code == 404:
            return f"No budget found with ID {budget_id}."

        if res.status_code >= 400:
            return f"Unable to get budget: {res.text}"

        return res.text

    except requests.exceptions.RequestException as e:
        return (
            "Budget service is waking up or unreachable. "
            f"Please try again in a moment. ({e})"
        )

@tool
def get_budget_by_user(user_id: int) -> str:
    """Get all budgets belonging to a specific user.

    Use this tool when the user asks for budgets by user ID,
    for example:
    - get budget with user id 2
    - show budgets for user 2
    - get all budgets of user 2
    """

    if user_id <= 0:
        return "Please provide a valid user_id."

    try:
        url = f"{expense_url}/budget/budget/user/{user_id}"

        res = requests.get(
            url,
            timeout=60
        )

        print(f"GET BUDGET BY USER URL: {url}")
        print(f"STATUS CODE: {res.status_code}")
        print(f"RESPONSE: {res.text}")

        if res.status_code == 404:
            return f"No budget found for user ID {user_id}."

        if res.status_code >= 400:
            return f"Unable to get budget for user {user_id}: {res.text}"

        return res.text

    except requests.exceptions.RequestException as e:
        return (
            "Budget service is waking up or unreachable. "
            f"Please try again in a moment. ({e})"
        )

@tool
def check_budget_service_health() -> str:
    """Check whether the budget service is running."""

    try:
        res = requests.get(
            f"{expense_url}/budget/health",
            timeout=60
        )

        return res.text

    except requests.exceptions.RequestException as e:
        return (
            "Budget service is waking up or unreachable. "
            f"Please try again in a moment. ({e})"
        )
