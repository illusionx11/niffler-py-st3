import pytest

class TestData:   
    # Login tests
    login_data = lambda x: pytest.mark.parametrize("login_data", x, ids=lambda param: param.username)
    # Registration tests
    register_data = lambda x: pytest.mark.parametrize("register_data", x, ids=lambda param: f"{param.username} {param.password} {param.password_repeat}")
    username = lambda x: pytest.mark.parametrize("username", x)
    password = lambda x: pytest.mark.parametrize("password", x)
    # Spendings tests
    spending_data = lambda x: pytest.mark.parametrize("spending_data", x, ids=lambda param: f"{param.amount} {param.currency} {param.category} {param.description}")
    query = lambda x: pytest.mark.parametrize("query", x)
    # Profile tests
    new_category = lambda x: pytest.mark.parametrize("new_category", x, indirect=True)
    category = lambda x: pytest.mark.parametrize("category", x, indirect=True)
    archived_category = lambda x: pytest.mark.parametrize("archived_category", x, indirect=True)
    profile_name = lambda x: pytest.mark.parametrize("profile_name", x)
    # Userdata tests
    new_user = lambda x: pytest.mark.parametrize("new_user", x, indirect=True, ids=lambda param: f"{param.username}")
    page_info = lambda x: pytest.mark.parametrize("page_info", x, ids=lambda param: f"page {param.page}, size {param.size}")