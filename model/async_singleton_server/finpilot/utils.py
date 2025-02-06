from fastapi import HTTPException, UploadFile
from langchain_core.documents import Document
import pymupdf4llm
import fitz
import os
import base64


def parse_pdf(file : UploadFile, session_id) -> Document:
    # Pdf Parsing
    page_content = pymupdf4llm.to_markdown(fitz.open(stream=file.file.read(), filetype="pdf"), show_progress=True)

    document = Document(
        page_content=page_content,
        metadata={
            "source" : file.filename,
            "session_id" : session_id
        }
    )

    print(document.metadata)

    return document


def delete_files_in_dir(dir):
    try:
        for filename in os.listdir(dir):
            file_path = os.path.join(dir, filename)
            
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"[Server Log] FILE REMOVED: {file_path}")
            elif os.path.isdir(file_path):
                print(f"[Server Log] REMOVE FAILED (DIR) : {file_path}")
        
        print(f"[Server Log] REMOVED ALL FILES IN PATH : '{dir}'")
    except Exception as e:
        print(f"[Server Log] ERROR : {e}")


def encode_img_base64(folder_path, png_files, source):
    images = []
    for file_name in png_files:
        file_path = os.path.join(folder_path, file_name)
        try:
            with open(file_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
                images.append({
                    "file_name": file_name, 
                    "image_data": img_base64, 
                    "source" : source
                })
            
            os.remove(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read file {file_name}: {str(e)}")
    
    return images