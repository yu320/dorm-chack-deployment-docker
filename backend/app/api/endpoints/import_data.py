from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
import io
import numpy as np

from ... import crud, schemas, auth

router = APIRouter()

# Define the mapping from Chinese headers to English fields
HEADER_MAPPING = {
    '棟別': 'building_name',
    '戶別': 'household',
    '寢室號碼': 'bed_number', # This column contains "A1201-1" which is effectively bed number
    '班級': 'class_name',
    '學號': 'student_id_number',
    '姓名': 'full_name',
    '性別': 'gender',
    '身分別': 'identity_status',
    '外籍生': 'is_foreign_student',
    '在學狀態': 'enrollment_status',
    '備註': 'remarks',
    '床型': 'bed_type',
    '床位可用狀態': 'bed_status',
    '房型': 'room_type',
    '臨時卡號': 'temp_card_number',
    '合約書': 'contract_info',
    '車牌號碼': 'license_plate',
}

@router.post("/upload", status_code=200, dependencies=[Depends(auth.PermissionChecker("manage_users"))])
async def upload_data(file: UploadFile = File(...), db: AsyncSession = Depends(auth.get_db)):
    """
    Upload and process a CSV or Excel file to import student and room data.
    """
    if not file.filename.endswith(('.csv', '.xlsx')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV or Excel file.")

    try:
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))

        # Rename columns using the mapping
        df.rename(columns=HEADER_MAPPING, inplace=True)
        
        # Replace numpy NaN values with None for JSON serialization
        df = df.replace({np.nan: None})

        created_counts = {"buildings": 0, "rooms": 0, "beds": 0, "students": 0}
        updated_counts = {"students": 0}

        for _, row in df.iterrows():
            # Skip rows where essential data is missing
            if not row.get('building_name') or not row.get('bed_number'):
                continue

            # 1. Get or Create Building
            building_name = row['building_name']
            building = await crud.crud_building.get_by_name(db, name=building_name)
            if not building:
                building = await crud.crud_building.create(db, obj_in=schemas.BuildingCreate(name=building_name))
                created_counts["buildings"] += 1

            # Extract room number from bed number (e.g., "A1201-1" -> "A1201")
            room_number = row['bed_number'].split('-')[0]

            # 2. Get or Create Room
            room = await crud.crud_room.get_by_building_and_number(db, building_id=building.id, room_number=room_number)
            if not room:
                room_in = schemas.RoomCreate(
                    building_id=building.id,
                    room_number=room_number,
                    household=row.get('household'),
                    room_type=row.get('room_type')
                )
                room = await crud.crud_room.create(db, obj_in=room_in)
                created_counts["rooms"] += 1
            
            # 3. Get or Create Bed
            bed_number = row['bed_number']
            bed = await crud.crud_bed.get_by_number(db, room_id=room.id, bed_number=bed_number)
            if not bed:
                bed_in = schemas.BedCreate(
                    room_id=room.id,
                    bed_number=bed_number,
                    bed_type=row.get('bed_type'),
                    status=row.get('bed_status') or 'available'
                )
                bed = await crud.crud_bed.create(db, obj_in=bed_in)
                created_counts["beds"] += 1
            else:
                 # Update status if present in row
                 if row.get('bed_status'):
                     await crud.crud_bed.update(db, db_obj=bed, obj_in={'status': row['bed_status']})

            # 4. Update or Create Student (if student data is present)
            student_id = row.get('student_id_number')
            full_name = row.get('full_name')

            if student_id and full_name:
                is_foreign = True if row.get('is_foreign_student') == '是' else False
                
                # Prepare student data
                student_data = {
                    "student_id_number": str(student_id), # Ensure string
                    "full_name": full_name,
                    "class_name": row.get('class_name'),
                    "gender": row.get('gender'),
                    "identity_status": row.get('identity_status'),
                    "is_foreign_student": is_foreign,
                    "enrollment_status": row.get('enrollment_status'),
                    "remarks": row.get('remarks'),
                    "license_plate": row.get('license_plate'),
                    "contract_info": row.get('contract_info'),
                    "temp_card_number": str(row.get('temp_card_number')) if row.get('temp_card_number') else None,
                    "bed_id": bed.id
                }
                
                existing_student = await crud.crud_student.get_by_id_number(db, student_id_number=str(student_id))
                
                if existing_student:
                    # Update existing student
                    # Note: We need to use schemas.StudentUpdate or just a dict for update in CRUDBase
                    # But CRUDBase.update expects obj_in to be Union[UpdateSchemaType, Dict[str, Any]]
                    await crud.crud_student.update(db, db_obj=existing_student, obj_in=student_data)
                    updated_counts["students"] += 1
                else:
                    # Create new student
                    # Ensure all required fields for StudentCreate are present
                    student_in = schemas.StudentCreate(**student_data)
                    await crud.crud_student.create(db, obj_in=student_in)
                    created_counts["students"] += 1

        return {
            "message": "Data import completed successfully.",
            "created": created_counts,
            "updated": updated_counts
        }

    except Exception as e:
        # In a real scenario, we might want to log the error and specific row
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")