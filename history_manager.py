# ArchitecturalRAGSystem/history_manager.py
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional # Ensure Optional and Any are imported

def save_conversation(session_id: str, 
                      start_timestamp_str: str, 
                      end_timestamp_str: str,
                      messages: list, 
                      history_dir: str = "conversation_history"):
    """
    Save conversation history to a JSON file.
    """
    os.makedirs(history_dir, exist_ok=True)
    
    json_filename = os.path.join(history_dir, f"conversation_{session_id}_{start_timestamp_str}.json")
    
    conversation_data = {
        "session_id": session_id,
        "timestamp_started": start_timestamp_str,
        "timestamp_ended": end_timestamp_str,
        "last_updated_save_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": messages # Should be a list of {"role": "user/assistant", "content": "..."}
    }

    try:
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)
        # print(f"Conversation saved to: {json_filename}") # Optional: for debugging
    except Exception as e:
        print(f"Error saving conversation to {json_filename}: {e}")


def load_conversation(filename: str, history_dir: str = "conversation_history") -> Optional[Dict[str, Any]]:
    """
    Load a conversation from a JSON file.
    """
    filepath = os.path.join(history_dir, filename)

    if not os.path.exists(filepath):
        # print(f"Conversation file not found: {filepath}") # Optional: for debugging
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            conversation_data = json.load(f)
        return conversation_data
    except Exception as e:
        print(f"Error loading conversation from {filepath}: {e}")
        return None


def list_conversations(history_dir: str = "conversation_history") -> list:
    """
    List all saved conversation JSON files.
    """
    if not os.path.exists(history_dir):
        return []
    try:
        # Filter for JSON files and a common prefix if you have one
        conversations = [f for f in os.listdir(history_dir) if f.startswith("conversation_") and f.endswith(".json")]
        return sorted(conversations, reverse=True) # Show newest first
    except Exception as e:
        print(f"Error listing conversations in {history_dir}: {e}")
        return []