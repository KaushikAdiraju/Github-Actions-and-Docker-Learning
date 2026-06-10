document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");

    function appendMessage(text, sender) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", sender === "user" ? "user-message" : "ai-message");
        messageDiv.innerText = text;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to bottom
        return messageDiv;
    }

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        // 1. Show user message and clear input
        appendMessage(text, "user");
        userInput.value = "";
        
        // 2. Show loading indicator
        const loadingDiv = appendMessage("Thinking and searching the web...", "ai");
        loadingDiv.classList.add("loading");

        try {
            // 3. Send request to Flask backend
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            });

            const data = await response.json();
            
            // 4. Remove loading indicator and show actual response
            chatBox.removeChild(loadingDiv);
            
            if (data.error) {
                appendMessage(data.error, "ai");
            } else {
                appendMessage(data.response, "ai");
            }

        } catch (error) {
            chatBox.removeChild(loadingDiv);
            appendMessage("Connection error. Is the Flask server running?", "ai");
        }
    }

    // --- Speech to Text Logic ---
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    const micBtn = document.getElementById("mic-btn");

    micBtn.addEventListener("click", async () => {
        if (!isRecording) {
            // START RECORDING
            try {
                // Ask user for mic permissions
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                
                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };
                
                mediaRecorder.onstop = async () => {
                    // When recording stops, package the audio into a Blob
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    audioChunks = []; // Reset for next time
                    
                    const formData = new FormData();
                    formData.append("audio", audioBlob, "recording.webm");
                    
                    userInput.placeholder = "Transcribing...";
                    userInput.disabled = true;
                    
                    try {
                        // Send audio to Flask
                        const response = await fetch("/transcribe", {
                            method: "POST",
                            body: formData
                        });
                        const data = await response.json();
                        
                        if(data.text) {
                            // Put the transcribed text directly into the input box
                            // so you can review it before hitting Send!
                            userInput.value = data.text;
                        }
                    } catch (error) {
                        console.error("Transcription error:", error);
                        alert("Error transcribing audio.");
                    }
                    
                    userInput.placeholder = "Ask me anything...";
                    userInput.disabled = false;
                };
                
                // Start the recording process
                mediaRecorder.start();
                isRecording = true;
                micBtn.classList.add("recording"); // Starts the red pulsing animation
                userInput.placeholder = "Listening... Click mic again to stop.";
                
            } catch (err) {
                alert("Microphone access denied or unavailable.");
            }
        } else {
            // STOP RECORDING
            mediaRecorder.stop();
            isRecording = false;
            micBtn.classList.remove("recording"); // Stops the animation
            
            // Turn off the microphone completely
            mediaRecorder.stream.getTracks().forEach(track => track.stop()); 
        }
    });

    // Send on button click or Enter key
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });
});