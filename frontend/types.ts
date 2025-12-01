// frontend/types.ts

// Enums matching backend models
export type InspectionStatus = 'pending' | 'submitted' | 'approved';
export type ItemStatus = 'ok' | 'damaged' | 'missing';
export type LightStatus = 'on' | 'off';
export type TagType = 'primary' | 'success' | 'warning' | 'danger' | 'info';

// --- Base Interfaces ---

export interface Permission {
  id: string; // UUID
  name: string;
  description?: string | null;
}

export interface Role {
  id: string; // UUID
  name: string;
  permissions: Permission[];
}

export interface User {
  id: string; // UUID
  username: string;
  email?: string | null;
  is_active: boolean;
  roles: Role[];
  student?: Student | null; // Optional relationship
  permissions: string[]; // Flattened list of permission names
}

export interface Student {
  id: string; // UUID
  user_id?: string | null; // UUID
  student_id_number: string;
  full_name: string;
  class_name?: string | null;
  gender?: string | null;
  identity_status?: string | null;
  is_foreign_student?: boolean;
  enrollment_status?: string | null;
  remarks?: string | null;
  license_plate?: string | null;
  contract_info?: string | null;
  temp_card_number?: string | null;
  bed_id?: number | null; // FK to Bed (Integer)
  bed?: Bed | null;
}

export interface Building {
  id: number; // Integer
  name: string;
  rooms?: Room[]; // Nested rooms
}

export interface Room {
  id: number; // Integer
  building_id: number;
  room_number: string;
  household?: string | null;
  room_type?: string | null;
  building?: Building;
  beds?: Bed[];
}

export interface Bed {
  id: number; // Integer
  room_id: number;
  bed_number: string;
  bed_type?: string | null;
  status?: string | null; // e.g., 'available'
  room?: Room;
  student?: Student | null;
}

// --- Inspection Interfaces ---

export interface InspectionItem {
  id: string; // UUID
  name: string;
  name_en?: string | null;
  description?: string | null;
  description_en?: string | null;
  is_active: boolean;
}

export interface Photo {
  id: string; // UUID
  file_path: string;
  uploaded_at: string; // ISO Date string
}

export interface InspectionDetail {
  id: string; // UUID
  record_id?: string; // UUID
  item_id: string; // UUID
  status: ItemStatus;
  comment?: string | null;
  item: InspectionItem;
  photos: Photo[];
}

export interface InspectionRecord {
  id: string; // UUID
  student_id: string; // UUID
  room_id: number; // Integer
  inspector_id?: string | null; // UUID
  status: InspectionStatus;
  created_at: string; // ISO Date string
  submitted_at?: string | null;
  student: Student;
  room: Room;
  inspector?: User | null;
  details: InspectionDetail[];
  signature?: string | null;
}

// --- Announcement Interfaces ---

export interface Announcement {
  id: string; // UUID
  title: string;
  title_en?: string | null;
  content: string;
  content_en?: string | null;
  tag: string;
  tag_type: TagType;
  is_active: boolean;
  created_at: string; // ISO Date string
  updated_at: string; // ISO Date string
  created_by?: string; // UUID
}

export interface PaginatedResponse<T> {
  total: number;
  records: T[];
}