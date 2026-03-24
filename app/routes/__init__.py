from fastapi import APIRouter

router = APIRouter()

from app.routes.root_route import router as root_router
from app.routes.common_route import router as common_router

from app.routes.meet_route import router as meet_router
from app.routes.meet_labor_route import router as meet_labor_router
from app.routes.meet_population_route import router as meet_population_router

from app.routes.open_door_route import router as open_door_router
from app.routes.radio_route import router as radio_router
from app.routes.round_table_route import router as round_table_router
from app.routes.smi_route import router as smi_router

router.include_router(root_router)
router.include_router(common_router)

router.include_router(meet_router)
router.include_router(meet_labor_router)
router.include_router(meet_population_router)

router.include_router(open_door_router)
router.include_router(radio_router)
router.include_router(smi_router)
router.include_router(round_table_router)

print(f'Зашли в __init__.py')