from .data_suite.route import data_suite_router
from .project_management.route import pm_server_router
from .user.route import user_router
from .work_load.route import work_load_router
from .expense_management.route import expense_router

routers = [
    user_router,
    pm_server_router,
    work_load_router,
    data_suite_router,
    expense_router,
]
