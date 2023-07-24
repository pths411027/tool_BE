
from .project_management.route import pm_server_router
from .work_load.route import work_load_router
from .user.route import user_router

routers = [
    user_router,
    pm_server_router,
    work_load_router,
]
