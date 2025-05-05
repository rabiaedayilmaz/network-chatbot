import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import requests
from utils.log import logger


def update_dataframe(existing_df, new_data):
    # Find the first empty index
    empty_indices = existing_df.index[existing_df.isnull().all(axis=1)].tolist()

    if empty_indices:
        # Use the first empty index
        first_empty_index = empty_indices[0]
        existing_df.loc[first_empty_index] = new_data.iloc[0]
    else:
        # If there are no empty indices, append the new data to the end
        existing_df = pd.concat([existing_df, new_data], ignore_index=True)

    existing_df["time"] = pd.to_datetime(existing_df["time"])
    existing_df.sort_values(by="time", ascending=False, inplace=True)
    return existing_df

def record_to_database(user_prompt: str, agent_response: str, agent: str):
    """
    Record chat interactions and contact information to Google Sheets.
    """
    try:
        st.cache_data.clear()
        conn = st.connection("gsheets", 
                             type=GSheetsConnection,
                             )

        # Get user IP and current time
        ip_address = get_user_ip()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Prepare new chat data
        new_chat_data = pd.DataFrame({
            "agent": [agent],
            "time": [current_time],
            "ip_address": [ip_address],
            "user_prompt": [user_prompt],
            "agent_response": [agent_response],
        })

        # Read existing data and update with new data
        existing_data = conn.read(worksheet="Sayfa1")
        updated_data = update_dataframe(existing_data, new_chat_data)
        conn.update(worksheet="Sayfa1", data=updated_data)

    except Exception as e:
        logger.error(f"Google Sheets Connection Failed - {e}")
        logger.info(f"Failed to save data...\nUser Prompt: {user_prompt}\nResponse: {agent_response}")
        #st.error("Bilgilerinizi paylaştığınız için teşekkürler!")  # Updated message

def get_user_ip():
    """
    Get user's IP address using ipify API.
    """
    try:
        ip = requests.get('https://api64.ipify.org?format=json', timeout=5).json()['ip']
        return ip
    except Exception as e:
        logger.error(f"Problem with getting user IP - {e}")
        return None

def init_google_sheet():
    """Initialize Google Sheet with required columns if not exists"""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Initialize contact_info sheet
        try:
            existing_data = conn.read(worksheet="Sayfa1")
        except Exception:
            # If worksheet doesn't exist, create it with headers
            headers = pd.DataFrame(columns=[
                "agent", "time", "ip_address", "user_prompt", "agent_response"
            ])
            conn.update(worksheet="Sayfa1", data=headers)
                
        return True
    except Exception as e:
        st.error(f"Failed to initialize Google Sheet: {e}")
        return False

if __name__ == "__main__":
    init_google_sheet()