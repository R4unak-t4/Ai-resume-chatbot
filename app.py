# FILE: app.py (Streamlit Frontend - No Summary Generator)
# Run with: streamlit run app.py

import streamlit as st
from backend import chatbot,load_vectorstore,load_single_pdf,is_vectorstore_loaded,save_vectorstore
from langchain_core.messages import HumanMessage
import uuid
import os

# Page configuration
st.set_page_config(
    page_title = "Resume Assistant",
    page_icon = "📄",
    layout = "wide",
    initial_sidebar_state = "expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp header {
        background-color: #2563eb;
    }
    .sidebar .sidebar-content {
        background-color: #f1f5f9;
    }
    h1 {
        color: #2563eb;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
""",unsafe_allow_html = True)


# ========== AUTO-LOAD RESUME ON STARTUP ==========
@st.cache_resource
def initialize_knowledge_base():
    """Load resume on app startup (cached)"""
    if is_vectorstore_loaded():
        return True,"Resume already loaded"

    # Try loading from saved vector store first
    if os.path.exists('./resume_vectorstore'):
        try:
            load_vectorstore('./resume_vectorstore')
            return True,"Loaded from saved vector store"
        except Exception as e:
            st.warning(f"Could not load saved vector store: {e}")

    # Try loading from PDF
    pdf_files=['resume.pdf','cv.pdf','my_resume.pdf']
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            try:
                load_single_pdf(pdf_file)
                save_vectorstore('./resume_vectorstore')
                return True,f"Loaded from {pdf_file}"
            except Exception as e:
                st.error(f"Error loading {pdf_file}: {e}")

    return False,"No resume found"


# Initialize knowledge base
kb_status,kb_message=initialize_knowledge_base()


def generate_thread_id():
    """Generate unique thread ID"""
    return str(uuid.uuid4())


def reset_chat():
    """Reset chat and create new thread"""
    thread_id=generate_thread_id()
    st.session_state['thread_id']=thread_id
    st.session_state['message_history']=[]
    st.session_state['chat_threads'].append(thread_id)
    st.rerun()


def load_conversation(thread_id):
    """Load conversation from specific thread"""
    try:
        state=chatbot.get_state(config = {'configurable':{'thread_id':thread_id}})
        if hasattr(state,'values') and 'messages' in state.values:
            return state.values['messages']
    except Exception as e:
        st.error(f"Error loading conversation: {e}")
    return []


# ========== SESSION STATE MANAGEMENT ==========

if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]

if 'thread_id' not in st.session_state:
    st.session_state['thread_id']=generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads']=[st.session_state['thread_id']]

# ========== SIDEBAR UI ==========

with st.sidebar:
    st.markdown("### 📄 Resume Assistant")
    st.title('Chat Interface')

    # Knowledge base status indicator
    if kb_status:
        st.success(f"✅ Resume Loaded")
        st.caption(kb_message)
    else:
        st.error(f"❌ {kb_message}")
        st.info("Please add 'resume.pdf' to the project folder and restart.")

    st.markdown('---')

    # New Chat Button
    col1,col2=st.columns([3,1])
    with col1:
        if st.button('➕ New Chat',use_container_width = True,type = "primary"):
            reset_chat()
    with col2:
        total_chats=len(st.session_state['chat_threads'])
        st.metric("",total_chats)

    st.markdown('---')

    # Quick Info Section
    with st.expander("💡 What can I help with?",expanded = True):
        st.markdown("""
        **Ask me about:**

        🎓 Education & Qualifications

        💼 Work Experience

        🛠️ Technical Skills

        📁 Projects & Achievements

        📜 Certifications

        📧 Contact Information
        """)

    st.markdown('---')
    st.header('💬 Chat History')

    # Display chat threads (simplified - no summaries)
    if len(st.session_state['chat_threads']) > 0:
        for i,thread_id in enumerate(reversed(st.session_state['chat_threads'])):
            # Highlight active thread
            is_active=(thread_id == st.session_state['thread_id'])
            button_type="primary" if is_active else "secondary"

            # Thread button with icon
            icon="💬" if is_active else "📝"
            display_text=f"Chat {len(st.session_state['chat_threads']) - i}"

            if st.button(
                    f"{icon} {display_text}",
                    key = f"chat_{thread_id}_{i}",
                    use_container_width = True,
                    type = button_type
            ):
                if thread_id != st.session_state['thread_id']:
                    st.session_state['thread_id']=thread_id
                    messages=load_conversation(thread_id)

                    temp_messages=[]
                    for message in messages:
                        if isinstance(message,HumanMessage):
                            role='user'
                        else:
                            role='assistant'
                        temp_messages.append({
                            'role':role,
                            'content':message.content
                        })

                    st.session_state['message_history']=temp_messages
                    st.rerun()
    else:
        st.info("No chat history yet. Start a conversation!")

    st.markdown('---')

    # Admin section for manual PDF loading
    with st.expander("⚙️ Upload Resume",expanded = False):
        uploaded_file=st.file_uploader("Upload Resume PDF",type = ['pdf'])
        if uploaded_file is not None:
            # Save uploaded file
            with open("temp_upload.pdf","wb") as f:
                f.write(uploaded_file.getbuffer())

            if st.button("Process Resume"):
                with st.spinner("Processing resume..."):
                    try:
                        load_single_pdf("temp_upload.pdf")
                        save_vectorstore('./resume_vectorstore')
                        st.success("✅ Resume processed successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # Footer
    st.markdown("""
    <div style='text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 2rem;'>
        <p>Resume Assistant Chatbot</p>
        <p>Powered by LangGraph</p>
    </div>
    """,unsafe_allow_html = True)

# ========== MAIN CHAT INTERFACE ==========

# Header
col1,col2,col3=st.columns([2,3,2])
with col2:
    st.title('📄 Resume Assistant')
    st.markdown('*Ask me anything about the resume*')

st.markdown('---')

# Warning if knowledge base not loaded
if not kb_status:
    st.warning(
        "⚠️ Resume not loaded. Please upload a resume PDF in the sidebar or add 'resume.pdf' to the project folder.")

# Display chat messages
chat_container=st.container()

with chat_container:
    for message in st.session_state['message_history']:
        role=message['role']
        content=message['content']

        if role == 'user':
            with st.chat_message('user',avatar = '👤'):
                st.markdown(content)
        else:
            with st.chat_message('assistant',avatar = '🤖'):
                st.markdown(content)

# Chat input
user_input=st.chat_input('Ask me about experience, skills, education, or anything else...')

if user_input:
    # Add user message to history
    st.session_state['message_history'].append({
        'role':'user',
        'content':user_input
    })

    # Display user message
    with st.chat_message('user',avatar = '👤'):
        st.markdown(user_input)

    # Generate AI response
    config={'configurable':{'thread_id':st.session_state['thread_id']}}

    with st.chat_message('assistant',avatar = '🤖'):
        # Stream the response
        response_placeholder=st.empty()
        full_response=""

        try:
            for message_chunk,metadata in chatbot.stream(
                    {'messages':[HumanMessage(content = user_input)]},
                    config = config,
                    stream_mode = 'messages',
            ):
                if hasattr(message_chunk,'content') and message_chunk.content:
                    full_response+=message_chunk.content
                    response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)

            # Add assistant message to history
            st.session_state['message_history'].append({
                'role':'assistant',
                'content':full_response
            })

        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            st.info("Please try again or start a new chat.")

# Add helpful prompts if chat is empty
if len(st.session_state['message_history']) == 0:
    st.markdown('---')
    st.subheader('💡 Try asking:')

    col1,col2,col3=st.columns(3)

    with col1:
        st.markdown("""
        **🎓 Education**
        - What degrees do you have?
        - Where did you study?
        - What's your educational background?
        - Any relevant coursework?
        """)

    with col2:
        st.markdown("""
        **💼 Experience**
        - Tell me about your work history
        - What was your last role?
        - What companies have you worked for?
        - Describe your responsibilities
        """)

    with col3:
        st.markdown("""
        **🛠️ Skills & Projects**
        - What technical skills do you have?
        - Tell me about your projects
        - What programming languages?
        - Any certifications?
        """)