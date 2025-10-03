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

# Temple Data: Coords & Base Daily Footfall (from Gujarat Tourism/Wiki)
TEMPLE_DATA = {
    'Somnath': {'lat': 20.888, 'lng': 70.401, 'base_footfall': 50000},  # ~18M annual 
    'Dwarka': {'lat': 22.238, 'lng': 68.968, 'base_footfall': 25000},    # ~9M annual 
    'Ambaji': {'lat': 24.333, 'lng': 72.850, 'base_footfall': 25000},    # ~9M annual 
    'Pavagadh': {'lat': 22.461, 'lng': 73.512, 'base_footfall': 6000}    # ~2.2M annual 
}

# Hardcoded Multilingual Support (Expanded)
TRANSLATIONS = {
    'English': {
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
        'traffic_flow': 'Dynamic Traffic (#5)'
    },
    # Gujarati & Hindi: Mirror updates (abbrev for brevity; copy full from prev + new keys)
    'Gujarati': {**TRANSLATIONS['English'], 'title': '🛕 યાત્રા સેવક: મલ્ટી-મંદિર વ્યવસ્થાપન (4 સ્થળો)', 'select_temple': 'મંદિર પસંદ કરો', 'footer': '4 મંદિરો માટે વિસ્તરણીય: અંબાજી, દ્વારકા, પાવાગઢ, સોમનાથ. બધી 7 ફીચર્સ એકીકૃત. ❤️'},
    'Hindi': {**TRANSLATIONS['English'], 'title': '🛕 यात्रा सेवक: मल्टी-मंदिर प्रबंधन (4 स्थल)', 'select_temple': 'मंदिर चुनें', 'footer': '4 मंदिरों के लिए स्केलेबल: अंबाजी, द्वारका, पावागढ़, सोमनाथ। सभी 7 फीचर्स एकीकृत। ❤️'}
}

# Session State
if 'queue_data' not in st.session_state: st.session_state.queue_data = []
if 'alerts' not in st.session_state: st.session_state.alerts = []
if 'surge_active' not in st.session_state: st.session_state.surge_active = False
if 'crowd_alert_sent' not in st.session_state: st.session_state.crowd_alert_sent = False
if 'drone_dispatched' not in st.session_state: st.session_state.drone_dispatched = False

# Model with Temple Param (#1)
@st.cache_data
def load_and_train_model(base_footfall):
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', end='2026-01-01', freq='D')
    n = len(dates)
    festivals = ['2025-01-14', '2025-02-26', '2025-10-20', '2025-11-15', '2025-09-29', '2025-10-07']
    is_festival = [1 if d.strftime('%Y-%m-%d') in festivals else 0 for d in dates]
    temp = np.random.normal(28, 5, n).clip(15, 40)
    is_holiday = [(d.weekday() >= 5) or isf for d, isf in zip(dates, is_festival)]
    festival_boost = np.array(is_festival) * (base_footfall * 2)  # Scale boost by temple
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
        today = date(2025, 10, 3)
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
    return TRANSLATIONS[lang]['token_issued'].format(est_wait, slot) + f" ({slot_type} - Dynamic Slot)"

# Other Functions (Updated for Temple)
def simulate_monitoring(temple):
    density = np.random.uniform(0.3, 0.9)
    if density > 0.8:
        panic_chance = np.random.choice([True, False], p=[0.4, 0.6])
        if panic_chance:
            alert = {'type': 'Panic Detected', 'location': np.random.choice(['Main Gate', 'Darshan Hall', 'Parking']), 'temple': temple, 'time': datetime.now(), 'severity': 'High'}
            st.session_state.alerts.append(alert)
            st.session_state.crowd_alert_sent = True
            return alert, density
    return None, density

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
    return m

# UI
st.set_page_config(page_title="Yatra Sevak - 4 Temples", layout="wide")
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
st.sidebar.title(f"{t['title']} - {temple}")

# Sidebar Sims
st.sidebar.header("Demo Integrations")
if st.sidebar.button('Sim Surge: #1 → #2 (Limit Slots)'):
    st.session_state.surge_active = True
    st.rerun()
if st.sidebar.button('Sim Crowded: #3 → #4 → #6 (Alert App)'):
    simulate_monitoring(temple)
    st.rerun()

st.title(f"{t['title']} - {temple}")

if role == t['pilgrim_app']:
    tabs = st.tabs([t['home_info'], t['join_queue'], t['sos_nav'], t['surveillance'], t['traffic'], t['accessibility'], t['medical_map']])
    
    with tabs[0]:  # #6
        st.header(f"{t['temple_info_wait']} - {temple}")
        pred_df = predict_crowd(temple, 3)
        if not pred_df.empty:
            st.dataframe(pred_df[['date', 'predicted_footfall']].style.background_gradient(cmap='Blues'))
        col1, col2, col3 = st.columns(3)
        with col1: st.success(f"🕐 {t['temple_timings']}")
        with col2: st.info(f"🏥 {t['facilities']}")
        with col3: st.error(f"📞 {t['emergency_contacts']}")
        st.info(f"🗺️ {t['routes']}")
        st.info(t['current_weather'])
        folium_static(create_map(temple, 'parking'))
        if st.session_state.surge_active:
            st.warning(t['surge_alert'].format('peak hours'))
        if st.session_state.crowd_alert_sent:
            st.warning("🚨 Avoid area - High crowd detected! (#6 Push Sim)")
    
    with tabs[1]:  # #2
        st.header(f"{t['virtual_darshan']} - {temple}")
        st.info(t['dynamic_slots'])
        priority = st.checkbox(t['elderly_priority'])
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
        if st.button(t['simulate_turn']):
            st.balloons()
            st.success(t['your_turn'])
        if st.session_state.queue_data:
            q_df = pd.DataFrame([q for q in st.session_state.queue_data if q.get('temple') == temple])
            for idx, row in q_df.iterrows():
                progress = min(100, (datetime.now() - row['join_time']).total_seconds() / 60 / row['est_wait'] * 100)
                st.progress(progress / 100)
                st.metric("Wait Left", f"{row['est_wait'] - progress/100 * row['est_wait']:.0f} min", f"Slot: {row['slot']}")
    
    with tabs[2]:  # #4
        st.header(f"{t['emergency_sos']} - {temple}")
        if st.button(t['press_sos'], type="primary"):
            st.error(t['sos_sent'])
            st.session_state.drone_dispatched = True
            st.success(t['drone_dispatch'])
            folium_static(create_map(temple, 'drone'))
    
    with tabs[3]:  # #3
        st.header(f"{t['surveillance']} - {temple}")
        if st.button(t['scan_now']):
            alert, density = simulate_monitoring(temple)
            fig, ax = plt.subplots(figsize=(6,5))
            ax.pie([density, 1-density], labels=[t['crowded'], t['safe']], autopct='%1.1f%%', colors=['#ff6b6b', '#4ecdc4'])
            ax.set_title('CCTV Density (#3)')
            st.pyplot(fig)
            st.metric("Sensors", f"{density*100:.0f}%", "IoT")
            st.metric("Drones", "Active", delta="Monitoring")
            if alert:
                st.error(t['panic_detected'].format(alert['location']))
    
    with tabs[4]:  # #5
        st.header(f"{t['parking_mobility']} - {temple}")
        folium_static(create_map(temple, 'parking'))
        data = TEMPLE_DATA[temple]
        st.info(t['empty_spots'].format(int(data['base_footfall']/5000)))  # Scale spots by size
        st.subheader(t['shuttle_schedule'])
        schedule = pd.DataFrame({
            'Time': ['10AM', '12PM', '2PM', '4PM'],
            'From': [f"{temple} Parking", 'Main Gate', 'Bus Station', 'Approach Road'],
            'To': ['Temple', f"{temple} Parking", 'Temple', 'Shuttle Hub'],
            'Status': ['On Time', 'Delayed 5min', 'On Time', 'Police Coordinated']
        })
        st.dataframe(schedule.style.highlight_max(axis=0))
        st.subheader(t['traffic_flow'])
        flow = np.random.choice(['Smooth', 'Moderate', 'Congested'])
        st.metric("Flow Status", flow, "Police Dynamic System")
    
    with tabs[5]:  # #7
        st.header(f"{t['voice_nav']} - {temple}")
        if st.button('Start Voice-Guided Mode (#7)'):
            st.info(t['audio_sim'])
            # Sim Audio
            st.audio("data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcDbiIAA==", format="audio/wav")
        st.info("AR Navigation Sim: Priority route highlighted for disabled.")
    
    with tabs[6]:  # #4 Medical
        st.header(f"{t['medical_map']} - {temple}")
        folium_static(create_map(temple, 'medical'))
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
            ax.set_title(f'Surge Forecast - {temple} (#1: Historical/Weather/Holidays/Festivals)')
            plt.xticks(rotation=45)
            st.pyplot(fig)
            high_surge = pred_df[pred_df['predicted_footfall'] > TEMPLE_DATA[temple]['base_footfall'] * 2]
            if not high_surge.empty:
                st.warning(t['surge_alert'].format(high_surge['date'].iloc[0].strftime('%Y-%m-%d')))
                st.session_state.surge_active = True
    
    with tabs[1]:  # #3
        st.header(f"{t['surveillance']} - {temple}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t['scan_now'], use_container_width=True):
                alert, density = simulate_monitoring(temple)
                fig, ax = plt.subplots()
                ax.pie([density, 1-density], labels=[t['crowded'], t['safe']], autopct='%1.1f%%', colors=['#ff6b6b', '#4ecdc4'])
                st.pyplot(fig)
        with col2:
            st.metric("IoT Sensors", f"{density*100:.0f}% Density")
            st.metric("CCTV Feeds", "Live", "AI Analytics")
            st.metric("Drones", "4/5 Deployed", "Auto Patrol")
        if alert:
            st.error(t['panic_detected'].format(alert['location']))
            st.session_state.crowd_alert_sent = True
    
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
            st.metric(loc, stat, delta=f"AI-Enabled (#4)")
    
    with tabs[4]:  # #5
        st.header(f"{t['parking_mobility']} - {temple}")
        folium_static(create_map(temple, 'parking'))
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
        st.metric("Flow", light, "City Police System")
    
    with tabs[5]:  # #6
        st.header(f"Pilgrim Engagement (#6) - {temple}")
        col1, col2, col3 = st.columns(3)
        q_df = pd.DataFrame([q for q in st.session_state.queue_data if q.get('temple') == temple])
        col1.metric("Wait Times", f"{np.mean(q_df['est_wait']):.0f} min Avg" if not q_df.empty else "N/A")
        col2.metric("Notifications Sent", st.session_state.crowd_alert_sent + st.session_state.surge_active)
        col3.metric("Active Pilgrims", len(q_df))
        st.info(f"{t['temple_timings']} | {t['routes']} | {t['facilities']} | {t['emergency_contacts']}")
    
    with tabs[6]:  # #7
        st.header(f"{t['accessibility']} - {temple}")
        st.checkbox("Enable Priority Queues (#7)")
        if st.button("Broadcast Voice Nav"):
            st.success("Voice Guide Sent to All Devices (#7)")
            st.info(t['audio_sim'])

st.markdown("---")
st.caption(t['footer'])
