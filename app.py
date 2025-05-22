# # ArchitecturalRAGSystem/app.py
# import streamlit as st
# import uuid
# from datetime import datetime
# from PIL import Image
# import io
# import json
# from typing import List, Dict, Any, Optional

# # Adjust imports based on your file structure
# from config import load_app_config
# from history_manager import save_conversation
# from system_prompt import SYSTEM_PROMPT, IMAGE_SYSTEM_PROMPT
# from gemini_handler import setup_model, start_chat_session, handle_text_input, handle_image_analysis_request

# # --- Load Configuration (Once per app run, effectively) ---
# try:
#     config = load_app_config()
# except ValueError as e:
#     st.error(f"Configuration Error: {e}")
#     st.stop()

# # --- One-Time Initialization Block (Runs only once per user browser session) ---
# if "app_initialized" not in st.session_state:
#     print("DEBUG: APP IS INITIALIZING FOR THE VERY FIRST TIME (or after full refresh/cache clear)")
    
#     # 1. Initialize Models
#     text_model, multimodal_model, use_multimodal = setup_model(config)
#     if not text_model or (use_multimodal and not multimodal_model):
#         st.error("Fatal Error: Gemini models could not be initialized. App cannot continue.")
#         st.stop() # Stop execution if models fail
#     st.session_state.text_model_global = text_model
#     st.session_state.multimodal_model_global = multimodal_model
#     st.session_state.use_multimodal_global = use_multimodal
#     print("DEBUG: Models initialized and stored in session state.")

#     # 2. Initialize Chat Session State Variables
#     session_id = str(uuid.uuid4())
#     start_time_obj = datetime.now()
#     start_time_str = start_time_obj.strftime("%Y-%m-%d_%H-%M-%S")

#     st.session_state.session_id = session_id
#     st.session_state.start_time_obj = start_time_obj
#     st.session_state.start_time_str = start_time_str
#     st.session_state.active = True
#     st.session_state.image_being_analyzed_id = None 
#     st.session_state.last_image_analysis_content = None
#     st.session_state.image_uploader_key_counter = 0 # Initialize uploader key

#     st.session_state.messages = [
#         {"role": "assistant", "content": "Hello! I'm your AI Design Assistant. How can I help you with your architectural or interior design project today?"}
#     ]
    
#     if st.session_state.text_model_global:
#         st.session_state.chat = start_chat_session(st.session_state.text_model_global, history_for_api=[])
#         if st.session_state.chat:
#             print(f"DEBUG: New chat session created for initial session_id: {session_id}")
#         else:
#             st.error("Initial chat session could not be created.")
#             print(f"DEBUG: Failed to initialize initial chat session for session_id: {session_id}")
#     else:
#         st.session_state.chat = None
#         st.error("Text model not available. Cannot start chat session.")

#     st.session_state.app_initialized = True # Set flag to indicate initialization is done
#     print("DEBUG: App initialization complete.")
# else:
#     print(f"DEBUG: App already initialized. Current session_id: {st.session_state.session_id}")


# # --- Helper Function to Reset for a New Conversation (Called by button) ---
# def start_new_chat_conversation():
#     """Resets state for a new logical conversation."""
#     print("DEBUG: 'New Conversation' button clicked. Resetting chat session state.")
#     # Save current conversation IF it has meaningful content
#     current_session_message_count = len(st.session_state.get("messages", []))
#     if current_session_message_count > 1 or \
#        (current_session_message_count == 1 and st.session_state.messages[0]["role"] != "assistant"):
#         history_to_save = [msg for msg in st.session_state.messages if msg.get("role") != "system"]
#         save_conversation(
#             session_id=st.session_state.session_id,
#             start_timestamp_str=st.session_state.start_time_str,
#             end_timestamp_str=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
#             messages=history_to_save,
#             history_dir=config.HISTORY_DIR
#         )
#         print(f"DEBUG: Saved old conversation {st.session_state.session_id}")

#     # Reset chat-specific parts of session state
#     session_id = str(uuid.uuid4())
#     start_time_obj = datetime.now()
#     start_time_str = start_time_obj.strftime("%Y-%m-%d_%H-%M-%S")

#     st.session_state.session_id = session_id
#     st.session_state.start_time_obj = start_time_obj
#     st.session_state.start_time_str = start_time_str
#     st.session_state.active = True
#     st.session_state.image_being_analyzed_id = None
#     st.session_state.last_image_analysis_content = None
#     st.session_state.messages = [
#         {"role": "assistant", "content": "Okay, let's start a fresh conversation! How can I help you with your design project?"}
#     ]
#     if st.session_state.text_model_global:
#         st.session_state.chat = start_chat_session(st.session_state.text_model_global, history_for_api=[])
#         if st.session_state.chat:
#             print(f"DEBUG: New logical chat session started: {session_id}")
#         else:
#             st.error("Failed to start new chat session.")
    
#     st.session_state.image_uploader_key_counter = st.session_state.get('image_uploader_key_counter', 0) + 1
#     st.rerun() # Rerun to apply changes


# # --- UI Layout ---
# st.set_page_config(page_title="AI Design Assistant", layout="wide")
# st.title("AI Architecture & Interior Design Assistant 📐✨")
# st.write("Describe your project, ask design questions, or upload an image for analysis.")

# # --- Main Chat Area ---
# chat_container = st.container() # Define it once at a higher scope
# with chat_container:
#     for message in st.session_state.get("messages", []): # Use .get() for safety
#         if message.get("role") == "system": 
#             continue
#         with st.chat_message(message["role"]):
#             content = message.get("content", "")
#             if isinstance(content, str) and content.strip().startswith("```json"):
#                 try:
#                     json_str_cleaned = content.strip().replace("```json", "").replace("```", "").strip()
#                     parsed_json = json.loads(json_str_cleaned)
#                     st.json(parsed_json)
#                 except json.JSONDecodeError:
#                     st.text(content) 
#             elif isinstance(content, str) and content.strip().startswith("{") and content.strip().endswith("}"):
#                 try:
#                     parsed_json = json.loads(content.strip())
#                     st.json(parsed_json)
#                 except json.JSONDecodeError:
#                      st.write(content) 
#             else:
#                 st.write(content)

# # --- Sidebar ---
# with st.sidebar:
#     st.title("Controls & Info")
#     st.write(f"Session ID: {st.session_state.get('session_id', 'N/A')[:8]}...")
#     st.write(f"Started: {st.session_state.get('start_time_str', 'N/A')}")
#     st.divider()

#     # Image Upload
#     if st.session_state.get("active", True):
#         st.subheader("Upload Image for Analysis")
#         uploader_key = f"image_uploader_{st.session_state.get('image_uploader_key_counter', 0)}"
#         uploaded_image_file = st.file_uploader(
#             "Upload a floor plan or reference image.",
#             type=["jpg", "jpeg", "png"],
#             key=uploader_key
#         )

#         analysis_button_disabled = uploaded_image_file is None or \
#                                    (uploaded_image_file is not None and \
#                                     st.session_state.get("image_being_analyzed_id") == uploaded_image_file.file_id)
        
#         # Temporarily display file info for debugging
#         # if uploaded_image_file:
#         #     st.write(f"DEBUG Sidebar: Uploaded: {uploaded_image_file.name}, ID: {uploaded_image_file.file_id}")
#         #     st.write(f"DEBUG Sidebar: image_being_analyzed_id: {st.session_state.get('image_being_analyzed_id')}")
#         #     st.write(f"DEBUG Sidebar: Button disabled: {analysis_button_disabled}")


#         if st.button("Analyze Uploaded Image", disabled=analysis_button_disabled, key=f"analyze_btn_{uploader_key}"):
#             if uploaded_image_file is not None: # This check is redundant if button is properly disabled
#                 if st.session_state.use_multimodal_global and st.session_state.multimodal_model_global:
#                     try:
#                         st.session_state.image_being_analyzed_id = uploaded_image_file.file_id # Mark as processing

#                         image_bytes = uploaded_image_file.getvalue()
#                         pil_image = Image.open(io.BytesIO(image_bytes))

#                         user_analysis_request_text = "Please analyze this uploaded image and provide a detailed architectural breakdown:"
                        
#                         # Add user message for display (handler will add it to chat history for LLM)
#                         st.session_state.messages.append({"role": "user", "content": user_analysis_request_text})
#                         # For immediate display of image in user's turn (before assistant replies)
#                         # This might require a slightly different handling in the message display loop
#                         # For now, we rely on the rerun from the handler.

#                         # Call handler - it will manage adding placeholder, getting analysis, updating message, and rerunning
#                         handle_image_analysis_request(
#                             image_bytes=image_bytes,
#                             multimodal_model=st.session_state.multimodal_model_global,
#                             text_chat_session=st.session_state.get("chat"),
#                             app_config_for_save=config 
#                         )
#                     except Exception as e:
#                         st.error(f"Error initiating image analysis from button: {e}")
#                         st.session_state.image_being_analyzed_id = None # Reset on error
#                 else:
#                     st.warning("Multimodal model is not available for image analysis.")
        
#         elif uploaded_image_file and (st.session_state.get("image_being_analyzed_id") != uploaded_image_file.file_id):
#             try:
#                 pil_image_preview = Image.open(uploaded_image_file)
#                 st.image(pil_image_preview, caption="Ready to Analyze", use_column_width=True)
#             except Exception as e:
#                 st.error(f"Could not display image preview: {e}")

#     st.divider()
#     st.header("Session Management")
#     if st.button("✨ New Conversation", key="new_convo_btn_sidebar"):
#         start_new_chat_conversation() # Call the helper function

#     if st.session_state.get("active", True):
#         if st.button("🛑 Stop Current Conversation", key="stop_convo_btn_sidebar"):
#             st.session_state.active = False 
#             current_session_message_count = len(st.session_state.get("messages", []))
#             if current_session_message_count > 1 or \
#                (current_session_message_count == 1 and st.session_state.messages[0]["role"] != "assistant"):
#                 history_to_save = [msg for msg in st.session_state.messages if msg.get("role") != "system"]
#                 save_conversation(
#                     session_id=st.session_state.session_id,
#                     start_timestamp_str=st.session_state.start_time_str,
#                     end_timestamp_str=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
#                     messages=history_to_save,
#                     history_dir=config.HISTORY_DIR
#                 )
#             st.success("Conversation ended and saved. Click 'New Conversation' to start another.")
#             st.rerun()
#     else: 
#         st.warning("This conversation has ended. Start a 'New Conversation' from the sidebar.")

#     st.divider()
#     st.header("Instructions")
#     st.write("""
#     - Type your design needs or questions below.
#     - Upload images via the sidebar for analysis.
#     - Manage conversations with sidebar buttons.
#     """)

# # --- User Text Input Field (at the bottom) ---
# if st.session_state.get("active", True):
#     user_prompt = st.chat_input("What are your design ideas or questions?")
#     if user_prompt: # This block executes when user presses Enter
#         chat_session_obj = st.session_state.get("chat")
#         if chat_session_obj:
#             handle_text_input(user_prompt, chat_session_obj, config)
#             # The handle_text_input function should NOT call st.rerun().
#             # The st.chat_input being processed naturally causes a rerun.
#             # If handle_text_input calls rerun, and this block also calls rerun, that's a problem.
#             # Let's remove explicit rerun here if handler doesn't need it.
#             # The act of submitting chat_input triggers a rerun.
#         else:
#             st.error("Chat session not properly initialized. Please start a new conversation.")
# else: 
#     st.info("This conversation has ended. Start a 'New Conversation' from the sidebar to chat again.")





# ArchitecturalRAGSystem/app.py
import streamlit as st
import uuid
from datetime import datetime
from PIL import Image
import io
import json
from typing import List, Dict, Any, Optional

# Adjust imports based on your file structure
from config import load_app_config
from history_manager import save_conversation # We might not need to call this directly for download
from system_prompt import SYSTEM_PROMPT, IMAGE_SYSTEM_PROMPT
from gemini_handler import setup_model, start_chat_session, handle_text_input, handle_image_analysis_request

# --- Load Configuration (Once per app run, effectively) ---
try:
    config = load_app_config()
except ValueError as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

# --- One-Time Initialization Block (Runs only once per user browser session) ---
if "app_initialized" not in st.session_state:
    print("DEBUG: APP IS INITIALIZING FOR THE VERY FIRST TIME (or after full refresh/cache clear)")
    text_model, multimodal_model, use_multimodal = setup_model(config)
    if not text_model or (use_multimodal and not multimodal_model):
        st.error("Fatal Error: Gemini models could not be initialized. App cannot continue.")
        st.stop()
    st.session_state.text_model_global = text_model
    st.session_state.multimodal_model_global = multimodal_model
    st.session_state.use_multimodal_global = use_multimodal
    print("DEBUG: Models initialized and stored in session state.")

    session_id = str(uuid.uuid4())
    start_time_obj = datetime.now()
    start_time_str = start_time_obj.strftime("%Y-%m-%d_%H-%M-%S")

    st.session_state.session_id = session_id
    st.session_state.start_time_obj = start_time_obj
    st.session_state.start_time_str = start_time_str
    st.session_state.active = True
    st.session_state.image_being_analyzed_id = None
    st.session_state.last_image_analysis_content = None
    st.session_state.image_uploader_key_counter = 0

    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your AI Design Assistant. How can I help you with your architectural or interior design project today?"}
    ]
    
    if st.session_state.text_model_global:
        st.session_state.chat = start_chat_session(st.session_state.text_model_global, history_for_api=[])
        if st.session_state.chat:
            print(f"DEBUG: New chat session created for initial session_id: {session_id}")
        else:
            st.error("Initial chat session could not be created.")
            print(f"DEBUG: Failed to initialize initial chat session for session_id: {session_id}")
    else:
        st.session_state.chat = None
        st.error("Text model is not available. Cannot start chat session.")

    st.session_state.app_initialized = True
    print("DEBUG: App initialization complete.")
else:
    print(f"DEBUG: App already initialized. Current session_id: {st.session_state.get('session_id', 'N/A')}")


# --- Helper Function to Reset for a New Conversation (Called by button) ---
def start_new_chat_conversation():
    """Resets state for a new logical conversation."""
    print("DEBUG: 'New Conversation' button clicked. Resetting chat session state.")
    current_session_message_count = len(st.session_state.get("messages", []))
    if current_session_message_count > 1 or \
       (current_session_message_count == 1 and st.session_state.messages[0]["role"] != "assistant"):
        history_to_save = [msg for msg in st.session_state.messages if msg.get("role") != "system"]
        save_conversation(
            session_id=st.session_state.session_id,
            start_timestamp_str=st.session_state.start_time_str,
            end_timestamp_str=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            messages=history_to_save,
            history_dir=config.HISTORY_DIR
        )
        print(f"DEBUG: Saved old conversation {st.session_state.session_id}")

    session_id = str(uuid.uuid4())
    start_time_obj = datetime.now()
    start_time_str = start_time_obj.strftime("%Y-%m-%d_%H-%M-%S")

    st.session_state.session_id = session_id
    st.session_state.start_time_obj = start_time_obj
    st.session_state.start_time_str = start_time_str
    st.session_state.active = True
    st.session_state.image_being_analyzed_id = None
    st.session_state.last_image_analysis_content = None
    st.session_state.messages = [
        {"role": "assistant", "content": "Okay, let's start a fresh conversation! How can I help you with your design project?"}
    ]
    if st.session_state.text_model_global:
        st.session_state.chat = start_chat_session(st.session_state.text_model_global, history_for_api=[])
        if st.session_state.chat:
            print(f"DEBUG: New logical chat session started: {session_id}")
        else:
            st.error("Failed to start new chat session.")
    
    st.session_state.image_uploader_key_counter = st.session_state.get('image_uploader_key_counter', 0) + 1
    st.rerun()


# --- UI Layout ---
st.set_page_config(page_title="AI Design Assistant", layout="wide")
st.title("AI Architecture & Interior Design Assistant 📐✨")
st.write("Describe your project, ask design questions, or upload an image for analysis.")

# --- Main Chat Area ---
chat_container = st.container()
with chat_container:
    for message in st.session_state.get("messages", []):
        if message.get("role") == "system": 
            continue
        with st.chat_message(message["role"]):
            content = message.get("content", "")
            if isinstance(content, str) and content.strip().startswith("```json"):
                try:
                    json_str_cleaned = content.strip().replace("```json", "").replace("```", "").strip()
                    parsed_json = json.loads(json_str_cleaned)
                    st.json(parsed_json)
                except json.JSONDecodeError:
                    st.text(content) 
            elif isinstance(content, str) and content.strip().startswith("{") and content.strip().endswith("}"):
                try:
                    parsed_json = json.loads(content.strip())
                    st.json(parsed_json)
                except json.JSONDecodeError:
                     st.write(content) 
            else:
                st.write(content)

# --- Sidebar ---
with st.sidebar:
    st.title("Controls & Info")
    st.write(f"Session ID: {st.session_state.get('session_id', 'N/A')[:8]}...")
    st.write(f"Started: {st.session_state.get('start_time_str', 'N/A')}")
    st.divider()

    # Image Upload
    if st.session_state.get("active", True):
        st.subheader("Upload Image for Analysis")
        uploader_key = f"image_uploader_{st.session_state.get('image_uploader_key_counter', 0)}"
        uploaded_image_file = st.file_uploader(
            "Upload a floor plan or reference image.",
            type=["jpg", "jpeg", "png"],
            key=uploader_key
        )

        analysis_button_disabled = uploaded_image_file is None or \
                                   (uploaded_image_file is not None and \
                                    st.session_state.get("image_being_analyzed_id") == uploaded_image_file.file_id)
        
        if st.button("Analyze Uploaded Image", disabled=analysis_button_disabled, key=f"analyze_btn_{uploader_key}"):
            if uploaded_image_file is not None: 
                if st.session_state.use_multimodal_global and st.session_state.multimodal_model_global:
                    try:
                        st.session_state.image_being_analyzed_id = uploaded_image_file.file_id 

                        image_bytes = uploaded_image_file.getvalue()
                        pil_image = Image.open(io.BytesIO(image_bytes))

                        user_analysis_request_text = "Please analyze this uploaded image and provide a detailed architectural breakdown:"
                        
                        st.session_state.messages.append({"role": "user", "content": user_analysis_request_text})
                        
                        # No need to display image here manually in chat_container,
                        # handle_image_analysis_request and the main message loop will do it on rerun.
                        
                        handle_image_analysis_request(
                            image_bytes=image_bytes,
                            multimodal_model=st.session_state.multimodal_model_global,
                            text_chat_session=st.session_state.get("chat"),
                            app_config_for_save=config 
                        )
                    except Exception as e:
                        st.error(f"Error initiating image analysis from button: {e}")
                        st.session_state.image_being_analyzed_id = None 
                else:
                    st.warning("Multimodal model is not available for image analysis.")
        
        elif uploaded_image_file and (st.session_state.get("image_being_analyzed_id") != uploaded_image_file.file_id):
            try:
                pil_image_preview = Image.open(uploaded_image_file)
                st.image(pil_image_preview, caption="Ready to Analyze", use_column_width=True)
            except Exception as e:
                st.error(f"Could not display image preview: {e}")

    st.divider()
    st.header("Session Management")
    if st.button("✨ New Conversation", key="new_convo_btn_sidebar"):
        start_new_chat_conversation() 

    if st.session_state.get("active", True):
        if st.button("🛑 Stop Current Conversation", key="stop_convo_btn_sidebar"):
            st.session_state.active = False 
            current_session_message_count = len(st.session_state.get("messages", []))
            if current_session_message_count > 1 or \
               (current_session_message_count == 1 and st.session_state.messages[0]["role"] != "assistant"):
                history_to_save = [msg for msg in st.session_state.messages if msg.get("role") != "system"]
                save_conversation(
                    session_id=st.session_state.session_id,
                    start_timestamp_str=st.session_state.start_time_str,
                    end_timestamp_str=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                    messages=history_to_save,
                    history_dir=config.HISTORY_DIR
                )
            st.success("Conversation ended and saved. Click 'New Conversation' to start another.")
            st.rerun()
    else: 
        st.warning("This conversation has ended. Start a 'New Conversation' from the sidebar.")

    # --- NEW: Download Conversation Button ---
    st.divider()
    st.subheader("Download Chat")
    
    # Prepare data for download
    # Only include user and assistant messages for the download content
    current_chat_messages_for_download = [
        msg for msg in st.session_state.get("messages", []) if msg.get("role") in ["user", "assistant"]
    ]
    
    if current_chat_messages_for_download: # Only show button if there's something to download
        conversation_to_download = {
            "session_id": st.session_state.get("session_id", "unknown_session"),
            "timestamp_started": st.session_state.get("start_time_str", "unknown_time"),
            "timestamp_downloaded": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            "messages": current_chat_messages_for_download
        }
        json_string_to_download = json.dumps(conversation_to_download, indent=2, ensure_ascii=False)
        
        st.download_button(
            label="📥 Download Conversation (JSON)",
            data=json_string_to_download,
            file_name=f"conversation_{st.session_state.get('session_id', 'session')}_{st.session_state.get('start_time_str', 'timestamp')}.json",
            mime="application/json",
            key="download_chat_btn"
        )
    else:
        st.info("No messages in the current conversation to download yet.")
    # --- END: Download Conversation Button ---

    st.divider()
    st.header("Instructions")
    st.write("""
    - Type your design needs or questions below.
    - Upload images via the sidebar for analysis.
    - Manage conversations with sidebar buttons.
    - Download the current chat at any time.
    """)

# --- User Text Input Field (at the bottom) ---
if st.session_state.get("active", True):
    user_prompt = st.chat_input("What are your design ideas or questions?")
    if user_prompt: 
        chat_session_obj = st.session_state.get("chat")
        if chat_session_obj:
            handle_text_input(user_prompt, chat_session_obj, config)
            # The act of submitting chat_input triggers a rerun by Streamlit.
            # Explicit st.rerun() here might be redundant or cause double rerun.
            # Test to see if input clears and new messages appear without it.
            # If not, add st.rerun() back.
        else:
            st.error("Chat session not properly initialized. Please start a new conversation.")
else: 
    st.info("This conversation has ended. Start a 'New Conversation' from the sidebar to chat again.")