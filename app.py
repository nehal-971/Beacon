import streamlit as st
from openai import OpenAI

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="BEACON", page_icon="✨", layout="wide")

# --- CUSTOM BACKGROUND MAGIC (IMAGE) ---
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://img.freepik.com/free-vector/dark-gradient-background-with-copy-space_53876-99548.jpg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 10px;
    padding: 10px;
}
/* Styling the sidebar to match the dark theme */
[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.95);
    border-right: 1px solid rgba(255,255,255,0.1);
}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# --- INITIALIZE AI CLIENT ---
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=st.secrets["GROQ_API_KEY"] 
)

# --- SESSION STATE FOR DYNAMIC DATA ---
# This keeps the user's tasks in memory even when they click buttons
if 'tasks' not in st.session_state:
    st.session_state.tasks = [
        {"title": "Submit Electronics Assignment", "deadline": "Friday, 11:59 PM", "type": "Academic"},
        {"title": "Pay Hostel Fee (₹5,000)", "deadline": "Saturday, 12:00 PM", "type": "Financial"}
    ]

if 'new_email' not in st.session_state:
    st.session_state.new_email = "The Data Structures exam has been moved up to Thursday morning."

# --- SIDEBAR: USER INPUT ---
with st.sidebar:
    st.header("⚙️ Setup Your Schedule")
    
    # 1. Input for the triggering email
    st.subheader("📧 Incoming Alert")
    email_input = st.text_area("What just happened?", value=st.session_state.new_email)
    
    # 2. Priority Mode
    st.subheader("🧠 Priority Mode")
    priority_mode = st.radio(
        "Who decides what's most important?",
        ("Let AI Decide (Auto-Prioritize)", "I will decide (Human Override)")
    )
    
    # 3. Add Tasks
    st.subheader("📝 Add a Task")
    with st.form("task_form", clear_on_submit=True):
        task_title = st.text_input("Task Name (e.g., Math Exam)")
        task_deadline = st.text_input("Deadline (e.g., Thursday 9 AM)")
        task_type = st.selectbox("Type", ["Academic", "Financial", "Personal"])
        submit_task = st.form_submit_button("➕ Add Task")
        
        if submit_task and task_title and task_deadline:
            st.session_state.tasks.append({
                "title": task_title,
                "deadline": task_deadline,
                "type": task_type
            })
            st.success("Task Added!")

    # Button to reset to default
    if st.button("🔄 Reset to Default Demo"):
        st.session_state.tasks = [
            {"title": "Submit Electronics Assignment", "deadline": "Friday, 11:59 PM", "type": "Academic"},
            {"title": "Pay Hostel Fee (₹5,000)", "deadline": "Saturday, 12:00 PM", "type": "Financial"}
        ]
        st.session_state.new_email = "The Data Structures exam has been moved up to Thursday morning."
        if 'ai_plan' in st.session_state:
            del st.session_state['ai_plan']
        st.rerun()


# --- MAIN UI LAYOUT ---
st.title("✨ BEACON — Your AI Student Copilot")
st.markdown("**Human-AI Collaboration for B.Tech Life**")
st.divider()

# Create 3 columns for the dashboard
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📬 Inbox")
    st.info(f"**From: University Admin**\n\n**Subject:** URGENT\n\n**Message:** {email_input}")
    
with col2:
    st.markdown("### 📅 Today's Calendar")
    st.write("🕒 10:00 AM - Data Structures Class")
    st.write("🕒 02:00 PM - Hackathon Team Meeting")
    st.write("🕒 05:00 PM - Gym")

with col3:
    st.markdown("### ⚠️ Critical Deadlines")
    # Dynamically display the tasks from Session State
    for task in st.session_state.tasks:
        if task["type"] == "Financial":
            st.error(f"**{task['title']}**\nDue: {task['deadline']}")
        elif task["type"] == "Academic":
            st.warning(f"**{task['title']}**\nDue: {task['deadline']}")
        else:
            st.info(f"**{task['title']}**\nDue: {task['deadline']}")

st.divider()

# --- THE HUMAN-AI COLLABORATION ENGINE ---
st.markdown("### 🤖 BEACON Conflict Resolver")
st.write(f"A new alert arrived. **Mode:** {priority_mode}. Let's see how BEACON handles it.")

# Dynamic Prompt based on User Inputs
prompt = f"""
You are BEACON, an AI life assistant for a B.Tech student.
Here are the student's current tasks: {st.session_state.tasks}
New Alert: "{email_input}"

CRITICAL INSTRUCTION - PRIORITY MODE: {priority_mode}
If Mode is 'Let AI Decide': Analyze the urgency and impact of all tasks and decide the best priority for the student.
If Mode is 'I will decide': The student is insisting on managing their own priorities. You must respect their autonomy, ask them what they want to prioritize, or strictly follow the order they listed in their tasks.

1. Analyze the conflict between the new alert and the current tasks.
2. Propose a strict, prioritized schedule for the next 48 hours based on the Priority Mode.
3. Explicitly tell the student what they need to sacrifice to survive this week.
Keep your response under 150 words. Be direct.
"""

if st.button("🚨 Run AI Conflict Analysis", type="primary"):
    with st.spinner("BEACON is simulating your schedule..."):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b", 
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            ai_output = response.choices[0].message.content
            st.success("### AI Recommendation:")
            st.write(ai_output)
            
            st.session_state['ai_plan'] = ai_output
            
        except Exception as e:
            st.error(f"Error connecting to AI: {e}")

# --- THE CORRECTION LOOP ---
if 'ai_plan' in st.session_state:
    st.markdown("#### 👤 Human-in-the-Loop Decision")
    st.write("The AI proposed a plan. But do you agree with it?")
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("✅ Accept Plan & Reschedule"):
            st.balloons()
            st.success("Schedule updated. AI learning from your preferences...")
            
    with col_btn2:
        if st.button("❌ Reject: I must prioritize my Financial task"):
            with st.spinner("AI is re-calculating based on your constraint..."):
                correction_prompt = f"""
                The AI previously proposed this plan: {st.session_state['ai_plan']}
                However, the human REJECTED it and said: "I must prioritize my Financial task (or specific task) first, regardless of the alert."
                Re-plan the schedule immediately to respect the human's constraint. Acknowledge the human's choice and show how the plan adapts.
                """
                
                try:
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[{"role": "user", "content": correction_prompt}],
                        temperature=0.7
                    )
                    st.warning("### AI Adjusted Plan (Based on Human Override):")
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error: {e}")
                    
    with col_btn3:
        if st.button("🔄 Clear AI Output"):
            if 'ai_plan' in st.session_state:
                del st.session_state['ai_plan']
            st.rerun()