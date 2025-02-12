from pathlib import Path
import os
from fastapi import HTTPException
from finpilot.utils import delete_files_in_dir


async def upload_csvs(
    session_id, file
):
    # Set Path to save CSV File
    upload_path = Path(os.getcwd()) / "data" / f"{session_id}"
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    
    # Delete Any Remaing CSV Files
    if len(os.listdir(upload_path)) > 0:
        await delete_files_in_dir(upload_path)

    # Set File Path
    upload_file_path = upload_path / file.filename

    # Save File to Local dir
    try :
        with open(upload_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error ocurred : {e}")
    

async def delete_csvs(
    session_id
):
    # Set Path to delete CSV File
    delete_path = Path(os.getcwd()) / "data" / f"{session_id}"
    if not os.path.exists(delete_path):
        os.makedirs(delete_path)
    
    # Delete Any Remaing CSV Files
    if len(os.listdir(delete_path)) > 0:
        await delete_files_in_dir(delete_path)
