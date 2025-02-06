from finpilot.session import get_session_app
import os
from pathlib import Path
from fastapi import HTTPException
from finpilot.utils import delete_files_in_dir, encode_img_base64
from fastapi.responses import JSONResponse

async def query_non_image(
    question, session_id, chat_option, redis
):

    # Create/Load the LangGraph Application according to Session ID
    pilot = await get_session_app(
        redis_client=redis,
        session_id=session_id
    )

    input = {
        "question" : question,
        "chat_option" : chat_option
    }

    config = {
        "configurable" : {"thread_id" : session_id},
        "recursion_limit" : 40
    }
    
    # invoke answer
    print("[Server Log] INVOKING PILOT ANSWER (NON-IMAGE)")
    answer = await pilot.ainvoke(input=input, config=config)
    print("[Server Log] PILOT ANSWER INVOKED")

    # return answer
    return {
        "answer" : answer["generation"],
        "source" : answer.get("source", [])
    }


async def query_image(
    question, session_id, chat_option, redis
):
    
    # Set Folder Path for Image saving
    folder_path = f"./charts/{session_id}/"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # Set Data Path for Get CSV Data
    data_path = Path(os.getcwd()) / "data" / f"{session_id}"
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    # Create/Load the LangGraph Application according to Session ID
    pilot = await get_session_app(
        redis_client=redis,
        session_id=session_id
    )

    input = {
        "question" : question,
        "chat_option" : chat_option
    }

    config = {
        "configurable" : {"thread_id" : session_id},
        "recursion_limit" : 40
    }

    # invoke answer
    print("[Server Log] INVOKING PILOT ANSWER (NON-IMAGE)")
    answer = await pilot.ainvoke(input=input, config=config)
    print("[Server Log] PILOT ANSWER INVOKED")

    # Get PNG File list
    png_files = [f for f in os.listdir(folder_path) if f.endswith(".png")]
    if not png_files:
        raise HTTPException(status_code=404, detail="No PNG files found in the folder")
    
    source_value = answer["source"]
    if isinstance(source_value, str):
        source_value = [source_value]
        
    # Encode Image to Base64 type
    images = encode_img_base64(folder_path, png_files, source=source_value)

    if chat_option == "데이터 시각화 (Upload)":
        # Delete Remaining CSV Files
        if len(os.listdir(data_path)) > 0:
            delete_files_in_dir(data_path)
    

    # Return Image data as JSON Form
    return JSONResponse(content={
        "images": images
    })