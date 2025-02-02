import os
import csv
import openai
import streamlit as st
from openai import OpenAI
from difflib import get_close_matches

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure page
st.set_page_config(
    page_title="PyBuddy - Learn Python!",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "character" not in st.session_state:
    st.session_state.character = "robot"
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Character configurations
CHARACTERS = {
    "robot": {
        "name": "CodeBot",
        "greeting": "Beep-boop! Ready to learn Python?",
        "avatar": "assets/avatars/robot.png",
        "prompt": "You are a friendly robot tutor that explains Python concepts using simple terms and tech analogies."
    },
    "dinosaur": {
        "name": "DinoCoder",
        "greeting": "Rawr! Let's code like dinosaurs!",
        "avatar": "assets/avatars/dinosaur.png",
        "prompt": "You are an enthusiastic dinosaur who teaches Python using prehistoric analogies and fun facts."
    },
    "wizard": {
        "name": "PyWizard",
        "greeting": "Abracadabra! Let's conjure some code!",
        "avatar": "assets/avatars/wizard.png",
        "prompt": "You are a wise wizard who teaches Python through magical metaphors and enchanting examples."
    }
}

# Configure API
def configure_api():
    with st.sidebar:
        st.subheader("\U0001F511 API Configuration")
        provider = st.selectbox("Select AI Provider", ["OpenAI", "DeepSeek"], index=0)
        
        api_key = st.text_input(
            f"{provider} API Key",
            type="password",
            value=os.getenv(f"{provider.upper()}_API_KEY", "")
        )
        return provider, api_key

# Function to run user-submitted code safely
def run_user_code(user_code, func_name, test_cases):
    loc = {}
    try:
        exec(user_code, {}, loc)
        if func_name not in loc:
            return False, "Function not defined"
        user_func = loc[func_name]
        for inp, expected in test_cases:
            result = user_func(*inp)
            if result != expected:
                return False, f"Test failed: {inp} -> Expected {expected}, got {result}"
        return True, "All tests passed! \U0001F389"
    except Exception as e:
        return False, f"Error: {str(e)}"

# Home Page
def show_home():
    st.title("Welcome to PyBuddy! \U0001F40D")
    st.markdown("""
    ## Learn Python Through Interactive Coding!
    Select your favorite tutor and start learning:
    """)
    
    cols = st.columns(3)
    for i, (char, config) in enumerate(CHARACTERS.items()):
        with cols[i]:
            st.image(config["avatar"], use_container_width=True)
            if st.button(config["name"], key=f"char_{i}"):
                st.session_state.character = char
                st.session_state.page = "Learn"
                st.rerun()

# Chat Interface
def show_chat():
    provider, api_key = configure_api()
    client = OpenAI(api_key=api_key)
    
    st.title(f"{CHARACTERS[st.session_state.character]['name']}'s Workshop")
    
    for message in st.session_state.messages:
        avatar = CHARACTERS[st.session_state.character]["avatar"] if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask your coding question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant", avatar=CHARACTERS[st.session_state.character]["avatar"]):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": CHARACTERS[st.session_state.character]['prompt']}] + st.session_state.messages,
                    temperature=0.7
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"API Error: {str(e)}")
                st.session_state.messages.pop()

# Coding Challenges
def show_challenges():
    st.title("Python Coding Challenges")
    challenges = [
        ("Sum Calculator", "add_numbers", [((2, 3), 5), ((-1, 1), 0)]),
        ("Reverse String", "reverse_string", [("hello", "olleh"), ("Python", "nohtyP")]),
        ("Sort List", "sort_list", [([3, 1, 4, 2], [1, 2, 3, 4]), ([5, -2, 0, 3], [-2, 0, 3, 5])])
    ]
    
    for title, func_name, test_cases in challenges:
        with st.expander(f"Challenge: {title}"):
            st.markdown(f"**Write a function named `{func_name}` that meets the following requirements.**")
            code = st.text_area("Write your code here:", height=200, key=f"{func_name}_code")
            if st.button("Run Tests", key=f"{func_name}_test"):
                passed, message = run_user_code(code, func_name, test_cases)
                if passed:
                    st.success(message)
                else:
                    st.error(message)

# Main app navigation
def main():
    if st.session_state.page == "Home":
        show_home()
    elif st.session_state.page == "Learn":
        show_chat()
    elif st.session_state.page == "Challenges":
        show_challenges()
    
    st.sidebar.title("Navigation")
    if st.sidebar.button("\U0001F3E0 Home"):
        st.session_state.page = "Home"
    if st.sidebar.button("\U0001F4DA Learn"):
        st.session_state.page = "Learn"
    if st.sidebar.button("\U0001F3C6 Challenges"):
        st.session_state.page = "Challenges"

if __name__ == "__main__":
    main()
