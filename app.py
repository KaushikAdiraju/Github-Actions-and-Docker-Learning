import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from speechtotext.speechtotext import transcribe_audio

# 1. Load your .env file before anything else runs
load_dotenv()

# 2. Import your compiled LangGraph workflow
# We import it as 'agent_app' so it doesn't conflict with the Flask 'app'
from agent.graph import app as agent_app

# 3. Initialize Flask
app = Flask(__name__)

@app.route("/")
def home():
    """Serves the main chat interface."""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Receives messages from the frontend, passes them to LangGraph, and returns the response."""
    user_input = request.json.get("message")
    
    if not user_input:
        return jsonify({"error": "No message provided"}), 400
    
    # Format the input exactly how our AgentState expects it
    inputs = {"messages": [HumanMessage(content=user_input)]}
    
    try:
        final_response = ""
        # stream() runs the graph node-by-node. 
        for output in agent_app.stream(inputs):
            for key, value in output.items():
                # Extract the text content from the last message generated
                final_response = value["messages"][-1].content
                
        return jsonify({"response": final_response})
    
    except Exception as e:
        print(f"Agent Error: {e}")
        return jsonify({"error": "Sorry, I encountered an error while thinking."}), 500
    from speechtotext import transcribe_audio

@app.route("/transcribe", methods=["POST"])
def transcribe():
    """Receives audio blob from frontend, saves it temporarily, and transcribes it."""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file found"}), 400
    
    audio_file = request.files["audio"]
    
    # Save the file temporarily
    temp_path = "temp_audio.webm"
    audio_file.save(temp_path)
    
    # Send to your STT script
    text = transcribe_audio(temp_path)
    
    # Clean up the temporary file so your hard drive doesn't fill up!
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    if text:
        return jsonify({"text": text})
    else:
        return jsonify({"error": "Failed to transcribe audio"}), 500

if __name__ == "__main__":
    app.run(debug=True)