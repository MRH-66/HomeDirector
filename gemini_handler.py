# ArchitecturalRAGSystem/gemini_handler.py
import google.generativeai as genai
from system_prompt import SYSTEM_PROMPT, IMAGE_SYSTEM_PROMPT
from history_manager import save_conversation
import streamlit as st
from typing import Tuple, Optional, Any, List, Dict 
from google.generativeai.types import HarmCategory, HarmBlockThreshold 
from google.generativeai.generative_models import GenerativeModel, ChatSession
from datetime import datetime

# Import AppConfig from your config module
# This assumes config.py (which defines AppConfig) is in the same directory 
# or your project structure allows this import (e.g., if both are in root, or src/ is in PYTHONPATH)
# If config.py is in the root and this file is in src/gemini_chat_handler.py, you'd use:
# from ..config import AppConfig (if running as part of a package)
# For simplicity, if all .py files are in the root, this is fine:
from config import AppConfig # Make sure config.py defines AppConfig

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# Modified to accept an AppConfig instance
# ArchitecturalRAGSystem/gemini_chat_handler.py
# ... (imports, SAFETY_SETTINGS, setup_model remain the same as the FULL one I provided before) ...

def setup_model(app_config: AppConfig) -> Tuple[Optional[GenerativeModel], Optional[GenerativeModel], bool]:
    """Setup the Gemini models and return instances."""
    try:
        genai.configure(api_key=app_config.GOOGLE_API_KEY) 
        
        chatbot_model_name = app_config.CHATBOT_MODEL_NAME
        image_model_name = app_config.IMAGE_ANALYSIS_MODEL_NAME
        
        text_model_instance = genai.GenerativeModel(
            model_name=chatbot_model_name,
            generation_config={"temperature": 0.7, "top_p": 0.95, "top_k": 0},
            system_instruction=SYSTEM_PROMPT, # Assumes your library version supports this
            safety_settings=SAFETY_SETTINGS
        )
        
        multimodal_model_instance = genai.GenerativeModel(
             model_name=image_model_name, 
             generation_config={"temperature": 0.2, "top_p": 0.95, "top_k": 0},
             safety_settings=SAFETY_SETTINGS
        )
        use_multimodal_flag = True

        print(f"Gemini Handler: Chatbot model '{chatbot_model_name}' and Image Analysis model '{image_model_name}' initialized.")
        return text_model_instance, multimodal_model_instance, use_multimodal_flag

    except Exception as e:
        # Check for the specific "system_instruction" error
        if "system_instruction" in str(e).lower() and "unexpected keyword argument" in str(e).lower():
            st.error(f"Error: Your 'google-generativeai' library version may not support 'system_instruction'. Attempting fallback.")
            print(f"Gemini Handler: system_instruction not supported, will use history prepending for system prompt.")
            # Fallback: Initialize without system_instruction, will be handled by start_chat_session
            try:
                text_model_instance = genai.GenerativeModel(
                    model_name=chatbot_model_name,
                    generation_config={"temperature": 0.7, "top_p": 0.95, "top_k": 0},
                    safety_settings=SAFETY_SETTINGS
                )
                multimodal_model_instance = genai.GenerativeModel(
                     model_name=image_model_name, 
                     generation_config={"temperature": 0.2, "top_p": 0.95, "top_k": 0},
                     safety_settings=SAFETY_SETTINGS
                )
                st.session_state.system_prompt_in_history = True # Flag that we need to manually add system prompt
                print(f"Gemini Handler: Fallback models initialized. System prompt will be added to history.")
                return text_model_instance, multimodal_model_instance, True
            except Exception as e_fallback:
                st.error(f"Error setting up Gemini model even with fallback: {e_fallback}")
                print(f"Error setting up Gemini model with fallback: {e_fallback}")
                return None, None, False
        else:
            st.error(f"Error setting up Gemini model: {e}")
            print(f"Error setting up Gemini model: {e}")
            return None, None, False

def start_chat_session(model: GenerativeModel, 
                       history_for_api: Optional[List[Dict[str,Any]]] = None
                       ) -> Optional[ChatSession]:
    """Starts a new chat session."""
    if not model:
        return None
    
    api_ready_history = []
    # Handle system prompt if system_instruction wasn't supported during model setup
    if st.session_state.get("system_prompt_in_history", False) and not history_for_api:
        api_ready_history = [
            {'role': 'user', 'parts': [{'text': SYSTEM_PROMPT}]},
            {'role': 'model', 'parts': [{'text': "Understood. I am ready to assist with architectural design."}]}
        ]
        print("DEBUG: Prepending system prompt to chat history for API in start_chat_session.")

    if history_for_api: # Append actual chat history if provided
        for msg in history_for_api:
            if msg['role'] == 'user':
                api_ready_history.append({'role': 'user', 'parts': [{'text': msg['content']}]})
            elif msg['role'] == 'assistant':
                 api_ready_history.append({'role': 'model', 'parts': [{'text': msg['content']}]})
                
    try:
        chat = model.start_chat(history=api_ready_history)
        return chat
    except Exception as e:
        print(f"Error starting chat session: {e}")
        st.error(f"Could not start chat session: {e}")
        return None

# handle_text_input remains the same (it uses the chat_session passed to it)
# ... (handle_text_input code from your last working version) ...
def handle_text_input(user_input: str, 
                      chat_session: Optional[ChatSession], 
                      app_config: AppConfig): 
    if not chat_session:
        st.error("Chat session is not available. Please start a new conversation.")
        st.session_state.messages.append({"role": "assistant", "content": "Error: Chat session not initialized."})
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    response_obj = None 
    try:
        with st.spinner("Assistant is thinking..."):
            # The chat_session should already have the correct history, including system prompt
            response_obj = chat_session.send_message(user_input) 
            response_text = ""
            if response_obj.candidates and response_obj.candidates[0].finish_reason.name == "SAFETY":
                response_text = "I'm sorry, I can't respond to that due to safety guidelines. Please rephrase."
                st.warning(response_text)
            elif response_obj.text:
                 response_text = response_obj.text
            else: 
                response_text = "I'm sorry, I didn't get a valid response. Please try again."
                st.warning(response_text)

        st.session_state.messages.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.write(response_text)

        history_to_save = [msg for msg in st.session_state.messages if msg["role"] != "system"]
        save_conversation(
            session_id=st.session_state.session_id,
            start_timestamp_str=st.session_state.start_time_str,
            end_timestamp_str=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            messages=history_to_save,
            history_dir=app_config.HISTORY_DIR
        )

    except Exception as e:
        error_msg = f"Error processing text input: {str(e)}"
        st.error(error_msg)
        if response_obj and hasattr(response_obj, 'prompt_feedback'):
            error_msg += f"\nFeedback: {response_obj.prompt_feedback}"
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        history_to_save = [msg for msg in st.session_state.messages if msg["role"] != "system"]
        save_conversation(
            session_id=st.session_state.session_id,
            start_timestamp_str=st.session_state.start_time_str,
            end_timestamp_str=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            messages=history_to_save,
            history_dir=app_config.HISTORY_DIR
        )


def handle_image_analysis_request(
    image_bytes: bytes,
    multimodal_model: GenerativeModel, # Model for image analysis
    text_chat_session: Optional[ChatSession], # The main text chat session
    app_config_for_save: AppConfig,
    analysis_prompt_text: str = IMAGE_SYSTEM_PROMPT
):
    """
    Handles image analysis and updates both Streamlit messages and the text chat session's history.
    """
    # 1. Add placeholder to Streamlit messages for immediate UI update
    placeholder_message = "[Analyzing image, please wait...]"
    st.session_state.messages.append({"role": "assistant", "content": placeholder_message})
    
    # Find index of placeholder for later update
    placeholder_index = -1
    for idx, msg in reversed(list(enumerate(st.session_state.messages))):
        if msg["role"] == "assistant" and msg["content"] == placeholder_message:
            placeholder_index = idx
            break
    
    # It's often better to trigger a rerun here if the placeholder needs to show *before* the spinner.
    # However, let's try to make it work within one flow first.
    # If UX is clunky, then add a targeted rerun for placeholder.

    response_obj = None
    analysis_result_text = ""
    try:
        # This spinner will appear in the main app area while this function runs
        with st.spinner("AI is analyzing the image..."):
            image_part = {"mime_type": "image/png", "data": image_bytes}
            prompt_parts = [analysis_prompt_text, image_part]

            response_obj = multimodal_model.generate_content(prompt_parts, safety_settings=SAFETY_SETTINGS)
            
            if response_obj.candidates and response_obj.candidates[0].finish_reason.name == "SAFETY":
                analysis_result_text = "I'm sorry, I encountered an issue analyzing this image due to safety guidelines."
            elif response_obj.text:
                analysis_result_text = response_obj.text 
            else:
                analysis_result_text = "Image analysis did not produce a result. Please try again."

        # 2. Update Streamlit messages with the actual analysis result
        if placeholder_index != -1:
             st.session_state.messages[placeholder_index] = {"role": "assistant", "content": analysis_result_text}
        else: # Fallback if placeholder wasn't found (shouldn't happen)
            st.session_state.messages.append({"role": "assistant", "content": analysis_result_text})

        # 3. CRITICAL: Update the main text chat session's history
        if text_chat_session and analysis_result_text:
            try:
                # Simulate the assistant providing the analysis to the text chat session
                # This makes the text model "aware" of the image analysis content
                
                # First, add the user's implicit request that led to the analysis
                # This assumes the user message that triggered analysis is the second to last message
                # in st.session_state.messages (user prompt, then assistant placeholder)
                user_request_for_analysis = "I've uploaded an image for analysis. Here are the details." # Generic
                if len(st.session_state.messages) >= 2 and st.session_state.messages[-2]["role"] == "user":
                    user_request_for_analysis = st.session_state.messages[-2]["content"] + " (Image was provided and analyzed)."

                # It's safer to use text_chat_session.history directly if API supports it.
                # Or send messages to update it.
                # Let's try sending messages to ensure the session state is managed by the SDK.
                # This might result in duplicate "User: please analyze" if not careful.
                # The best way is often to reconstruct history and start a new chat if directly modifying history is problematic.
                # For Gemini's ChatSession, we can append to its history list, but it must be done
                # in the correct format {'role': 'user'/'model', 'parts': [{'text': '...'}]}
                
                # Add user's (implicit) image submission turn to text chat history
                text_chat_session.history.append(
                     {'role': 'user', 'parts': [{'text': user_request_for_analysis}]}
                )
                # Add model's analysis turn to text chat history
                text_chat_session.history.append(
                     {'role': 'model', 'parts': [{'text': f"Okay, I have analyzed the image. The key findings are: {analysis_result_text}"}]} # Prepend a phrase
                )
                print("DEBUG: Image analysis summary added to text chat session history.")

            except Exception as e_hist:
                print(f"DEBUG: Error updating text chat session history with image analysis: {e_hist}")
                # Optionally add a message to st.session_state.messages about this failure for UX
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"(Internal note: Failed to fully integrate image analysis into ongoing chat context: {e_hist})"
                })


    except Exception as e:
        error_msg = f"Critical error during image analysis: {str(e)}"
        if placeholder_index != -1:
            st.session_state.messages[placeholder_index] = {"role": "assistant", "content": f"Error analyzing image: {error_msg}"}
        else:
            st.session_state.messages.append({"role": "assistant", "content": f"Error analyzing image: {error_msg}"})
    
    finally:
        # 4. Save conversation (always, even if errors occur during analysis/history update)
        history_to_save = [msg for msg in st.session_state.messages if msg["role"] != "system"]
        save_conversation(
            session_id=st.session_state.session_id,
            start_timestamp_str=st.session_state.start_time_str,
            end_timestamp_str=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            messages=history_to_save,
            history_dir=app_config_for_save.HISTORY_DIR
        )
        # 5. Rerun Streamlit to display the final analysis message (or error)
        return analysis_result_text