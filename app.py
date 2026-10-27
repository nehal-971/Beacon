import streamlit as st
from openai import OpenAI

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="BEACON", page_icon="✨", layout="wide")

# --- INITIALIZE AI CLIENT ---
# ⚠️ REPLACE THE STRING BELOW WITH YOUR ACTUAL GROQ API KEY (keep the quotes)
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key="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" 
)

# --- MOCK DATA (The Student's Life) ---
tasks = [
    {"title": "Submit Electronics Assignment", "deadline": "Friday, 11:59 PM", "type": "Academic"},
    {"title": "Pay Hostel Fee (₹5,000)", "deadline": "Saturday, 12:00 PM", "type": "Financial"}
]

# --- UI LAYOUT ---
st.title("✨ BEACON — Your AI Student Copilot")
st.markdown("**Human-AI Collaboration for B.Tech Life**")
st.divider()

# Create 3 columns for the dashboard
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📬 Inbox")
    st.info("**From: University Admin**\n\n**Subject:** URGENT: Exam Reschedule\n\n**Message:** The Data Structures exam has been moved up to Thursday morning.")
    
with col2:
    st.markdown("### 📅 Today's Calendar")
    st.write("🕒 10:00 AM - Data Structures Class")
    st.write("🕒 02:00 PM - Hackathon Team Meeting")
    st.write("🕒 05:00 PM - Gym")

with col3:
    st.markdown("### ⚠️ Critical Deadlines")
    for task in tasks:
        if task["type"] == "Financial":
            st.error(f"**{task['title']}**\nDue: {task['deadline']}")
        else:
            st.warning(f"**{task['title']}**\nDue: {task['deadline']}")

st.divider()

# --- THE HUMAN-AI COLLABORATION ENGINE ---
st.markdown("### 🤖 BEACON Conflict Resolver")
st.write("A new email arrived that affects your schedule. Let's see how the AI handles it.")

# Setup the prompt for Groq
prompt = f"""
You are BEACON, an AI life assistant for a B.Tech student.
Here are the student's current tasks: {tasks}
A new email just arrived: "The Data Structures exam has been moved up to Thursday morning."

1. Analyze the conflict between the new exam date, the assignment deadline, and the hostel fee.
2. Propose a strict, prioritized schedule for the next 48 hours.
3. Explicitly tell the student what they need to sacrifice (e.g., skip the Hackathon meeting or Gym) to survive this week.
Keep your response under 150 words. Be direct.
"""

if st.button("🚨 Run AI Conflict Analysis", type="primary"):
    with st.spinner("BEACON is simulating your schedule..."):
        try:
            # Call Groq API
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b", 
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            ai_output = response.choices[0].message.content
            st.success("### AI Recommendation:")
            st.write(ai_output)
            
            # Store the AI output in the session so we can use it for the next step
            st.session_state['ai_plan'] = ai_output
            
        except Exception as e:
            st.error(f"Error connecting to AI: {e}\n\n*Tip: If it's a 404 error, try changing the model in the code to 'openai/gpt-oss-120b'*")

# --- THE CORRECTION LOOP (The Hackathon Winning Feature) ---
if 'ai_plan' in st.session_state:
    st.markdown("#### 👤 Human-in-the-Loop Decision")
    st.write("The AI proposed a plan. But do you agree with it?")
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("✅ Accept Plan & Reschedule"):
            st.balloons()
            st.success("Schedule updated. AI learning from your preferences...")
            
    with col_btn2:
        if st.button("❌ Reject: I must pay the hostel fee first"):
            with st.spinner("AI is re-calculating based on your constraint..."):
                # Create a new prompt that FORCES the AI to respect the human's choice
                correction_prompt = f"""
                The AI previously proposed this plan: {st.session_state['ai_plan']}
                However, the human REJECTED it and said: "I must pay the hostel fee first, regardless of the exam."
                Re-plan the schedule immediately to respect the human's financial constraint. Acknowledge the human's choice.
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
        if st.button("🔄 Reset Demo"):
            # This clears the memory so you can demo it again for the next judge!
            if 'ai_plan' in st.session_state:
                del st.session_state['ai_plan']
            st.rerun()