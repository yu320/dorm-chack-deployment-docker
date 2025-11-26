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
    '寢室號碼': 'bed_number',
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
            if not row['building_name'] or not row['bed_number']:
                continue

            # 1. Get or Create Building
            building = await crud.get_or_create_building(db, name=row['building_name'])
            if building.id is None: created_counts["buildings"] += 1 # A bit tricky, might need adjustment

            # Extract room number from bed number (e.g., "A1201-1" -> "A1201")
            room_number = row['bed_number'].split('-')[0]

            # 2. Get or Create Room
            room = await crud.get_or_create_room(db, 
                building_id=building.id, 
                room_number=room_number,
                household=row.get('household'),
                room_type=row.get('room_type')
            )
            if room.id is None: created_counts["rooms"] += 1

            # 3. Get or Create Bed
            bed = await crud.get_or_create_bed(db,
                room_id=room.id,
                bed_number=row['bed_number'],
                bed_type=row.get('bed_type'),
                status=row.get('bed_status')
            )
            if bed.id is None: created_counts["beds"] += 1

            # 4. Update or Create Student (if student data is present)
            if row.get('student_id_number') and row.get('full_name'):
                
                is_foreign = True if row.get('is_foreign_student') == '是' else False

                student_data = schemas.StudentCreate(
                    student_id_number=row['student_id_number'],
                    full_name=row['full_name'],
                    class_name=row.get('class_name'),
                    gender=row.get('gender'),
                    identity_status=row.get('identity_status'),
                    is_foreign_student=is_foreign,
                    enrollment_status=row.get('enrollment_status'),
                    remarks=row.get('remarks'),
                    license_plate=row.get('license_plate'),
                    contract_info=row.get('contract_info'),
                    temp_card_number=row.get('temp_card_number'),
                    bed_id=bed.id # Assign student to this bed
                )
                
                existing_student = await crud.get_student_by_id_number(db, student_id_number=row['student_id_number'])
                student = await crud.update_or_create_student(db, student_data=student_data)

                if existing_student:
                    updated_counts["students"] += 1
                else:
                    created_counts["students"] += 1

        return {
            "message": "Data import completed successfully.",
            "created": created_counts,
            "updated": updated_counts
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")
