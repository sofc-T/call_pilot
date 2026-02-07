const talkBtn = document.getElementById('talkBtn');
const statusText = document.getElementById('statusText');
const log = document.getElementById('log');
const visualizer = document.getElementById('visualizer');
const textInput = document.getElementById('textInput');
const sendBtn = document.getElementById('sendBtn');
const hostEmailSpan = document.getElementById('hostEmail');

// Load Config
async function loadConfig() {
    try {
        const response = await fetch('/config');
        const data = await response.json();
        if (data.host_email) {
            hostEmailSpan.innerText = data.host_email;
        }
    } catch (e) {
        console.error("Failed to load config", e);
    }
}

loadConfig();

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

// 1. Initialize Recorder
async function initMic() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            audioChunks = [];
            
            setUIState('processing');
            await sendAudio(audioBlob);
        };

        return true;
    } catch (err) {
        console.error("Mic Error:", err);
        statusText.innerText = "Please allow microphone access";
        return false;
    }
}

// 2. Button Logic
talkBtn.addEventListener('click', async () => {
    if (!mediaRecorder) {
        setUIState('initializing');
        const success = await initMic();
        if (!success) {
            setUIState('ready');
            return;
        }
    }

    if (!isRecording) {
        // Start Recording
        mediaRecorder.start();
        isRecording = true;
        setUIState('recording');
    } else {
        // Stop Recording
        mediaRecorder.stop();
        isRecording = false;
        // State change handled in onstop
    }
});

// Text Input Logic
sendBtn.addEventListener('click', () => {
    const text = textInput.value.trim();
    if (text) {
        sendText(text);
    }
});

textInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        const text = textInput.value.trim();
        if (text) {
            sendText(text);
        }
    }
});

async function sendText(text) {
    textInput.value = ''; // Clear input
    addMessage('user', text);
    setUIState('processing');

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: text,
                session_id: sessionId
            })
        });

        if (!response.ok) {
            throw new Error(`Server Error: ${response.statusText}`);
        }

        const data = await response.json();
        
        if (data.ai_text) {
             addMessage("ai", data.ai_text);
        }

        setUIState('ready');

        // Play Audio
        if (data.audio_url) {
            const audio = new Audio(data.audio_url);
            audio.play();
        }

    } catch (error) {
        console.error(error);
        addMessage("ai", "Sorry, I encountered an error.");
        setUIState('ready');
    }
}

// 3. Send to Backend
// Generate a simple Session ID
const sessionId = 'session_' + Math.random().toString(36).substr(2, 9);

async function sendAudio(blob) {
    const formData = new FormData();
    formData.append("file", blob, "input.webm");
    formData.append("session_id", sessionId);

    try {
        const response = await fetch("/talk", {
            method: "POST",
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server Error: ${response.statusText}`);
        }

        const data = await response.json();

        // Update UI with Chat Bubbles
        if (data.user_text) {
            addMessage("user", data.user_text);
        }
        
        if (data.ai_text) {
             addMessage("ai", data.ai_text);
        }

        setUIState('ready');

        // Play Audio
        if (data.audio_url) {
            const audio = new Audio(data.audio_url);
            audio.play();
        }

    } catch (error) {
        console.error(error);
        addMessage("ai", "Sorry, I encountered an error.");
        setUIState('ready');
    }
}

function addMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    
    // Icon
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.innerHTML = role === 'ai' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
    
    // Bubble
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.innerText = text;

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    
    log.appendChild(msgDiv);
    
    // Scroll to new message
    log.scrollTop = log.scrollHeight;
}

// UI State Management
function setUIState(state) {
    talkBtn.classList.remove('recording', 'processing');
    visualizer.classList.remove('active');
    talkBtn.disabled = false;
    
    // Reset Icon
    talkBtn.innerHTML = '<i class="fas fa-microphone"></i>';

    switch (state) {
        case 'ready':
            statusText.innerText = "Tap to speak";
            break;
        case 'initializing':
            statusText.innerText = "Accessing microphone...";
            talkBtn.disabled = true;
            break;
        case 'recording':
            statusText.innerText = "Listening...";
            talkBtn.classList.add('recording');
            talkBtn.innerHTML = '<i class="fas fa-stop"></i>'; // Stop icon
            visualizer.classList.add('active');
            break;
        case 'processing':
            statusText.innerText = "Thinking...";
            talkBtn.classList.add('processing');
            talkBtn.innerHTML = '<i class="fas fa-circle-notch"></i>'; // Spinner (CSS handles spin)
            break;
    }
}