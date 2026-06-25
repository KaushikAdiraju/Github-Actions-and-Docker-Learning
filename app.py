import os
from fastapi import FastAPI, Request, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from speechtotext.speechtotext import transcribe_audio
import uvicorn

# 1. Load your .env file before anything else runs
load_dotenv()

# 2. Import your compiled LangGraph workflow
from agent.graph import app as agent_app

# 3. Initialize FastAPI
app = FastAPI()

# Mount static files (e.g., your index.html, CSS, JS)
# Assuming 'static' directory for frontend files, adjust if different
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serves the main chat interface."""
    # You might need to adjust the path to your index.html
    # For simplicity, assuming index.html is directly in a 'static' folder
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="index.html not found. Make sure it's in the 'static' directory.")


@app.post("/chat")
async def chat(request: Request):
    """Receives messages from the frontend, passes them to LangGraph, and returns the response."""
    try:
        data = await request.json()
        user_input = data.get("message")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON or missing 'message' field in request body")

    if not user_input:
        raise HTTPException(status_code=400, detail="No message provided")

    # Format the input exactly how our AgentState expects it
    inputs = {"messages": [HumanMessage(content=user_input)]}

    try:
        final_response = ""
        # stream() runs the graph node-by-node.
        for output in agent_app.stream(inputs):
            for key, value in output.items():
                # Extract the text content from the last message generated
                final_response = value["messages"][-1].content

        return JSONResponse(content={"response": final_response})

    except Exception as e:
        print(f"Agent Error: {e}")
        raise HTTPException(status_code=500, detail="Sorry, I encountered an error while thinking.")


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """Receives audio blob from frontend, saves it temporarily, and transcribes it."""
    if not audio:
        raise HTTPException(status_code=400, detail="No audio file found")

    # Save the file temporarily
    temp_path = "temp_audio.webm"
    with open(temp_path, "wb") as f:
        f.write(await audio.read())

    # Send to your STT script
    text = transcribe_audio(temp_path)

    # Clean up the temporary file so your hard drive doesn't fill up!
    if os.path.exists(temp_path):
        os.remove(temp_path)

    if text:
        return JSONResponse(content={"text": text})
    else:
        raise HTTPException(status_code=500, detail="Failed to transcribe audio")


if __name__ == "__main__":
    # Binding to 0.0.0.0 allows the container to accept external mapping requests
    uvicorn.run(app, host="0.0.0.0", port=5000)
