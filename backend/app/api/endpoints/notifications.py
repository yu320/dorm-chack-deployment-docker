from fastapi import APIRouter, Depends, HTTPException, status, Request # Import Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ... import schemas, auth, models # Import models for student queries
from ...services.notification_service import notification_service
from ... import crud # Import crud for student queries
from ...utils.audit import audit_log # Import audit_log

router = APIRouter()

@router.post("/send-email", status_code=status.HTTP_200_OK, dependencies=[Depends(auth.PermissionChecker("manage_users"))])
@audit_log(action="CREATE", resource_type="EmailNotification")
async def send_notification_email(
    email_data: schemas.EmailSchema,
    request: Request,
    db: AsyncSession = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    """
    Send email notifications to selected recipients.
    Requires 'manage_users' permission.
    """
    recipients = []
    
    # Logic to determine recipients based on selection
    if email_data.recipient_type == "all_students":
        paginated_students = await crud.get_students(db)
        students = paginated_students.get("records", [])
        recipients.extend([s.user.username for s in students if s.user and s.user.username])
    elif email_data.recipient_type == "students_in_building" and email_data.building_id:
        # Assuming you have a crud function to get students by building
        building_students = await crud.get_students_by_building(db, building_id=email_data.building_id)
        recipients.extend([s.user.username for s in building_students if s.user and s.user.username])
    elif email_data.recipient_type == "students_in_room" and email_data.room_id:
        # Assuming you have a crud function to get students by room
        room_students = await crud.get_students_by_room(db, room_id=email_data.room_id)
        recipients.extend([s.user.username for s in room_students if s.user and s.user.username])
    elif email_data.recipient_type == "students_in_household" and email_data.household:
        # Assuming you have a crud function to get students by household
        household_students = await crud.get_students_by_household(db, household=email_data.household)
        recipients.extend([s.user.username for s in household_students if s.user and s.user.username])
    elif email_data.recipient_type == "custom" and email_data.custom_recipients:
        recipients.extend(email_data.custom_recipients)
    
    if not recipients:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No recipients found or specified.")

    try:
        await notification_service.send_email_notification(
            subject=email_data.subject,
            recipients=recipients,
            body_html=email_data.body
        )
        return {"message": "Email sent successfully!"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to send email: {e}")

