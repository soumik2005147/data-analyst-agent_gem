from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pipeline import run_pipeline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify domains like ["https://app.example.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# Default GET endpoint
@app.get("/")
async def read_root():
    return {"message": "Hello, world!"}

# POST endpoint to handle uploaded data analysis task
@app.post("/api/")
async def analyze_task(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".txt"):
            return JSONResponse(
                status_code=400,
                content={"error": "Only .txt files are supported"}
            )

        contents = await file.read()
        task_description = contents.decode("utf-8").strip()

        # Log or process the task description here
        print("\nReceived Task:", task_description)

        answer = run_pipeline(task_description)

        return answer

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"API:  error occurred: {str(e)}"}
        )
