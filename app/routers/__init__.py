
from .project_management.route import pm_server_router
from .work_load.route import work_load_router

routers = [
    pm_server_router,
    work_load_router,
]
