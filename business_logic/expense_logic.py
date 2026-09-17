from urllib import response

from langchain_core.tools import tool
import requests


BASE_URL = "https://expense-tracker-7r84.onrender.com"


# ============================================================
# EXPENSE TOOL
# ============================================================

@tool
def add_expense(
    id: int,
    title: str,
    amount: float,
    category: str,
    date: str,
    user_id: int,
    user_name: str
) -> str:
    """
    Create a new expense.

    Args:
        id: Unique ID of the expense.
        title: Title or name of the expense.
        amount: Amount spent.
        category: Expense category.
        date: Date of the expense.
        user_id: ID of the user.
        user_name: Name of the user.
    """

    if id <= 0:
        return "Please provide a valid expense ID."

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
        "id": id,
        "title": title,
        "amount": amount,
        "category": category,
        "date": date,
        "user_id": user_id,
        "user_name": user_name
    }

    try:
        response = requests.post(
            f"{BASE_URL}/tracker/expenses",
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
        f"{BASE_URL}/tracker/expenses",
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
        f"{BASE_URL}/tracker/expenses/{expense_id}",
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
            f"{BASE_URL}/tracker/expenses/{expense_id}",
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
        f"{BASE_URL}/tracker/expenses/{expense_id}",
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
        f"{BASE_URL}/tracker/expenses/category/{category}",
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
        f"{BASE_URL}/tracker/expenses/date/{date}",
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
        f"{BASE_URL}/tracker/expenses/user/{user_id}",
        timeout=60
    )

    return response.text


@tool
def check_expense_service_health() -> str:
    """Check the health of the expense service."""

    response = requests.get(
        f"{BASE_URL}/tracker/health",
        timeout=60
    )

    return response.text


# ------------------------------------------------------------
# CREATE BUDGET
# ------------------------------------------------------------

@tool
def add_budget(
    budget_amount: float,
    total_spent: float,
    remaining_amt: float,
    month: str,
    user_id: int,
    user_name: str
) -> str:
    """Create a new monthly budget.

    Args:
        budget_amount: Total budget amount for the month
        total_spent: Total amount already spent
        remaining_amt: Remaining amount in the budget
        month: Month for the budget
        user_id: ID of the user
        user_name: Name of the user
    """

    if budget_amount <= 0:
        return "Please provide a valid budget amount."

    if not month:
        return "Please provide the budget month."

    if user_id <= 0:
        return "Please provide a valid user_id."

    if not user_name:
        return "Please provide the user_name."

    data = {
        "budget_amount": budget_amount,
        "total_spent": total_spent,
        "remaining_amt": remaining_amt,
        "month": month,
        "user_id": user_id,
        "user_name": user_name
    }

    try:
        res = requests.post(
            f"{BASE_URL}/budget",
            json=data,
            timeout=60
        )

        return res.text

    except requests.exceptions.RequestException as e:
        return (
            "Budget service is waking up or unreachable. "
            f"Please try again in a moment. ({e})"
        )


# ------------------------------------------------------------
# GET BUDGET STATUS
# ------------------------------------------------------------

@tool
def get_budget_status() -> str:
    """Get the current budget status.

    Returns the current budget information including
    budget amount, total spent, and remaining amount.
    """

    try:
        res = requests.get(
            f"{BASE_URL}/budget/status",
            timeout=60
        )

        return res.text

    except requests.exceptions.RequestException as e:
        return (
            "Budget service is waking up or unreachable. "
            f"Please try again in a moment. ({e})"
        )

# ------------------------------------------------------------
# GET BUDGET BY ID
# ------------------------------------------------------------

@tool
def get_budget(budget_id: int) -> str:
    """Get a specific budget using its budget ID.

    Args:
        budget_id: Unique ID of the budget to retrieve
    """

    if budget_id <= 0:
        return "Please provide a valid budget_id."

    try:
        res = requests.get(
            f"{BASE_URL}/budget/{budget_id}",
            timeout=60
        )

        return res.text

    except requests.exceptions.RequestException as e:
        return (
            "Budget service is waking up or unreachable. "
            f"Please try again in a moment. ({e})"
        )


# ------------------------------------------------------------
# GET BUDGET BY USER
# ------------------------------------------------------------

@tool
def get_budget_by_user(user_id: int) -> str:
    """Get the budget belonging to a specific user.

    Args:
        user_id: ID of the user whose budget should be retrieved
    """

    if user_id <= 0:
        return "Please provide a valid user_id."

    try:
        res = requests.get(
            f"{BASE_URL}/budget/user/{user_id}",
            timeout=60
        )

        return res.text

    except requests.exceptions.RequestException as e:
        return (
            "Budget service is waking up or unreachable. "
            f"Please try again in a moment. ({e})"
        )


# ------------------------------------------------------------
# BUDGET HEALTH
# ------------------------------------------------------------

@tool
def check_budget_service_health() -> str:
    """Check whether the budget service is running."""

    try:
        res = requests.get(
            f"{BASE_URL}/budget/health",
            timeout=60
        )

        return res.text

    except requests.exceptions.RequestException as e:
        return (
            "Budget service is waking up or unreachable. "
            f"Please try again in a moment. ({e})"
        )
