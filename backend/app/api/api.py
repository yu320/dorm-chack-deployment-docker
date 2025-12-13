from fastapi import APIRouter

from .endpoints import (
    auth, users, roles, rooms, items, inspections, 
    buildings, beds, students, lights_out, patrol_locations,
    permissions, admin, admin_inspections, import_data, reports, notifications, backup,

    dashboard, search, images, audit_logs,announcements, system_settings # Add audit_logs, system_settings

)


api_router = APIRouter()

api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(system_settings.router, prefix="/system-settings", tags=["system-settings"])
api_router.include_router(images.router, prefix="/images", tags=["images"]) # New images router
api_router.include_router(announcements.router, prefix="/announcements", tags=["announcements"]) # New announcements router
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["permissions"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(inspections.router, prefix="/inspections", tags=["inspections"])
api_router.include_router(lights_out.router, prefix="/lights-out", tags=["lights-out"])
api_router.include_router(patrol_locations.router, prefix="/patrol-locations", tags=["patrol-locations"])
api_router.include_router(buildings.router, prefix="/buildings", tags=["buildings"])
api_router.include_router(beds.router, prefix="/beds", tags=["beds"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(search.router, prefix="/search", tags=["search"]) # New search router
api_router.include_router(dashboard.router, prefix="/admin", tags=["admin-dashboard"])
api_router.include_router(admin_inspections.router, prefix="/admin/inspections", tags=["admin-inspections"])
api_router.include_router(import_data.router, prefix="/import", tags=["import"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(backup.router, prefix="/backup", tags=["backup"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit-logs"])
