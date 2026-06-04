import os
import json
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET', 'secret_key_123')
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# In-memory storage for session history
# In a production app, use Redis or a Database
chat_histories = {}

# --- ROUTES ---

@app.route('/')
def index():
    """Landing page for role selection."""
    return render_template('index.html')

@app.route('/interview')
def interview():
    """The live interview room."""
    role = request.args.get('role', 'Software Engineer')
    return render_template('interview.html', role=role)

@app.route('/report')
def report():
    """The final performance analysis page."""
    return render_template('report.html')

# --- SOCKET LOGIC ---

@socketio.on('user_answer')
def handle_answer(data):
    role = data.get('role', 'Software Engineer')
    user_text = data.get('text', '')
    session_id = request.sid

    # Initialize history if new session
    if session_id not in chat_histories:
        chat_histories[session_id] = [
            {"role": "system", "content": (
                f"You are a professional HR Manager interviewing a candidate for a {role} position. "
                "Ask one challenging question at a time. Keep responses under 50 words. "
                "Be realistic and professional."
            )}
        ]
    
    # Append user answer
    chat_histories[session_id].append({"role": "user", "content": user_text})

    try:
        # Get AI HR Response using Llama 3.3
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=chat_histories[session_id],
            temperature=0.7,
            max_tokens=150
        )
        
        ai_response = completion.choices[0].message.content
        chat_histories[session_id].append({"role": "assistant", "content": ai_response})
        
        # Send voice-ready text back to frontend
        emit('hr_question', {'text': ai_response})
        
    except Exception as e:
        print(f"Error calling Groq: {e}")
        emit('hr_question', {'text': "I'm sorry, I'm having trouble connecting. Could you repeat that?"})

@socketio.on('generate_report')
def handle_report(data):
    session_id = request.sid
    role = data.get('role', 'Candidate')
    history = chat_histories.get(session_id, [])
    
    if not history:
        emit('final_report', json.dumps({"feedback": "No interview data found."}))
        return

    # Prompt for evaluation
    evaluation_prompt = (
        f"Analyze this interview for a {role} position. "
        "Provide a JSON object with: 'technical_score' (1-10), 'soft_skills_score' (1-10), "
        "'feedback' (a 2-sentence summary), and 'areas_to_improve' (list of 3 strings). "
        f"Transcript: {history}"
    )

    try:
        report_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": evaluation_prompt}],
            response_format={"type": "json_object"}
        )
        
        # Send the JSON string to the frontend
        emit('final_report', report_completion.choices[0].message.content)
        
        # Clean up memory
        del chat_histories[session_id]
        
    except Exception as e:
        print(f"Evaluation Error: {e}")
        emit('final_report', json.dumps({"feedback": "Error generating report."}))

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5007)