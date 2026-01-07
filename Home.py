import streamlit as st
import time
from datetime import datetime
import pandas as pd

# ---------------- CONFIG ----------------
EDGE_BUZZER_TIME = 3
ESCALATION_DELAY = 5

NORMAL = "NORMAL"
EDGE_ALERT = "EDGE_ALERT"
ESCALATION = "ESCALATION"
CONTROL_ALERT = "CONTROL_ALERT"
ACKNOWLEDGED = "ACKNOWLEDGED"

# ---------------- CSS ----------------
st.markdown("""
<style>
.centered-img {
    display: flex;
    justify-content: center;
}
audio { display: none; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION INIT ----------------
if "state" not in st.session_state:
    st.session_state.state = NORMAL
    st.session_state.t0 = None
    st.session_state.logs = []
    st.session_state.selected_label = None
    st.session_state.event_time = None
    st.session_state.process_request = False
if "control_audio_played" not in st.session_state:
    st.session_state.control_audio_played = False

if "distress_time" not in st.session_state:
    st.session_state.distress_time = None

if "edge_buzzer_played" not in st.session_state:
    st.session_state.edge_buzzer_played = False

if "selected_image" not in st.session_state:
    st.session_state.selected_image = None
# ---------------- PAGE ----------------
st.set_page_config("MS KAVACH Dashboard", layout="wide")
st.title("🛡️ MS KAVACH – Mānavī Suraksha Kavach Prototype Simulation Dashboard")
st.caption("Complements physical prototype with Alert escalation")

with st.sidebar:
    st.header("System Controls")

    if st.button("🔄 Reset System"):
        st.session_state.state = NORMAL
        st.session_state.t0 = None
        st.session_state.selected_label = None
        st.session_state.event_time = None
        st.session_state.process_request = False
        st.session_state.logs = []
        st.session_state.edge_buzzer_played = False
        st.success("System reset successfully")
        time.sleep(0.5)
        st.rerun()

# ---------------- TABS ----------------
tabs = st.tabs([
    "Overview",
    "Workflow",
    "Live Simulation",
    "Control Room Demonstration",
    "Alert Logs",
    "Future Deployment"
])

# ---------------- TAB 1: OVERVIEW ----------------
with tabs[0]:
    st.header("📌 Project Overview")
    st.write("""
    MS KAVACH is a camera-mounted, IoT-enabled women safety module designed to deliver instant local deterrence and rapid escalation during distress situations.
This dashboard demonstrates the end-to-end operational workflow of the system under simulated conditions, closely mirroring real-world deployment behavior.""")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(
            "assets/overview.png",
            caption="Conceptual visualization of the MS KAVACH IoT safety module",
            width=650
        )
    st.write("""
    **Privacy & Ethical Use Notice**  
    Images captured during **alert situations** are accessed solely by
    **authorized control-room personnel** for verification and response.  
    Unauthorized access or misuse of image data is strictly prohibited.
    """)
# ---------------- TAB 2: WORKFLOW ----------------
with tabs[1]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(
            "assets/workflow.png",
            caption="The Workflow of MS Kavach",
            width=650
        )
    st.markdown("""
        **Key Design Principles**
        - Privacy-first activation (event-only imaging)
        - Human-verified escalation
        - Zero-latency local deterrence
        - Modular, low-cost, scalable deployment
    """)

# ---------------- TAB 3: LIVE SIMULATION ----------------
with tabs[2]:
    st.subheader("🎥 Live Simulation")

    images = [
        ("NORMAL", "assets/normal1.jpg"),
        ("NORMAL", "assets/normal2.jpg"),
        ("DISTRESS", "assets/distress1.jpg"),
        ("DISTRESS", "assets/distress2.jpg"),
        ("DISTRESS", "assets/distress3.jpg")
    ]

    cols = st.columns(5)

    for i, (label, img) in enumerate(images):
        with cols[i]:
            st.image(img, width=200)
            if st.button("Analyze Frame", key=f"img_{i}"):
                st.session_state.selected_label = label
                st.session_state.selected_image = img
                st.session_state.process_request = True
               
                if label == "DISTRESS":
                    st.session_state.edge_buzzer_played = False
                    st.session_state.control_audio_played = False
                    st.session_state.distress_time = time.time()

                else:  # NORMAL clicked
                    st.session_state.state = NORMAL
                    st.session_state.selected_image = None

    col1, col2, col3 = st.columns(3)

    # INPUT
    with col1:
        st.subheader("📷 Camera Input")
        if st.session_state.selected_label:
            st.write("Image Received")

    # PROCESS
    with col2:
        st.subheader("⚙️ Processing")
        if st.session_state.process_request:
            with st.spinner("Processing the image..."):
                time.sleep(2)

            st.session_state.event_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            if st.session_state.selected_label == "DISTRESS":
                st.session_state.state = EDGE_ALERT
                st.session_state.t0 = time.time()
                st.session_state.distress_time = time.time()
                st.session_state.logs.append({
                    "Time": st.session_state.event_time,
                    "Type": "Distress",
                    "Status": "Alert Escalated"
                })
            else:
                st.session_state.logs.append({
                    "Time": st.session_state.event_time,
                    "Type": "Normal",
                    "Status": "No Alert"
                })

            st.success("Processing Completed")
            st.session_state.process_request = False

    # OUTPUT
    with col3:
        st.subheader("🚨 System Output")
        if st.session_state.event_time:
            if st.session_state.selected_label == "NORMAL":
                st.write("This is a normal situation.")
                st.success("No Alert Generated")
                st.write("🔔 Buzzer: OFF")
                st.write("📡 Alert Transmission: NOT SENT")
            else:
                st.write("Distress situation detected!")
                st.error("ALERT TRIGGERED")
                st.write("🔔 Deterrence Buzzer Activated")
                st.write("📡 Alert Sent to Control Room")
                if not st.session_state.edge_buzzer_played:
                    st.audio("assets/buzzer.wav", autoplay=True)
                    st.session_state.edge_buzzer_played = True
               
        else:
            st.info("Waiting for event trigger...")
# ---------------- TAB 4: CONTROL ROOM DEMONSTRATION ----------------  
with tabs[3]:
    st.header("🏢 Control Room")

    if st.session_state.state == CONTROL_ALERT:


        st.markdown("""
        <div style="
            background-color:#ff0000;
            padding:20px;
            border-radius:10px;
            text-align:center;
            animation: blink 1s infinite;
        ">
            <h2 style="color:white;">🚨 CONTROL ROOM ALERT 🚨</h2>       
            <p style="color:white;">Emergency signal received from MS KAVACH device</p>
        </div>

        <style>
        @keyframes blink {
            0% {opacity:1;}
            50% {opacity:0.4;}
            100% {opacity:1;}
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 🔔 Play control room audio once, after delay
        if (
            st.session_state.distress_time
            and not st.session_state.control_audio_played
            and time.time() - st.session_state.distress_time >= 5
        ):
            st.audio("assets/control_room_alert.wav", autoplay=True)
            st.session_state.control_audio_played = True

        st.subheader("📷 Image & Location Verification")

        col_img, col_loc = st.columns([1.2, 1])

        with col_img:
            if st.session_state.selected_image:
                st.image(
                    st.session_state.selected_image,
                    caption="Image received from MS KAVACH device",
                    width=360
                    )

        with col_loc:
            st.markdown("### 📍 Location Details")
            st.markdown("[🌍 Open in Google Maps](https://maps.google.com/?q=17.7430,83.3194)")
            st.write("Location link: https://maps.google.com/?q=17.7430,83.3194")
            st.write("MVP Colony Junction, Visakhapatnam")
            st.write("Coordinates: 17.7430, 83.3194")

        st.button("📞 Notify Emergency Response Units", disabled=True)
        st.caption("Simulation only • In deployment, this triggers secured alert channels")

        st.subheader("🚨 Response Actions")
        col_flow, col_escalate = st.columns([1.4, 1])
        with col_flow:
            st.markdown("""
            **Workflow:**
            
            1️⃣ Alert is received from an MS KAVACH device and the operator verifies the incoming image  
            2️⃣ If the image confirms distress, response protocols are initiated  
            3️⃣ Camera location is identified  
            4️⃣ Alert is escalated to nearest response units  
            """)
        with col_escalate:
            st.markdown("""
            **Escalation Targets:**
            
            - 🚓 Local Police  
            - 👮 SHE Teams / Women Safety Units  
            - 🚨 Emergency Patrol & Rapid Response Units  
            """)

        st.markdown("Escalation pathways are configurable based on jurisdiction and deployment area.")
        
        st.warning("All communication actions and and the location shown are simulated for academic demonstration purposes only.")

    else:
        st.success("🟢 Monitoring active")
        st.write("""
        All connected **MS Kavach** devices are functioning normally.

        - No active emergency alerts  
        - No distress signals detected  
        - Control room is in passive monitoring mode  

        The system will notify the operators when a distress
        situation is detected in the field.
        """)


# ---------------- TAB 5: ALERT LOGS ----------------
with tabs[4]:
    st.header("📋 Alert Log")

    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)

        def highlight_distress(row):
            if row["Type"] == "Distress":
                return ["background-color: #8B0000; color: white"] * len(row)
            else:
                return [""] * len(row)

        styled_df = df.style.apply(highlight_distress, axis=1)

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No alerts recorded yet.")

# ---------------- TAB 6: FUTURE ----------------
with tabs[5]:
    st.header("🚀 Future Deployment & Scalability")

    st.write("""
    - Live ESP32-CAM feeds replace simulated images
    - Physical on-device deterrence modules replace audio playback
    - Authorized telecom gateways enable secure alert escalation
    - Centralized command dashboard monitors multiple MS KAVACH units
    - Jurisdiction-aware routing for faster response times
    """)

    st.info("⚠️ Immediate local deterrence will always remain autonomous and will never be delayed by network latency or backend processing.")

# ---------------- STATE MACHINE ----------------
now = time.time()

if st.session_state.state == EDGE_ALERT:
    if now - st.session_state.t0 >= EDGE_BUZZER_TIME:
        st.session_state.state = ESCALATION
        st.session_state.t0 = now

elif st.session_state.state == ESCALATION:
    if now - st.session_state.t0 >= ESCALATION_DELAY:
        st.session_state.state = CONTROL_ALERT
        st.session_state.t0 = now


if st.session_state.state in [EDGE_ALERT, ESCALATION]:
    time.sleep(0.5)
    st.rerun()
# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("MS KAVACH • End-to-End Women Safety System Simulation")

