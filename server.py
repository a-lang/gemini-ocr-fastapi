from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from gemini_ocr import ocr_infer
import json
import tempfile
import uvicorn

# Constants
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB = 1*1024*1024 bytes
ALLOWED_CONTENT_TYPES = ["application/pdf"]

app = FastAPI()

""" Sample codes:
# http://127.0.0.1:8000/
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

# http://127.0.0.1:8000/square?num=3
@app.get("/square")
async def calculate_square(num: int):
    return {"number": num, "square": num ** 2}

# http://127.0.0.1:8000/users/123
@app.get("/users/{user_id}")
async def read_user(user_id: int):
    return {"user_id": user_id}

# curl -X POST "http://127.0.0.1:8000/uploadfile/" -H "accept: application/json" -H "Content-Type:multipart/form-data" -F "file=@your.pdf"
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile | None = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        return {"filename": file.filename}
@app.post("/tempfile/")
async def temp_file(file: UploadFile | None = None):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
    temp_file.close

    return {"filepath": temp_file.name, "filename": file.filename, "content_type": file.content_type, "size": file.size}
"""

@app.post("/ocr/")
async def ocr(file: UploadFile | None = None):
    # No file uploaded
    if not file:
        return {"message": "No upload file sent"}
    
    # Validate file type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )
    
    # Check file size (limit to xxMB)
    content = await file.read()
    file_size = len(content)
    await file.seek(0)  # Reset file pointer after reading
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds the limit of {MAX_FILE_SIZE / (1024 * 1024)} MB"
            )
    
    # Gemini OCR
    # This section handles OCR processing for uploaded files using the Gemini-2.5-flash model.
    # It creates a temporary file to store the uploaded content, performs OCR inference,
    # and returns the result as JSON. Error handling is included to catch and report any issues.
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            result = ocr_infer("gemini-2.5-flash", temp_file.name)
        temp_file.close
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result # JSON type
    
@app.get("/health")
async def health():
    #return {"message": "Production app is ready"}
    return JSONResponse(content={"message": "Production app is ready"})


if __name__ == "__main__":
    #uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True, workers=1)
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)