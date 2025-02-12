# from fastapi import HTTPException
# def handle_error_operation(operation):
#     try:
#         return operation()
#     except ValueError as ve:
#         raise HTTPException(status_code=400, detail=str(ve))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
