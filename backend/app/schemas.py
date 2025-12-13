import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from typing import List, Optional, Any
from datetime import datetime

from .models import InspectionStatus, ItemStatus, LightStatus, TagType

# --- Permission Schemas ---
class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(PermissionBase):
    name: Optional[str] = None
    description: Optional[str] = None

class Permission(PermissionBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class PaginatedPermissions(BaseModel):
    total: int
    records: List[Permission]

# --- Role Schemas ---
class RoleBase(BaseModel):
    name: str
class RoleCreate(RoleBase):
    permissions: List[uuid.UUID] = []
class RoleUpdate(BaseModel):
    name: Optional[str] = None
    permissions: Optional[List[uuid.UUID]] = None
class Role(RoleBase):
    id: uuid.UUID
    permissions: List[Permission] = []
    model_config = ConfigDict(from_attributes=True)

class PaginatedRoles(BaseModel):
    total: int
    records: List[Role]

# --- Building Schemas (ID is INT) ---
class BuildingBase(BaseModel):
    name: str
class BuildingCreate(BuildingBase):
    pass
class Building(BuildingBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Room Schemas (ID is INT) ---
class RoomBase(BaseModel):
    building_id: int
    room_number: str
    household: Optional[str] = None
    room_type: Optional[str] = None
class RoomCreate(RoomBase):
    pass
class RoomUpdate(BaseModel):
    building_id: Optional[int] = None
    room_number: Optional[str] = None
    household: Optional[str] = None
    room_type: Optional[str] = None
class Room(RoomBase):
    id: int
    building: Building
    model_config = ConfigDict(from_attributes=True)

class PaginatedRooms(BaseModel):
    total: int
    records: List[Room]

# --- Bed Schemas (ID is INT) ---
class BedBase(BaseModel):
    room_id: int
    bed_number: str
    bed_type: Optional[str] = None
    status: Optional[str] = "available"
class BedCreate(BedBase):
    pass
class BedUpdate(BaseModel):
    room_id: Optional[int] = None
    bed_number: Optional[str] = None
    bed_type: Optional[str] = None
    status: Optional[str] = None
class Bed(BedBase):
    id: int
    room: Room
    model_config = ConfigDict(from_attributes=True)

class PaginatedBeds(BaseModel):
    total: int
    records: List[Bed]

# --- Nested Schemas for Tree View ---
class BedNested(BaseModel):
    id: int
    bed_number: str
    status: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class RoomWithBeds(BaseModel):
    id: int
    room_number: str
    room_type: Optional[str]
    beds: List[BedNested] = []
    model_config = ConfigDict(from_attributes=True)

class BuildingWithRooms(BaseModel):
    id: int
    name: str
    rooms: List[RoomWithBeds] = []
    model_config = ConfigDict(from_attributes=True)


# --- Student Schemas ---
class StudentBase(BaseModel):
    student_id_number: str
    full_name: str
    class_name: Optional[str] = None
    gender: Optional[str] = None
    identity_status: Optional[str] = None
    is_foreign_student: Optional[bool] = False
    enrollment_status: Optional[str] = None
    remarks: Optional[str] = None
    license_plate: Optional[str] = None
    contract_info: Optional[str] = None
    temp_card_number: Optional[str] = None
class StudentCreate(StudentBase):
    bed_id: Optional[int] = None # Stays int
class StudentUpdate(BaseModel):
    student_id_number: Optional[str] = None
    full_name: Optional[str] = None
    class_name: Optional[str] = None
    gender: Optional[str] = None
    identity_status: Optional[str] = None
    is_foreign_student: Optional[bool] = None
    enrollment_status: Optional[str] = None
    remarks: Optional[str] = None
    license_plate: Optional[str] = None
    contract_info: Optional[str] = None
    temp_card_number: Optional[str] = None
    bed_id: Optional[int] = None

class StudentAssignBed(BaseModel):
    bed_id: Optional[int] = None # Stays int, None for unassigning

class Student(StudentBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    bed: Optional[Bed] = None
    model_config = ConfigDict(from_attributes=True)

class PaginatedStudents(BaseModel):
    total: int
    records: List[Student]

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
class UserCreate(UserBase):
    password: str
    student_id_number: str
    bed_number: Optional[str] = None
    email: EmailStr

    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('password_too_short')
        return v

class UserUpdate(UserBase):
    username: Optional[str] = None
    is_active: Optional[bool] = None
    roles: Optional[List[uuid.UUID]] = None # For updating user roles

class UserChangePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

class UserInDB(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: List[Role] = []
    student: Optional[Student] = None
    model_config = ConfigDict(from_attributes=True)
class User(UserInDB):
    permissions: List[str] = []

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    roles: List[Role] = []
    student: Optional[Student] = None
    model_config = ConfigDict(from_attributes=True)

class PaginatedUsers(BaseModel):
    total: int
    records: List[User]

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    username: Optional[str] = None

# --- Item Schemas ---
class InspectionItemBase(BaseModel):
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
class InspectionItemCreate(InspectionItemBase):
    pass
class InspectionItemUpdate(BaseModel):
    name: Optional[str] = None
    name_en: Optional[str] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
    is_active: Optional[bool] = None
class InspectionItemInDBBase(InspectionItemBase):
    id: uuid.UUID
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
class InspectionItem(InspectionItemInDBBase):
    pass

class PaginatedInspectionItems(BaseModel):
    total: int
    records: List[InspectionItem]

class InspectionItemBatchUpdate(BaseModel):
    item_ids: List[uuid.UUID]
    is_active: bool

# --- Photo Schemas ---
class PhotoBase(BaseModel):
    # file_path: str # Removed, as it will be generated on backend
    pass

class PhotoCreate(PhotoBase):
    file_content: str # Base64 encoded image content
    file_name: str # Original file name with extension
    file_path: Optional[str] = None # To be populated by the service

class Photo(PhotoBase):
    id: uuid.UUID
    file_path: str # Path to the stored image (generated on backend)
    uploaded_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Inspection Detail Schemas ---
class InspectionDetailBase(BaseModel):
    item_id: uuid.UUID
    status: ItemStatus = ItemStatus.ok
    comment: Optional[str] = None
class InspectionDetailCreate(InspectionDetailBase):
    photos: List[PhotoCreate] = []
class InspectionDetailUpdate(InspectionDetailBase):
    pass
class InspectionDetail(InspectionDetailBase):
    id: uuid.UUID
    item: InspectionItem
    photos: List[Photo] = []
    model_config = ConfigDict(from_attributes=True)

# --- Inspection Record Schemas ---
class InspectionRecordBase(BaseModel):
    student_id: uuid.UUID # FK to Student
    room_id: int # FK to Room (Stays int)
class InspectionRecordCreate(BaseModel):
    details: List[InspectionDetailCreate]
    signature: Optional[str] = None
class InspectionRecordUpdate(BaseModel):
    status: Optional[InspectionStatus] = None
class InspectionRecord(InspectionRecordBase):
    id: uuid.UUID
    status: InspectionStatus
    created_at: datetime
    submitted_at: Optional[datetime] = None
    student: Student
    room: Room
    details: List[InspectionDetail] = []
    signature: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class PaginatedInspectionRecords(BaseModel):
    total: int
    records: List[InspectionRecord]

class InspectionCreate(BaseModel):
    room_id: Optional[int] = None
    student_id: Optional[uuid.UUID] = None
    details: List[InspectionDetailCreate]
    signature_base64: Optional[str] = None

class BatchInspectionCreate(BaseModel):
    inspections: List[InspectionCreate]


class EmailSchema(BaseModel):
    recipient_type: str # e.g., "all_students", "students_in_building", "students_in_room", "students_in_household", "custom"
    subject: str
    body: str
    custom_recipients: Optional[List[str]] = None
    building_id: Optional[int] = None
    room_id: Optional[int] = None
    household: Optional[str] = None

class InspectionReportEmailRequest(BaseModel):
    recipient_email: str

class DataExportRequest(BaseModel):
    table_names: List[str]


# --- Lights Out Check Schemas ---
class PatrolLocationBase(BaseModel):
    name: str
    building_id: int # Stays int
    household: Optional[str] = None
    check_items: Optional[List[Any]] = None # List of items to check

class PatrolLocationCreate(PatrolLocationBase):
    pass

class PatrolLocationUpdate(PatrolLocationBase):
    name: Optional[str] = None
    building_id: Optional[int] = None

class PatrolLocation(PatrolLocationBase):
    id: uuid.UUID
    building: Building
    model_config = ConfigDict(from_attributes=True)

class PaginatedPatrolLocations(BaseModel):
    total: int
    records: List[PatrolLocation]


class LightsOutCheckBase(BaseModel):
    patrol_location_id: Optional[uuid.UUID] = None
    room_id: Optional[int] = None
    status: LightStatus
    notes: Optional[str] = None

class LightsOutCheckCreate(LightsOutCheckBase):
    pass

class LightsOutCheck(LightsOutCheckBase):
    id: uuid.UUID
    location: Optional[PatrolLocation] = None
    room: Optional[Room] = None
    model_config = ConfigDict(from_attributes=True)


class LightsOutPatrolBase(BaseModel):
    building_id: int # Stays int

class LightsOutPatrolCreate(LightsOutPatrolBase):
    checks: List[LightsOutCheckCreate]

class LightsOutPatrol(LightsOutPatrolBase):
    id: uuid.UUID
    patroller_id: uuid.UUID
    patrol_time: datetime
    patroller: User
    building: Building
    checks: List[LightsOutCheck] = []
    model_config = ConfigDict(from_attributes=True)

class PaginatedLightsOutPatrols(BaseModel):
    total: int
    records: List[LightsOutPatrol]

# --- Dashboard Schemas ---
class DamageRankingItem(BaseModel):
    name: str
    count: int
    model_config = ConfigDict(from_attributes=True)

class DashboardChartData(BaseModel):
    pass_rate: dict[str, int]
    damage_ranking: List[DamageRankingItem]
    model_config = ConfigDict(from_attributes=True)

# --- Error Handling Schemas ---
class Message(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str
    status_code: int = 400

# --- Global Search Schemas ---
class GlobalSearchRequest(BaseModel):
    query: str

class SearchResultItem(BaseModel):
    type: str  # e.g., "student", "room"
    id: str    # UUID for student, int for room
    title: str # Display name
    description: Optional[str] = None # Additional info

class GlobalSearchResults(BaseModel):
    results: List[SearchResultItem]

class RequestPasswordReset(BaseModel):
    email: str

class ResetPassword(BaseModel):
    token: str
    new_password: str
    confirm_password: str


# --- Announcement Schemas ---
class AnnouncementBase(BaseModel):
    title: str
    title_en: Optional[str] = None
    content: str
    content_en: Optional[str] = None
    tag: str
    tag_type: str = "primary"


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    title_en: Optional[str] = None
    content: Optional[str] = None
    content_en: Optional[str] = None
    tag: Optional[str] = None
    tag_type: Optional[str] = None
    is_active: Optional[bool] = None


class AnnouncementResponse(AnnouncementBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PaginatedAnnouncements(BaseModel):
    total: int
    records: List[AnnouncementResponse]

# --- Audit Log Schemas ---
class AuditLogBase(BaseModel):
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    created_at: datetime
    user: Optional[User] = None

    model_config = ConfigDict(from_attributes=True)

class PaginatedAuditLogs(BaseModel):
    total: int
    records: List[AuditLog]


# --- System Settings Schemas ---
class SystemSettingBase(BaseModel):
    key: str
    value: Optional[str] = None
    description: Optional[str] = None

class SystemSettingCreate(SystemSettingBase):
    pass

class SystemSettingUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None

class SystemSetting(SystemSettingBase):
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Rebuild models with forward references if any were used, e.g. in User
# This is a good practice when schemas reference each other.
User.model_rebuild()
LightsOutPatrol.model_rebuild()
AuditLog.model_rebuild()
