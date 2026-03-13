from ui import render_chat_interface, STREAMLIT_MODE

if STREAMLIT_MODE:
    import streamlit as st
    from config import PAGE_CONFIG
    
    # Configure page settings (only for Streamlit mode)
    st.set_page_config(**PAGE_CONFIG)

# Render the chat interface
if __name__ == "__main__":
    render_chat_interface()