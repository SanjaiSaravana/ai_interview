/**
 * interview.js - Core Logic for Camera, Mic, and AI HR Interaction
 */

const socket = io();
const chatLog = document.getElementById('chat-log');
const recordBtn = document.getElementById('record-btn');
const finishBtn = document.getElementById('finish-btn');
const videoElement = document.getElementById('videoElement');

// Get the role from the URL parameters
const urlParams = new URLSearchParams(window.location.search);
const currentRole = urlParams.get('role') || "Software Engineer";

// --- 1. INITIALIZE CAMERA & MIC ---
async function setupCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 1280, height: 720 }, 
            audio: true 
        });
        videoElement.srcObject = stream;
    } catch (err) {
        console.error("Error accessing media devices:", err);
        alert("Please allow camera and microphone access to continue.");
    }
}

// --- 2. SPEECH RECOGNITION SETUP (Web Speech API) ---
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (!SpeechRecognition) {
    alert("Your browser does not support Speech Recognition. Please use Chrome.");
}

const recognition = new SpeechRecognition();
recognition.continuous = false; // Stops when user stops talking
recognition.interimResults = false;
recognition.lang = 'en-US';

// Handling the "Hold to Speak" button
recordBtn.onmousedown = () => {
    recognition.start();
    recordBtn.style.background = "#ff4b2b";
    recordBtn.innerText = "Listening...";
};

recordBtn.onmouseup = () => {
    recognition.stop();
    recordBtn.style.background = "#00d4ff";
    recordBtn.innerText = "Hold to Speak";
};

// When user stops speaking, send text to Flask via Socket
recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    addMessage("You", transcript, "user-msg");
    
    // Emit data to backend
    socket.emit('user_answer', {
        text: transcript,
        role: currentRole
    });
};

// --- 3. AI HR RESPONSES ---
socket.on('hr_question', (data) => {
    addMessage("AI HR", data.text, "hr-msg");
    speakText(data.text);
});

function speakText(text) {
    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    
    // Optional: Pick a specific voice if available
    const voices = window.speechSynthesis.getVoices();
    // Prefer a professional sounding voice
    utterance.voice = voices.find(v => v.name.includes("Google US English")) || voices[0];
    
    window.speechSynthesis.speak(utterance);
}

// --- 4. UTILS ---
function addMessage(sender, text, className) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `msg ${className}`;
    msgDiv.innerHTML = `<b>${sender}:</b> ${text}`;
    chatLog.appendChild(msgDiv);
    chatLog.scrollTop = chatLog.scrollHeight;
}

// --- 5. FINISH & REPORT ---
finishBtn.onclick = () => {
    if(confirm("Are you sure you want to end the interview?")) {
        socket.emit('generate_report', { role: currentRole });
        addMessage("System", "Analyzing your performance... please wait.", "");
    }
};

socket.on('final_report', (data) => {
    // Store JSON in session to display on report.html
    sessionStorage.setItem('last_report', data);
    window.location.href = '/report';
});

// Initialize on load
setupCamera();