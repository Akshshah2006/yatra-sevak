import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
from sklearn.model_selection import train_test_split
import io
import humanize  # Added for nicer numbers (e.g., 85,000 instead of 85000)

# Temple Data: Coords & Base Daily Footfall (from Gujarat Tourism/Wiki)
TEMPLE_DATA = {
    'Somnath': {'lat': 20.888, 'lng': 70.401, 'base_footfall': 50000},  # ~18M annual 
    'Dwarka': {'lat': 22.238, 'lng': 68.968, 'base_footfall': 25000},    # ~9M annual 
    'Ambaji': {'lat': 24.333, 'lng': 72.850, 'base_footfall': 25000},    # ~9M annual 
    'Pavagadh': {'lat': 22.461, 'lng': 73.512, 'base_footfall': 6000}    # ~2.2M annual 
}
# Hardcoded Multilingual Support (Expanded)
# Fix: Define English first, then copy for others
english_trans = {
    'title': '🛕 Yatra Sevak: Multi-Temple Management (4 Sites)',
    'select_temple': 'Select Temple',
    'home_info': 'Home & Temple Info (#6)',
    'join_queue': 'Smart Queue & Ticketing (#2)',
    'sos_nav': 'Emergency & Safety (#4)',
    'surveillance': 'IoT & Surveillance (#3)',
    'traffic': 'Traffic & Mobility (#5)',
    'accessibility': 'Accessibility Features (#7)',
    'prediction': 'AI Crowd Prediction (#1)',
    'pilgrim_app': 'Pilgrim View',
    'authority_dashboard': 'Authority Dashboard',
    'language': 'Language / ભાષા / भाषा',
    'view_as': 'View As',
    'temple_info_wait': 'Engagement: Timings, Routes, Facilities (#6)',
    'current_weather': 'Weather (for #1): 28°C (Sim). Routes Below.',
    'virtual_darshan': 'Virtual Queue Management',
    'elderly_priority': 'Priority for Elderly/Disabled (#7)',
    'join_btn': 'Get Digital Darshan Pass',
    'simulate_turn': 'Simulate Your Turn',
    'token_issued': 'Pass Issued! Wait: {} mins. Slot: {}. Real-time Update.',
    'your_turn': 'Your Turn! Proceed.',
    'emergency_sos': 'SOS Button (#4)',
    'press_sos': '🚨 Press SOS',
    'sos_sent': 'SOS Sent! First Responders Alerted. Drone Dispatched.',
    'voice_guide': 'Voice-Guided Navigation (#7)',
    'audio_sim': "Voice: 'Turn left 50m to priority entry.'",
    'surge_alert': 'Surge Forecast: Limiting Slots (#1 → #2)',
    'scan_now': 'Scan CCTV/Sensors/Drones',
    'crowded': 'Crowded (High Density)',
    'safe': 'Safe',
    'panic_detected': '🚨 Panic at {}! Triggered Alert (#3 → #4). Notify App (#6).',
    'active_queues': 'Queues & Alerts (#2, #4)',
    'no_alerts': 'No Alerts.',
    'dispatch': 'Dispatch Responders',
    'dispatched': 'Dispatched! (Police/Medical).',
    'parking_mobility': 'Parking Guidance & Shuttle (#5)',
    'empty_spots': 'Empty Spots: {}/10. Police-Integrated Flow.',
    'footer': 'Scalable to 4 Temples: Ambaji, Dwarka, Pavagadh, Somnath. All 7 Features Integrated. ❤️',
    'predicted_crowd': 'Predicted Footfall',
    'temple_timings': 'Timings: 5AM-9PM (#6)',
    'facilities': 'Facilities: Restrooms, Food, Medical (#6)',
    'emergency_contacts': 'Contacts: Police 100, Medical 108 (#6)',
    'routes': 'Routes: Gate → Hall → Exit (#6)',
    'medical_map': 'Medical Mapping (#4)',
    'barricades': 'Smart Barricades (#4)',
    'drone_dispatch': 'Drone Dispatched w/ Camera/Speaker/Kit (#4)',
    'dynamic_slots': 'Dynamic Slots: Free if Low Demand (#2)',
    'voice_nav': 'Voice Mode for Visually Impaired (#7)',
    'shuttle_schedule': 'Shuttle Coordination (#5)',
    'traffic_flow': 'Dynamic Traffic (#5)',
    'live_log': 'Live Event Log',
    'cctv_feed': 'Live CCTV Feed (#3)',
    'drone_view': 'Drone Patrol View (#3/#4)',
    'current_footfall': 'Live Footfall Counter (#1)',
    'kiosk_mode': 'Kiosk Mode (For Temple Kiosks - #2)',
    'volunteer_coord': 'Volunteer Coordination (#7)',
    'smart_wheelchair': 'Smart Wheelchair Tracker (#7)',
    'abnormal_movement': 'Abnormal Movement Detected (#4)',
    'sudden_rush': 'Sudden Rush Detected (#4)',
    'police_alert': 'Police Alert Sent (#4)',
    'medical_alert': 'Medical Alert Sent (#4)',
    'iot_parking': 'IoT Parking Detection (#5)',
    'shuttle_police': 'Shuttle with Police Coordination (#5)',
    'wait_times': 'Real-Time Wait Times (#6)',
    'temple_info': 'Temple Timings & Info (#6)',
    'emergency_sos_button': 'Emergency SOS Button (#6)',
    'accessibility_support': 'Accessibility Support (#6)',
    'priority_entry': 'Priority Entry Routes (#7)',
    'smart_wheelchair_retrieval': 'Smart Wheelchair IoT-Tracked Retrieval (#7)',
    'volunteer_assist': 'Volunteer Assist Coordination (#7)'
}

# Session State (lists for persistence)
if 'queue_data' not in st.session_state:
    st.session_state.queue_data = []
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'surge_active' not in st.session_state:
    st.session_state.surge_active = False
if 'crowd_alert_sent' not in st.session_state:
    st.session_state.crowd_alert_sent = False
if 'drone_dispatched' not in st.session_state:
    st.session_state.drone_dispatched = False
if 'live_footfall' not in st.session_state:
    st.session_state.live_footfall = 0
if 'density' not in st.session_state:
    st.session_state.density = 0.5
if 'log_entries' not in st.session_state:
    st.session_state.log_entries = []
if 'wheelchair_locations' not in st.session_state:
    st.session_state.wheelchair_locations = {}  # For #7
if 'volunteers' not in st.session_state:
    st.session_state.volunteers = []  # For #7

def add_log(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    st.session_state.log_entries.append(f"[{timestamp}] {msg}")
    if len(st.session_state.log_entries) > 10: st.session_state.log_entries.pop(0)

# Surveillance (#3) - Run on load for defaults
alert, density = simulate_monitoring(temple)  # Fixed: Call here for defaults

# Model
@st.cache_data
def load_and_train_model(base_footfall):
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', end='2026-01-01', freq='D')
    n = len(dates)
    festivals = ['2025-01-14', '2025-02-26', '2025-10-20', '2025-11-15', '2025-09-29', '2025-10-07']
    is_festival = [1 if d.strftime('%Y-%m-%d') in festivals else 0 for d in dates]
    temp = np.random.normal(28, 5, n).clip(15, 40)
    is_holiday = [(d.weekday() >= 5) or isf for d, isf in zip(dates, is_festival)]
    festival_boost = np.array(is_festival) * (base_footfall * 2)
    holiday_boost = np.array(is_holiday) * (base_footfall * 0.2)
    weather_factor = (30 - temp) / 10
    noise = np.random.normal(0, base_footfall * 0.1, n)
    footfall = (base_footfall + festival_boost + holiday_boost + weather_factor * base_footfall * 0.1 + noise).clip(0, base_footfall * 3)
    
    df = pd.DataFrame({'date': dates, 'footfall': footfall, 'temperature': temp, 'is_festival': is_festival, 'is_holiday': is_holiday})
    df['month'] = df['date'].dt.month
    df['dayofweek'] = df['date'].dt.dayofweek
    features = ['temperature', 'is_festival', 'is_holiday', 'month', 'dayofweek']
    X = df[features]
    y = df['footfall']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model, features, df

def predict_crowd(temple, days_ahead=7):
    data = TEMPLE_DATA[temple]
    model, features, _ = load_and_train_model(data['base_footfall'])
    try:
        today = date(2025, 10, 4)
        future_dates = pd.date_range(start=today, periods=days_ahead, freq='D')
        future_n = len(future_dates)
        future_temp = np.random.normal(28, 5, future_n).clip(15, 40)
        future_fest = [1 if d.strftime('%Y-%m-%d') in ['2025-10-20', '2025-11-01', '2025-11-15'] else 0 for d in future_dates]
        future_hol = [(d.weekday() >= 5) or ff for d, ff in zip(future_dates, future_fest)]
        future_df = pd.DataFrame({'date': future_dates, 'temperature': future_temp, 'is_festival': future_fest, 'is_holiday': future_hol})
        future_df['month'] = future_df['date'].dt.month
        future_df['dayofweek'] = future_df['date'].dt.dayofweek
        X_future = future_df[features]
        predictions = model.predict(X_future)
        future_df['predicted_footfall'] = predictions
        return future_df
    except Exception as e:
        st.error(f"Prediction error: {e}")
        return pd.DataFrame()

# Queue (Scaled by Temple)
def join_queue(temple, user_id, priority=False, lang='English'):
    now = datetime.now()
    pred_df = predict_crowd(temple, 1)
    base = TEMPLE_DATA[temple]['base_footfall']
    surge_threshold = base * 2  # Scale surge per temple
    surge_penalty = 60 if (not pred_df.empty and pred_df['predicted_footfall'].iloc[0] > surge_threshold) else 0
    base_wait = np.random.randint(30, 120)
    est_wait = base_wait + (0 if priority else 15) - surge_penalty
    slot = (now + timedelta(minutes=est_wait)).strftime('%H:%M')
    slot_type = 'Free' if est_wait < 45 else 'Paid'
    entry = {'temple': temple, 'user_id': user_id, 'join_time': now, 'priority': priority, 'lang': lang, 'slot': slot, 'status': 'Waiting', 'est_wait': est_wait, 'slot_type': slot_type}
    st.session_state.queue_data.append(entry)
    add_log("A mobile app/kiosk system lets devotees book digital tokens/darshan slots.")
    add_log("Shows real-time waiting time and sends alerts when it’s their turn.")
    return TRANSLATIONS[lang]['token_issued'].format(est_wait, slot) + f" ({slot_type} - Dynamic Slot)"

# Emergency & Safety Module (#4)
def trigger_emergency(temple, location):
    add_log("Emergency & Safety Module")
    add_log("Panic detection via AI-enabled CCTV (e.g., sudden rush or abnormal movement).")
    add_log("Alerts local police & medical teams instantly.")
    st.session_state.dispatched_police = True
    st.session_state.dispatched_medical = True
    add_log("Real-time panic detection")
    add_log("Smart barricade systems")
    add_log("AI-enabled first responder alerts")
    add_log("Medical assistance mapping")

# Traffic & Parking System (#5)
def get_parking_status(temple):
    base = TEMPLE_DATA[temple]['base_footfall']
    empty = np.random.randint(1, 10)
    add_log("Traffic & Parking System")
    add_log("Smart parking guidance (IoT sensors detect empty spots, app directs cars).")
    add_log(f"Empty spots: {empty}/10")
    return empty

def get_shuttle_status(temple):
    status = np.random.choice(['On Time', 'Delayed 5min', 'Police Coordinated'])
    add_log("Shuttle/bus coordination integrated with police for smooth road management.")
    add_log(f"Status: {status}")
    return status

# Pilgrim Engagement Platforms (#6)
def get_engagement_info(temple):
    timings = "5AM-9PM"
    routes = "Gate → Hall → Exit"
    facilities = "Restrooms, Food, Medical"
    contacts = "Police 100, Medical 108"
    add_log("Pilgrim Engagement Platforms")
    add_log("Multilingual apps providing information on wait times, temple timings, routes, facilities, and emergency contacts.")
    add_log("Shows wait times, temple info, routes, facilities, SOS button, accessibility support.")
    return timings, routes, facilities, contacts

# Accessibility Features (#7)
def get_accessibility_support(temple, priority=False):
    add_log("Accessibility Features")
    add_log("Navigation assistance and priority services for elderly and differently-abled pilgrims.")
    if priority:
        add_log("Special priority entry routes highlighted in app for elderly/differently-abled.")
        return "Priority entry routes active"
    return "Standard navigation support"

def track_wheelchair(temple, user_id):
    location = np.random.choice(['Near Gate', 'Hall Area', 'Parking'])
    st.session_state.wheelchair_locations[user_id] = location
    add_log("Smart wheelchairs (IoT-tracked for easy retrieval).")
    add_log(f"Wheelchair {user_id} at {location}")
    return location

def coordinate_volunteer(temple, need):
    volunteer = np.random.choice(['Volunteer A', 'Volunteer B'])
    st.session_state.volunteers.append(volunteer)
    add_log("Volunteer coordination via app to assist those in need.")
    add_log(f"{volunteer} assigned for {need}")
    return volunteer

# Map (For all features)
def create_map(temple, feature='parking'):
    data = TEMPLE_DATA[temple]
    m = folium.Map(location=[data['lat'], data['lng']], zoom_start=15)
    spots = [(data['lat'] + 0.001, data['lng'] + 0.001), (data['lat'] - 0.001, data['lng'] - 0.001)]
    for spot in spots:
        folium.Marker(spot, popup="Empty Parking", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker([data['lat'], data['lng']], popup=f"{temple} Temple", icon=folium.Icon(color='red')).add_to(m)
    if feature == 'medical':
        folium.Marker([data['lat'] - 0.002, data['lng'] + 0.002], popup="Medical Center", icon=folium.Icon(color='orange')).add_to(m)
    if feature == 'drone' and st.session_state.drone_dispatched:
        folium.Marker([data['lat'] + 0.0015, data['lng'] - 0.0005], popup="Drone w/ Kit", icon=folium.Icon(color='blue')).add_to(m)
    if feature == 'wheelchair':
        for user, loc in st.session_state.wheelchair_locations.items():
            folium.Marker([data['lat'] + np.random.uniform(-0.001, 0.001), data['lng'] + np.random.uniform(-0.001, 0.001)], popup=f"Smart Wheelchair {user} Retrieval (#7)", icon=folium.Icon(color='purple')).add_to(m)
    if feature == 'priority':
        folium.PolyLine([[data['lat'], data['lng']], [data['lat'] - 0.001, data['lng'] + 0.001]], color="gold", weight=3, popup="Priority Entry Routes for Elderly/Differently-Abled (#7)").add_to(m)
    return m

# UI
st.set_page_config(page_title="Yatra Sevak - Winning Prototype", layout="wide")
st.markdown("""
<style>
.main {background-color: #e6f3ff;}
.stTabs [data-baseweb="tab-list"] {gap: 0.5rem; font-size: 1.1rem;}
.stTab > div > div {padding: 1.5rem; border-radius: 10px;}
.metric {background-color: #4CAF50; color: white;}
</style>
""", unsafe_allow_html=True)

lang = st.sidebar.selectbox(TRANSLATIONS['English']['language'], ['English', 'Gujarati', 'Hindi'])
t = TRANSLATIONS[lang]
temple = st.sidebar.selectbox(t['select_temple'], list(TEMPLE_DATA.keys()))
role = st.sidebar.selectbox(t['view_as'], [t['pilgrim_app'], t['authority_dashboard']])
live_mode = st.sidebar.checkbox(t['live_mode'], key=f"live_checkbox_{temple}")
st.sidebar.title(f"{t['title']} - {temple}")

# Sidebar Sims
st.sidebar.header("Demo Integrations")
if st.sidebar.button('Sim Surge: #1 → #2 (Limit Slots)'):
    st.session_state.surge_active = True
    add_log("Surge sim activated - Queues capped")
    st.rerun()
if st.sidebar.button('Sim Crowded: #3 → #4 → #6 (Alert App)'):
    simulate_monitoring(temple)
    st.rerun()
if st.sidebar.button('Sim Wheelchair Track (#7)'):
    track_wheelchair(temple, np.random.randint(1, 10))
    st.rerun()
if st.sidebar.button('Sim Volunteer Coord (#7)'):
    coordinate_volunteer(temple, np.random.choice(['elderly assist', 'differently-abled support']))
    st.rerun()
if st.sidebar.button('Toggle Kiosk Mode (#2)'):
    st.session_state.kiosk_mode = not st.session_state.kiosk_mode
    add_log("Kiosk mode toggled for virtual queue management via mobile apps and kiosks (#2)")
    st.rerun()

st.title(f"{t['title']} - {temple}")

# Live Footfall Counter (#1)
pred_df = predict_crowd(temple, 1)
st.session_state.live_footfall += np.random.randint(50, 200)
st.metric(t['current_footfall'], f"{st.session_state.live_footfall:,}", delta=f"+{np.random.randint(50, 200)}/min", help="Live from Sensors")

# Kiosk Mode Sim (#2)
if st.session_state.kiosk_mode:
    st.info("Kiosk Mode Active: A mobile app/kiosk system lets devotees book digital tokens/darshan slots (#2)")

if role == t['pilgrim_app']:
    tabs = st.tabs([t['home_info'], t['join_queue'], t['sos_nav'], t['surveillance'], t['traffic'], t['accessibility'], t['medical_map']])
    
    with tabs[0]:  # #6 Full
        st.header(f"{t['temple_info_wait']} - {temple}")
        pred_df = predict_crowd(temple, 3)
        if not pred_df.empty:
            st.dataframe(pred_df[['date', 'predicted_footfall']].rename(columns={'predicted_footfall': t['predicted_crowd']}))
        col1, col2, col3 = st.columns(3)
        with col1: st.success(f"🕐 {t['temple_timings']}")
        with col2: st.info(f"🏥 {t['facilities']}")
        with col3: st.error(f"📞 {t['emergency_contacts']}")
        st.info(f"🗺️ {t['routes']}")
        st.info(t['current_weather'])
        st_folium(create_map(temple, 'parking'), width=700, height=500, key=f"home_map_{temple}")
        if st.session_state.surge_active:
            st.warning(t['surge_alert'].format('peak hours'))
        if st.session_state.crowd_alert_sent:
            st.warning("🚨 Avoid area - High crowd detected! (#6 Push Sim)")
        st.info(t['wait_times'])
        st.info(t['temple_info'])
        st.info(t['emergency_sos_button'])
        st.info(t['accessibility_support'])
    
    with tabs[1]:  # #2 Full
        st.header(f"{t['virtual_darshan']} - {temple}")
        st.info(t['dynamic_slots'])
        priority = st.checkbox(t['elderly_priority'], key=f"pilgrim_priority_checkbox_{temple}")
        if st.button(t['join_btn'], use_container_width=True):
            user_id = len(st.session_state.queue_data) + 1
            msg = join_queue(temple, user_id, priority, lang)
            st.success(msg)
            # QR Sim
            qr_text = f"Pass: {temple}-User{user_id} Slot:{st.session_state.queue_data[-1]['slot']}"
            fig, ax = plt.subplots(figsize=(4,4))
            ax.text(0.5, 0.5, qr_text, ha='center', va='center', fontsize=12)
            ax.axis('off')
            st.pyplot(fig)
            st.info("Shows real-time waiting time and sends alerts when it’s their turn (#2)")
        if st.button(t['simulate_turn']):
            st.balloons()
            st.success(t['your_turn'])
        if st.session_state.queue_data:
            q_df = pd.DataFrame([q for q in st.session_state.queue_data if q.get('temple') == temple])
            for idx, row in q_df.iterrows():
                progress = min(100, (datetime.now() - row['join_time']).total_seconds() / 60 / row['est_wait'] * 100)
                st.progress(progress / 100)
                st.metric("Wait Left", f"{row['est_wait'] - progress/100 * row['est_wait']:.0f} min", f"Slot: {row['slot']}")
        if st.session_state.get('kiosk_mode', False):
            st.info("Kiosk Mode: Virtual queue management, digital darshan passes, and real-time updates via mobile apps and kiosks (#2)")
    
    with tabs[2]:  # #4 Full
        st.header(f"{t['emergency_sos']} - {temple}")
        if st.button(t['press_sos'], type="primary"):
            st.error(t['sos_sent'])
            st.session_state.drone_dispatched = True
            st.success(t['drone_dispatch'])
            st_folium(create_map(temple, 'drone'), width=700, height=500, key=f"sos_map_{temple}")
            trigger_emergency(temple, "Main Gate")
            st.info(t['abnormal_movement'])
            st.info(t['sudden_rush'])
            st.info(t['police_alert'])
            st.info(t['medical_alert'])
    
    with tabs[3]:  # #3 Full
        st.header(f"{t['surveillance']} - {temple}")
        if st.button(t['scan_now']):
            alert, density = simulate_monitoring()
            fig, ax = plt.subplots(figsize=(6,5))
            ax.pie([density, 1-density], labels=[t['crowded'], t['safe']], autopct='%1.1f%%', colors=['#ff6b6b', '#4ecdc4'])
            ax.set_title('Sensors, CCTV with AI analytics, and drones for crowd density monitoring and automated alerts (#3)')
            st.pyplot(fig)
            st.metric("Sensors", f"{density*100:.0f}%", "IoT")
            st.metric("Drones", "Active", delta="Monitoring")
            if alert:
                st.error(t['panic_detected'].format(alert['location']))
        st_folium(create_map(temple, 'drone'), width=700, height=500, key=f"surveillance_map_{temple}")
    
    with tabs[4]:  # #5 Full
        st.header(f"{t['parking_mobility']} - {temple}")
        empty_spots = get_parking_status(temple)
        st.info(t['empty_spots'].format(empty_spots))
        shuttle_status = get_shuttle_status(temple)
        st.subheader(t['shuttle_schedule'])
        schedule = pd.DataFrame({
            'Time': ['10AM', '12PM', '2PM', '4PM'],
            'From': [f"{temple} Parking", 'Main Gate', 'Bus Station', 'Approach Road'],
            'To': ['Temple', f"{temple} Parking", 'Temple', 'Shuttle Hub'],
            'Status': [shuttle_status, 'On Time', 'Delayed 5min', 'Police Coordinated']
        })
        st.dataframe(schedule.style.highlight_max(axis=0))
        st.subheader(t['traffic_flow'])
        flow = np.random.choice(['Smooth', 'Moderate', 'Congested'])
        st.metric("Flow Status", flow, "Police Dynamic System")
        st.info(t['iot_parking'])
        st.info(t['shuttle_police'])
        st_folium(create_map(temple, 'parking'), width=700, height=500, key=f"traffic_map_{temple}")
    
    with tabs[5]:  # #7 Full
        st.header(f"{t['voice_nav']} - {temple}")
        priority = st.checkbox(t['elderly_priority'], key=f"pilgrim_priority_checkbox_{temple}")
        support = get_accessibility_support(temple, priority)
        st.info(support)
        if st.button('Start Voice-Guided Mode (#7)'):
            st.info(t['audio_sim'])
            st.audio("data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcDbiIAA==", format="audio/wav")
        st.info(t['priority_entry'])
        if st.button('Track Smart Wheelchair (#7)'):
            user_id = np.random.randint(1, 10)
            location = track_wheelchair(temple, user_id)
            st.info(f"{t['smart_wheelchair_retrieval']}: {location}")
        if st.button('Request Volunteer Assist (#7)'):
            need = st.text_input("Need (e.g., elderly assist)")
            volunteer = coordinate_volunteer(temple, need)
            st.success(f"{t['volunteer_assist']}: {volunteer}")
        st_folium(create_map(temple, 'wheelchair'), width=700, height=500, key=f"access_map_{temple}")
    
    with tabs[6]:  # #4 Medical
        st.header(f"{t['medical_map']} - {temple}")
        st_folium(create_map(temple, 'medical'), width=700, height=500, key=f"medical_map_{temple}")
        st.info("Nearest Aid: 200m - Mapped for Quick Response.")

elif role == t['authority_dashboard']:
    tabs = st.tabs([t['prediction'], t['surveillance'], t['active_queues'], t['barricades'], t['traffic'], 'Engagement (#6)', t['accessibility']])
    
    with tabs[0]:  # #1
        st.header(f"{t['prediction']} - {temple}")
        pred_df = predict_crowd(temple, 7)
        if not pred_df.empty:
            st.dataframe(pred_df.style.background_gradient(cmap='YlOrRd'))
            fig, ax = plt.subplots(figsize=(10,5))
            bars = ax.bar([d.strftime('%Y-%m-%d') for d in pred_df['date']], pred_df['predicted_footfall'], color='orange')
            ax.set_title(f'AI-based Crowd Prediction & Monitoring: Forecast visitor surges based on historical + weather + festival calendar data (#1)')
            plt.xticks(rotation=45)
            st.pyplot(fig)
            high_surge = pred_df[pred_df['predicted_footfall'] > TEMPLE_DATA[temple]['base_footfall'] * 2]
            if not high_surge.empty:
                st.warning(t['surge_alert'].format(high_surge['date'].iloc[0].strftime('%Y-%m-%d')))
                st.session_state.surge_active = True
    
    with tabs[1]:  # #3
        st.header(f"{t['surveillance']} - {temple}")
        if st.button(t['scan_now'], use_container_width=True):
            alert, density = simulate_monitoring(temple)
            fig, ax = plt.subplots()
            ax.pie([density, 1-density], labels=[t['crowded'], t['safe']], autopct='%1.1f%%', colors=['#ff6b6b', '#4ecdc4'])
            st.pyplot(fig)
            st.metric("Sensors", f"{density*100:.0f}%", "IoT")
            st.metric("CCTV Feeds", "Live", "AI Analytics")
            st.metric("Drones", "4/5 Deployed", "Auto Patrol")
            if alert:
                st.error(t['panic_detected'].format(alert['location']))
        st_folium(create_map(temple, 'drone'), width=700, height=500, key=f"auth_surveillance_map_{temple}")
    
    with tabs[2]:  # #2 + #4
        st.header(f"{t['active_queues']} - {temple}")
        q_df = pd.DataFrame([q for q in st.session_state.queue_data if q.get('temple') == temple])
        if not q_df.empty:
            st.dataframe(q_df)
        a_df = pd.DataFrame([a for a in st.session_state.alerts if a.get('temple') == temple])
        if not a_df.empty:
            st.dataframe(a_df)
            if st.button(t['dispatch'], type="primary"):
                st.success(t['dispatched'])
        else:
            st.info(t['no_alerts'])
    
    with tabs[3]:  # #4 Barricades
        st.header(f"{t['barricades']} - {temple}")
        statuses = {'Main Gate': 'Locked (High Surge)', 'Darshan Hall': 'Open', 'Exit': 'Active'}
        for loc, stat in statuses.items():
            color = 'red' if 'Locked' in stat else 'green' if 'Open' in stat else 'orange'
            st.metric(loc, stat, delta="Smart barricade systems (#4)")
    
    with tabs[4]:  # #5
        st.header(f"{t['parking_mobility']} - {temple}")
        st_folium(create_map(temple, 'parking'), width=700, height=500, key=f"auth_traffic_map_{temple}")
        data = TEMPLE_DATA[temple]
        st.info(t['empty_spots'].format(int(data['base_footfall']/5000)))
        st.subheader(t['shuttle_schedule'])
        schedule = pd.DataFrame({
            'Time': ['10AM', '12PM', '2PM'],
            'Route': [f"{temple} Parking → Temple", 'Gate → Parking', 'Station → Temple'],
            'Coord': ['Police Cleared', 'On Time', 'Dynamic Reroute']
        })
        st.dataframe(schedule)
        st.subheader(t['traffic_flow'])
        light = np.random.choice(['🟢 Green', '🟡 Yellow', '🔴 Red'])
        st.metric("Flow", light, "Police Dynamic System")
    
    with tabs[5]:  # #6
        st.header(f"Pilgrim Engagement Platforms (#6) - {temple}")
        timings, routes, facilities, contacts = get_engagement_info(temple)
        col1, col2, col3 = st.columns(3)
        q_df = pd.DataFrame([q for q in st.session_state.queue_data if q.get('temple') == temple])
        col1.metric("Wait Times", f"{np.mean(q_df['est_wait']):.0f} min Avg" if not q_df.empty else "N/A")
        col2.metric("Notifications Sent", st.session_state.crowd_alert_sent + st.session_state.surge_active)
        col3.metric("Active Pilgrims", len(q_df))
        st.info(f"{t['temple_timings']}: {timings}")
        st.info(f"{t['routes']}: {routes}")
        st.info(f"{t['facilities']}: {facilities}")
        st.info(f"{t['emergency_contacts']}: {contacts}")
    
    with tabs[6]:  # #7
        st.header(f"{t['accessibility']} - {temple}")
        priority = st.checkbox(t['elderly_priority'], key=f"auth_priority_checkbox_{temple}")
        support = get_accessibility_support(temple, priority)
        st.info(support)
        if st.button('Start Voice-Guided Mode (#7)'):
            st.info(t['audio_sim'])
            st.audio("data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcDbiIAA==", format="audio/wav")
        st.info(t['priority_entry'])
        if st.button('Track Smart Wheelchair (#7)'):
            user_id = np.random.randint(1, 10)
            location = track_wheelchair(temple, user_id)
            st.info(f"{t['smart_wheelchair_retrieval']}: {location}")
        if st.button('Request Volunteer Assist (#7)'):
            need = st.text_input("Need (e.g., elderly assist)")
            volunteer = coordinate_volunteer(temple, need)
            st.success(f"{t['volunteer_assist']}: {volunteer}")
        st_folium(create_map(temple, 'wheelchair'), width=700, height=500, key=f"auth_access_map_{temple}")

# Live Log
with st.expander(t['live_log']):
    for entry in st.session_state.log_entries[-5:]:
        st.write(entry)

st.markdown("---")
st.caption(t['footer'])
