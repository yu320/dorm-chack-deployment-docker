export interface Student {
  id: string;
  full_name: string;
  student_id_number: string;
  class_name: string;
  bed_id: number | null;
}

export interface Room {
  id: number;
  room_number: string;
  building_id: number;
}

export interface InspectionDetail {
  id: number;
  item_id: number;
  status: 'ok' | 'damaged';
  comment: string | null;
  photo_url: string | null;
  item: {
    id: number;
    name: string;
  };
}

export interface InspectionRecord {
  id: string;
  student_id: string;
  room_id: number;
  status: 'submitted' | 'passed' | 'failed';
  created_at: string;
  student: Student;
  room: Room;
  details: InspectionDetail[];
  signature: string | null;
}
