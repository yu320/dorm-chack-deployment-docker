import enum
import uuid
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    Text,
    Table,
    UniqueConstraint,
    CHAR, # Use CHAR for UUIDs
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


# --- Association Tables ---
role_permissions = Table('role_permissions', Base.metadata,
    Column('role_id', CHAR(36), ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', CHAR(36), ForeignKey('permissions.id'), primary_key=True)
)

user_roles = Table('user_roles', Base.metadata,
    Column('user_id', CHAR(36), ForeignKey('users.id'), primary_key=True),
    Column('role_id', CHAR(36), ForeignKey('roles.id'), primary_key=True)
)


# --- Permission Model ---
class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False) # e.g., "manage_rooms", "submit_inspection"
    description = Column(String(255))


# --- Role Model ---
class Role(Base):
    __tablename__ = 'roles'
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), unique=True, nullable=False)
    permissions = relationship("Permission", secondary=role_permissions, backref="roles")


# --- User Model ---
class User(Base):
    __tablename__ = "users"
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    roles = relationship("Role", secondary=user_roles, back_populates="users", lazy="selectin")
    student = relationship("Student", back_populates="user", uselist=False, lazy="selectin") # One-to-one with Student

Role.users = relationship("User", secondary=user_roles, back_populates="roles")


# --- Building Model (ID is INT) ---
class Building(Base):
    __tablename__ = "buildings"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False) # e.g., A1

    rooms = relationship("Room", back_populates="building")


# --- Room Model (ID is INT) ---
class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    room_number = Column(String(50), index=True, nullable=False) # e.g., A1201
    household = Column(String(50), index=True) # e.g., A1201
    room_type = Column(String(50)) # e.g., 冷氣套房

    __table_args__ = (UniqueConstraint('building_id', 'room_number', name='_building_room_uc'),)

    building = relationship("Building", back_populates="rooms")
    beds = relationship("Bed", back_populates="room")
    inspections = relationship("InspectionRecord", back_populates="room")


# --- Bed Model (ID is INT) ---
class Bed(Base):
    __tablename__ = "beds"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    bed_number = Column(String(20), nullable=False) # e.g., A1201-1, or just '1' if room_number is unique
    bed_type = Column(String(50)) # e.g., 上鋪
    status = Column(String(20), default="available") # e.g., available, occupied, reserved

    room = relationship("Room", back_populates="beds")
    student = relationship("Student", back_populates="bed", uselist=False) # One-to-one with Student


# --- Student Model ---
class Student(Base):
    __tablename__ = "students"
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id"), unique=True, nullable=True) # Link to User, nullable for pre-populated
    bed_id = Column(Integer, ForeignKey("beds.id"), unique=True, nullable=True) # Stays Integer
    student_id_number = Column(String(20), unique=True, index=True, nullable=False) # 學號
    full_name = Column(String(100), nullable=False) # 姓名
    class_name = Column(String(50)) # 班級
    gender = Column(String(10)) # 性別
    identity_status = Column(String(50)) # 身分別
    is_foreign_student = Column(Boolean, default=False) # 外籍生
    enrollment_status = Column(String(50)) # 在學狀態
    remarks = Column(Text) # 備註
    license_plate = Column(String(20)) # 車牌號碼
    contract_info = Column(Text) # 合約書
    temp_card_number = Column(String(50)) # 臨時卡號

    user = relationship("User", back_populates="student", uselist=False) # One-to-one with User
    bed = relationship("Bed", back_populates="student", uselist=False) # One-to-one with Bed
    inspections = relationship("InspectionRecord", back_populates="student")


class InspectionItem(Base):
    __tablename__ = "inspection_items"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=True)
    description = Column(String(255))
    description_en = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)


class InspectionStatus(str, enum.Enum):
    pending = "pending"
    submitted = "submitted"
    approved = "approved"


class InspectionRecord(Base):
    __tablename__ = "inspection_records"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(CHAR(36), ForeignKey("students.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False) # Stays Integer
    inspector_id = Column(CHAR(36), ForeignKey("users.id"), nullable=True) # Link to User who performed inspection
    status = Column(Enum(InspectionStatus), nullable=False, default=InspectionStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at = Column(DateTime(timezone=True))
    
    # Field to store the signature as a Base64 encoded string
    signature = Column(Text)

    student = relationship("Student", back_populates="inspections")
    room = relationship("Room", back_populates="inspections")
    inspector = relationship("User", foreign_keys=[inspector_id])
    details = relationship("InspectionDetail", back_populates="record", cascade="all, delete-orphan")


class ItemStatus(str, enum.Enum):
    ok = "ok"
    damaged = "damaged"
    missing = "missing"


class InspectionDetail(Base):
    __tablename__ = "inspection_details"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    record_id = Column(CHAR(36), ForeignKey("inspection_records.id"), nullable=False)
    item_id = Column(CHAR(36), ForeignKey("inspection_items.id"), nullable=False)
    status = Column(Enum(ItemStatus), nullable=False, default=ItemStatus.ok)
    comment = Column(String(500))

    record = relationship("InspectionRecord", back_populates="details")
    item = relationship("InspectionItem")
    photos = relationship("Photo", back_populates="detail", cascade="all, delete-orphan")


class Photo(Base):
    __tablename__ = "photos"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    detail_id = Column(CHAR(36), ForeignKey("inspection_details.id"), nullable=False)
    file_path = Column(String(255), nullable=False) # Path to the stored image
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    detail = relationship("InspectionDetail", back_populates="photos")


# --- Lights Out Check Models ---

class PatrolLocation(Base):
    __tablename__ = "patrol_locations"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False) # e.g., "戶廳", "曬衣間", "一樓大廳"
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False) # Stays Integer
    household = Column(String(50), index=True, nullable=True) # e.g., "A1201", null if it's a building-level area

    building = relationship("Building")
    __table_args__ = (UniqueConstraint('building_id', 'household', 'name', name='_building_household_name_uc'),)


class LightStatus(str, enum.Enum):
    on = "on"
    off = "off"

class LightsOutPatrol(Base):
    __tablename__ = "lights_out_patrols"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False) # Stays Integer
    patroller_id = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    patrol_time = Column(DateTime(timezone=True), server_default=func.now())
    
    building = relationship("Building")
    patroller = relationship("User")
    checks = relationship("LightsOutCheck", back_populates="patrol", cascade="all, delete-orphan")


class LightsOutCheck(Base):
    __tablename__ = "lights_out_checks"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patrol_id = Column(CHAR(36), ForeignKey("lights_out_patrols.id"), nullable=False)
    patrol_location_id = Column(CHAR(36), ForeignKey("patrol_locations.id"), nullable=False)
    status = Column(Enum(LightStatus), nullable=False)
    notes = Column(Text)

    patrol = relationship("LightsOutPatrol", back_populates="checks")
    location = relationship("PatrolLocation")


class TokenType(str, enum.Enum):
    access = "access"
    refresh = "refresh"
    verification = "verification"
    password_reset = "password_reset"

class TokenBlocklist(Base):
    __tablename__ = "token_blocklist"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    jti = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=True) # Link to User
    token_type = Column(Enum(TokenType), nullable=False, default=TokenType.access) # New column
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User") # Establish relationship


from sqlalchemy.dialects.mysql import JSON # Import JSON for MySQL

# --- Audit Log Model ---
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id"), nullable=True) # User who performed the action
    action = Column(String(50), nullable=False) # e.g., "CREATE", "UPDATE", "DELETE", "LOGIN"
    resource_type = Column(String(50), nullable=False) # e.g., "Student", "Room", "InspectionRecord"
    resource_id = Column(String(255), nullable=True) # ID of the resource affected
    details = Column(JSON, nullable=True) # Snapshot of changes, or additional context
    ip_address = Column(String(45), nullable=True) # IP address of the request
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")


# --- Announcement Models ---

class TagType(str, enum.Enum):
    primary = "primary"
    success = "success"
    warning = "warning"
    danger = "danger"
    info = "info"


class Announcement(Base):
    __tablename__ = "announcements"
    
    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    title_en = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)
    content_en = Column(Text, nullable=True)
    tag = Column(String(50), nullable=False)
    tag_type = Column(Enum(TagType), nullable=False, default=TagType.primary)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(CHAR(36), ForeignKey("users.id"), nullable=False)
    
    creator = relationship("User")