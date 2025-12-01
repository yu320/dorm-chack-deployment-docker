from .crud_user import crud_user
from .crud_student import crud_student
from .crud_room import crud_room
from .crud_building import crud_building
from .crud_bed import crud_bed
from .crud_inspection import crud_inspection
from .crud_announcement import crud_announcement
from .crud_patrol_location import crud_patrol_location
from .crud_lights_out import crud_lights_out
from .crud_audit import audit_log_crud as crud_audit
from .crud_backup import backup_crud as crud_backup
from .crud_permission import permission_crud as crud_permission
from .crud_role import role_crud as crud_role
from .crud_item import item_crud as crud_item

# Export instances for easy access
__all__ = [
    "crud_user",
    "crud_student",
    "crud_room",
    "crud_building",
    "crud_bed",
    "crud_inspection",
    "crud_announcement",
    "crud_patrol_location",
    "crud_lights_out",
    "crud_audit",
    "crud_backup",
    "crud_permission",
    "crud_role",
    "crud_item"
]