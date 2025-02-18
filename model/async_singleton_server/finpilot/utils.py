from fastapi import HTTPException, UploadFile
from langchain_core.documents import Document
import pymupdf4llm
import fitz
import os
import base64
import asyncio
import aiofiles
from aiofiles.os import remove


async def parse_pdf(file : UploadFile, session_id) -> Document:
    
    async with aiofiles.tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        await temp_file.write(await file.read())
        temp_file_path = temp_file.name

    # Pdf Parsing
    page_content = pymupdf4llm.to_markdown(
        fitz.open(
            temp_file_path
        ), 
        show_progress=True
    )

    document = Document(
        page_content=page_content,
        metadata={
            "source" : file.filename,
            "session_id" : session_id
        }
    )

    return document

async def delete_file(file_path):
    try :
        await remove(file_path)
        print(f"[Server Log] FILE REMOVED: {file_path}")
    except Exception as e:
        print(f"[Server Log] ERROR DELETING FILE {file_path} : \n{e}")

async def delete_files_in_dir(dir):
    tasks = []

    try :
        for filename in os.listdir(dir):
            file_path = os.path.join(dir, filename)

            if os.path.isfile(file_path):
                tasks.append(delete_file(file_path))
            elif os.path.isdir(file_path):
                print(f"[Server Log] REMOVE FAILED (DIR) : {file_path}")
        
        await asyncio.gather(*tasks)
        print(f"[Server Log] REMOVED ALL FILES IN PATH : '{dir}'")
    except Exception as e:
        print(f"[Server Log] ERROR : \n{e}")


async def encode_base64(file_path, file_name, source):
    try:
        async with aiofiles.open(file_path, mode="rb") as img_file:
            img_base64 = base64.b64encode(await img_file.read()).decode("utf-8")
        
        await remove(file_path)

        return {
            "file_name" : file_name,
            "image_data" : img_base64,
            "source" : source
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FAILED TO ENCODE FILE {file_path} : \b{e}")

async def encode_img_base64(folder_path, png_files, source):
    tasks = []

    for file_name in png_files:
        file_path = os.path.join(folder_path, file_name)
        tasks.append(encode_base64(file_path, file_name, source))
    
    images = await asyncio.gather(*tasks)
    
    return images