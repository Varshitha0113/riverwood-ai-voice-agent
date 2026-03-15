import streamlit as st
from gtts import gTTS
import speech_recognition as sr
from fuzzywuzzy import fuzz
from io import BytesIO
import base64
import streamlit.components.v1 as components

# --- 1. Page Configuration & Theme-Friendly UI ---
st.set_page_config(page_title="Riverwood AI Concierge", page_icon="🎙️", layout="wide")

# Updated CSS: Removed hardcoded dark colors to ensure visibility in Dark Mode
st.markdown("""
    <style>
    .main-title { 
        font-size: 36px; 
        font-weight: bold; 
        text-align: center; 
        margin-bottom: 10px;
    }
    /* Simple border that works in both modes */
    .agent-container {
        padding: 15px;
        border: 1px solid #888;
        border-radius: 10px;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">🎙️ Riverwood AI Voice Support</div>', unsafe_allow_html=True)
st.write("<center>Ask about Project Timeline, Budget, Location, or Amenities</center>", unsafe_allow_html=True)

# --- 2. Knowledge Base ---
knowledge_base = {
    "project deadline completion finish": "The project deadline is March 30, 2026.",
    "budget cost price": "The estimated budget of the project is 2.5 crore INR.",
    "location where site": "The project site is located in Ongole Mandal, Andhra Pradesh.",
    "progress status": "The project is currently progressing on schedule.",
    "construction building process": "Construction includes land preparation, foundation work, and structural development.",
    "site visit visit project": "Yes, customers can schedule a site visit during weekends.",
    "contact phone email": "You can contact Riverwood at support@riverwoodindia.com or call +91 9876543218.",
    "book plot booking procedure": "Plots can be booked by contacting our sales team or visiting the office.",
    "plot price cost": "Plot prices vary depending on size and location in the layout.",
    "amenities facilities": "The project includes internal roads, electricity, water supply, and green spaces.",
    "developer builder company": "Riverwood Projects LLP is the developer of this township.",
    "completion finish": "The first phase is expected to complete by early 2026.",
    "investment return": "The project is considered a good investment due to infrastructure growth.",
    "documents legal approvals": "All legal approvals and documentation are available for verification."
}

# --- 3. Session State ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- 4. Core Helper Functions ---

def stop_audio():
    """Stops all active audio playback."""
    stop_js = """<script>
        var audios = parent.document.querySelectorAll('audio');
        audios.forEach(function(a) { a.pause(); a.src = ""; a.remove(); });
    </script>"""
    components.html(stop_js, height=0)

def speak_and_display(text):
    """Voice synthesis and auto-playback with theme-safe display."""
    tts = gTTS(text=text, lang='en')
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    audio_base64 = base64.b64encode(audio_buffer.read()).decode()
    
    # Using st.info for the agent message as it automatically adapts to Dark/Light mode
    st.info(f"**Agent:** {text}")

    audio_html = f"""
        <audio autoplay="true">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
    """
    components.html(audio_html, height=0)

def get_response(question):
    q = question.lower().strip()

    # --- Conversational Layer (Politeness & Closures) ---
    thanks_list = ["thank you", "thanks", "ok thanks", "okay thank you", "thx"]
    closure_list = ["no", "nothing else", "that is all", "no thanks", "bye", "goodbye", "no more"]
    greetings_list = ["hi", "hello", "hey", "good morning"]
    
    if any(word in q for word in thanks_list):
        return "You're very welcome! I'm happy to help. Do you have any other questions about Riverwood?"
    
    if q in closure_list:
        return "Understood. It was a pleasure assisting you today! Have a wonderful day."

    if any(word in q for word in greetings_list):
        return "Hello! I am your Riverwood AI assistant. How can I help you today?"

    # --- Knowledge Base Match (Fuzzy Matching) ---
    best_score = 0
    best_answer = None

    for key in knowledge_base:
        score = fuzz.token_set_ratio(q, key)
        if score > best_score:
            best_score = score
            best_answer = knowledge_base[key]

    if best_score > 55:
        return best_answer
    else:
        return "I'm sorry, I couldn't find specific details on that. Please ask about the location, budget, or amenities."

# --- 5. UI Layout ---

# Sidebar for History (Automatically handles Dark Mode)
with st.sidebar:
    st.header("💬 Chat History")
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()
    st.divider()
    for speaker, text in reversed(st.session_state.history):
        if speaker == "User":
            st.write(f"👤 **You:** {text}")
        else:
            st.write(f"🤖 **Agent:** {text}")
        st.write("---")

# Main Controls
col_voice, col_stop = st.columns([1, 1])

with col_voice:
    if st.button("🎤 Ask by Voice", use_container_width=True):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.toast("Listening...")
            try:
                audio = recognizer.listen(source, timeout=5)
                question = recognizer.recognize_google(audio)
                st.write(f"🗨️ **Recognized:** {question}")
                
                response = get_response(question)
                st.session_state.history.append(("User", question))
                st.session_state.history.append(("Agent", response))
                speak_and_display(response)
            except:
                st.error("Could not understand audio. Please try again.")

with col_stop:
    if st.button("🛑 Stop Audio", use_container_width=True):
        stop_audio()

st.divider()

# Text input
user_input = st.text_input("Or type your question here:", placeholder="Try: 'What is the location?'")

if user_input:
    response = get_response(user_input)
    st.session_state.history.append(("User", user_input))
    st.session_state.history.append(("Agent", response))
    speak_and_display(response)

# Action Buttons (Professional UI touch)
st.write("### Quick Inquiries")
q_col1, q_col2, q_col3 = st.columns(3)
with q_col1:
    if st.button("📍 Location"): speak_and_display(knowledge_base["location where site"])
with q_col2:
    if st.button("💰 Plot Price"): speak_and_display(knowledge_base["plot price cost"])
with q_col3:
    if st.button("📞 Contact Us"): speak_and_display(knowledge_base["contact phone email"])

# Start Greeting
if not st.session_state.history:
    if st.button("🚀 Start Agent Session"):
        greet = "Hello, I am the Riverwood support agent. How can I help you today?"
        speak_and_display(greet)