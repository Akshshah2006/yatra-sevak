import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
from sklearn.model_selection import train_test_split
import time

# Temple Data
TEMPLE_DATA = {
    'Somnath': {'lat': 20.888, 'lng': 70.401, 'base_footfall': 50000},
    'Dwarka': {'lat': 22.238, 'lng': 68.968, 'base_footfall': 25000},
    'Ambaji': {'lat': 24.333, 'lng': 72.850, 'base_footfall': 25000},
    'Pavagadh': {'lat': 22.461, 'lng': 73.512, 'base_footfall': 6000}
}

# TRANSLATIONS (Full, Fixed)
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
    'live_mode': 'Live Mode (Auto-Update)',
    'temple_info_wait': 'Engagement: Timings, Routes, Facilities (#6)',
    'current_weather': 'Live Weather (for #1): {}°C. Routes Below.',
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
    'drone_dispatch': 'Drone Dispatched'
}

TRANSLATIONS = {
    'English': english_trans,
    'Gujarati': {
        **english_trans,
        'title': '🛕 યાત્રા સેવક: મલ્ટી-મંદિર વ્યવસ્થાપન (4 સ્થળો)',
        'select_temple': 'મંદિર પસંદ કરો',
        'live_mode': 'લાઇવ મોડ (ઓટો-અપડેટ)',
        'home_info': 'ઘર અને મંદિર માહિતી (#6)',
        'join_queue': 'સ્માર્ટ કતાર અને ટિકિટિંગ (#2)',
        'sos_nav': 'ઇમરજન્સી અને સુરક્ષા (#4)',
        'surveillance': 'IoT અને સર્વેલન્સ (#3)',
        'traffic': 'ટ્રાફિક અને મોબિલિટી (#5)',
        'accessibility': 'પહોંચવાની સુવિધાઓ (#7)',
        'prediction': 'AI ભીડ અનુમાન (#1)',
        'pilgrim_app': 'તીર્થયાત્રી વ્યૂ',
        'authority_dashboard': 'અધિકારી ડેશબોર્ડ',
        'language': 'ભાષા / ભાષા / भाषा',
        'view_as': 'જોવા માટે',
        'temple_info_wait': 'એન્ગેજમેન્ટ: સમય, માર્ગ, સુવિધાઓ (#6)',
        'current_weather': 'લાઇવ હવામાન (#1): {}°C. નીચે માર્ગો.',
        'virtual_darshan': 'વર્ચ્યુઅલ કતાર વ્યવસ્થાપન',
        'elderly_priority': 'વૃદ્ધ/અપંગ માટે પ્રાયોરિટી (#7)',
        'join_btn': 'ડિજિટલ દર્શન પાસ મેળવો',
        'simulate_turn': 'તમારી વાર સિમ્યુલેટ કરો',
        'token_issued': 'પાસ જારી! વાટ: {} મિન. સ્લોટ: {}. રીઅલ-ટાઇમ અપડેટ.',
        'your_turn': 'તમારી વાર! આગળ વધો.',
        'emergency_sos': 'SOS બટન (#4)',
        'press_sos': '🚨 SOS દબાવો',
        'sos_sent': 'SOS મોકલાયું! પ્રથમ પ્રતિભાગીઓ અલર્ટ. ડ્રોન મોકલાયું.',
        'voice_guide': 'વૉઇસ-ગાઇડેડ નેવિગેશન (#7)',
        'audio_sim': "વૉઇસ: '50mમાં ડાબી વળો પ્રાયોરિટી એન્ટ્રી તરફ.'",
        'surge_alert': 'સર્જ અનુમાન: સ્લોટ્સ મર્યાદિત (#1 → #2)',
        'scan_now': 'CCTV/સેન્સર/ડ્રોન સ્કેન',
        'crowded': 'ભીડ (ઉચ્ચ ઘનતા)',
        'safe': 'સુરક્ષિત',
        'panic_detected': '🚨 {} પર પેનિક! અલર્ટ ટ્રિગર (#3 → #4). એપને જાણ (#6).',
        'active_queues': 'કતારો અને અલર્ટ્સ (#2, #4)',
        'no_alerts': 'કોઈ અલર્ટ્સ નથી.',
        'dispatch': 'પ્રતિભાગીઓ મોકલો',
        'dispatched': 'મોકલાયું! (પોલીસ/મેડિકલ).',
        'parking_mobility': 'પાર્કિંગ માર્ગદર્શન અને શટલ (#5)',
        'empty_spots': 'ખાલી જગ્યા: {}/10. પોલીસ-એકીકૃત ફ્લો.',
        'footer': '4 મંદિરો માટે વિસ્તરણીય: અંબાજી, દ્વારકા, પાવાગઢ, સોમનાથ. બધી 7 ફીચર્સ એકીકૃત. ❤️',
        'predicted_crowd': 'અનુમાનિત ભીડ',
        'temple_timings': 'સમય: 5AM-9PM (#6)',
        'facilities': 'સુવિધાઓ: રેસ્ટરૂમ, ખાવાનું, મેડિકલ (#6)',
        'emergency_contacts': 'સંપર્ક: પોલીસ 100, મેડિકલ 108 (#6)',
        'routes': 'માર્ગ: ગેટ → હોલ → એક્ઝિટ (#6)',
        'medical_map': 'મેડિકલ મેપિંગ (#4)',
        'barricades': 'સ્માર્ટ બેરિકેડ્સ (#4)',
        'drone_dispatch': 'કેમેરા/સ્પીકર/કીટ સાથે ડ્રોન મોકલાયું (#4)',
        'dynamic_slots': 'ડાયનેમિક સ્લોટ્સ: ઓછી માંગમાં મફત (#2)',
        'voice_nav': 'દ્રષ્ટિહીન માટે વૉઇસ મોડ (#7)',
        'shuttle_schedule': 'શટલ કોર્ડિનેશન (#5)',
        'traffic_flow': 'ડાયનેમિક ટ્રાફિક (#5)',
        'live_log': 'લાઇવ ઇવેન્ટ લોગ',
        'cctv_feed': 'લાઇવ CCTV ફીડ (#3)',
        'drone_view': 'ડ્રોન પેટ્રોલ વ્યૂ (#3/#4)',
        'current_footfall': 'લાઇવ ફૂટફોલ કાઉન્ટર (#1)'
    },
    'Hindi': {
        **english_trans,
        'title': '🛕 यात्रा सेवक: मल्टी-मंदिर प्रबंधन (4 स्थल)',
        'select_temple': 'मंदिर चुनें',
        'live_mode': 'लाइव मोड (ऑटो-अपडेट)',
        'home_info': 'घर और मंदिर जानकारी (#6)',
        'join_queue': 'स्मार्ट कतार और टिकटिंग (#2)',
        'sos_nav': 'आपातकालीन और सुरक्षा (#4)',
        'surveillance': 'IoT और निगरानी (#3)',
        'traffic': 'ट्रैफिक और मोबिलिटी (#5)',
        'accessibility': 'पहुंच सुविधाएं (#7)',
        'prediction': 'AI भीड़ पूर्वानुमान (#1)',
        'pilgrim_app': 'तीर्थयात्री व्यू',
        'authority_dashboard': 'प्राधिकरण डैशबोर्ड',
        'language': 'भाषा / ભાષા / भाषा',
        'view_as': 'देखें के रूप में',
        'temple_info_wait': 'एंगेजमेंट: समय, मार्ग, सुविधाएं (#6)',
        'current_weather': 'लाइव मौसम (#1): {}°C. नीचे मार्ग.',
        'virtual_darshan': 'वर्चुअल कतार प्रबंधन',
        'elderly_priority': 'वृद्ध/अपंग के लिए प्राथमिकता (#7)',
        'join_btn': 'डिजिटल दर्शन पास प्राप्त करें',
        'simulate_turn': 'अपनी बारी सिमुलेट करें',
        'token_issued': 'पास जारी! प्रतीक्षा: {} मिन. स्लॉट: {}. रीयल-टाइम अपडेट.',
        'your_turn': 'आपकी बारी! आगे बढ़ें.',
        'emergency_sos': 'SOS बटन (#4)',
        'press_sos': '🚨 SOS दबाएं',
        'sos_sent': 'SOS भेजा! फर्स्ट रिस्पॉन्डर्स अलर्ट. ड्रोन भेजा.',
        'voice_guide': 'वॉइस-गाइडेड नेविगेशन (#7)',
        'audio_sim': "वॉइस: '50m में बाएं मुड़ें प्राथमिकता एंट्री की ओर।'",
        'surge_alert': 'सर्ज पूर्वानुमान: स्लॉट्स सीमित (#1 → #2)',
        'scan_now': 'CCTV/सेंसर/ड्रोन स्कैन',
        'crowded': 'भीड़ (उच्च घनत्व)',
        'safe': 'सुरक्षित',
        'panic_detected': '🚨 {} पर पैनिक! अलर्ट ट्रिगर (#3 → #4). ऐप को सूचित (#6).',
        'active_queues': 'कतारें और अलर्ट (#2, #4)',
        'no_alerts': 'कोई अलर्ट नहीं।',
        'dispatch': 'रिस्पॉन्डर्स भेजें',
        'dispatched': 'भेजा! (पुलिस/मेडिकल).',
        'parking_mobility': 'पार्किंग मार्गदर्शन और शटल (#5)',
        'empty_spots': 'खाली स्थान: {}/10. पुलिस-एकीकृत फ्लो.',
        'footer': '4 मंदिरों के लिए स्केलेबल: अंबाजी, द्वारका, पावागढ़, सोमनाथ। सभी 7 फीचर्स एकीकृत। ❤️',
        'predicted_crowd': 'अनुमानित भीड़',
        'temple_timings': 'समय: 5AM-9PM (#6)',
        'facilities': 'सुविधाएं: रेस्टोरूम, खाना, मेडिकल (#6)',
        'emergency_contacts': 'संपर्क: पुलिस 100, मेडिकल 108 (#6)',
        'routes': 'मार्ग: गेट → हॉल → एक्जिट (#6)',
        'medical_map': 'मेडिकल मैपिंग (#4)',
        'barricades': 'स्मार्ट बैरिकेड्स (#4)',
        'drone_dispatch': 'कैमरा/स्पीकर/किट के साथ ड्रोन भेजा (#4)',
        'dynamic_slots': 'डायनामिक स्लॉट्स: कम मांग में मुफ्त (#2)',
        'voice_nav': 'दृष्टिबाधित के लिए वॉइस मोड (#7)',
        'shuttle_schedule': 'शटल कोऑर्डिनेशन (#5)',
        'traffic_flow': 'डायनामिक ट्रैफिक (#5)',
        'live_log': 'लाइव इवेंट लॉग',
        'cctv_feed': 'लाइव CCTV फीड (#3)',
        'drone_view': 'ड्रोन पेट्रोल व्यू (#3/#4)',
        'current_footfall': 'लाइव फुटफॉल काउंटर (#1)'
    }
}

# Session State
if 'queue_data' not in st.session_state: st.session_state.queue_data = []
if 'alerts' not in st.session_state: st.session_state.alerts = []
if 'surge_active' not in st.session_state: st.session_state.surge_active = False
if 'crowd_alert_sent' not in st.session_state: st.session_state.crowd_alert_sent = False
if 'drone_dispatched' not in st.session_state: st.session_state.drone_dispatched = False
if 'live_footfall' not in st.session_state: st.session_state.live_footfall = 0
if 'density' not in st.session_state: st.session_state.density = 0.5
if 'log_entries' not in st.session_state: st.session_state.log_entries = []

def add_log(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    st.session_state.log_entries.append(f"[{timestamp}] {msg}")
    if len(st.session_state.log_entries) > 10: st.session_state.log_entries.pop(0)

# Surveillance (Moved up)
def simulate_monitoring(temple):
    st.session_state.density = np.random.uniform(0.3, 0.9)
    alert = None
    if st.session_state.density > 0.8:
        panic_chance = np.random.choice([True, False], p=[0.4, 0.6])
        if panic_chance:
            alert = {'type': 'Panic Detected', 'location': np.random.choice(['Main Gate', 'Darshan Hall', 'Parking']), 'temple': temple, 'time': datetime.now(), 'severity': 'High'}
            st.session_state.alerts.append(alert)
            st.session_state.crowd_alert_sent = True
            add_log(f"Panic alert: {alert['location']} at {temple}")
    return alert, st.session_state.density

# Model
@st.cache_data
def load_and_train_model(base_footfall):
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', end='2026-01-01', freq='D')
    n = len(dates)
    festivals = ['2025-01-14', '2025-02-26', '2025-10-20', '2025-11-15', '2025-09-29', '2025-10-07']
    is_festival = [1 if d.strftime('%Y-%m-%d') in festivals else 0 for d in dates]
    temp = np.random.normal(28, 5, n).clip(15, 40)
    is_holiday_list = [(d.weekday() >= 5) or isf for d, isf in zip(dates, is_festival)]
    is_holiday = pd.Series(is_holiday_list).astype(int)
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
        future_hol_list = [(d.weekday() >= 5) or ff for d, ff in zip(future_dates, future_fest)]
        future_hol = pd.Series(future_hol_list).astype(int)
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

# Queue
def join_queue(temple, user_id, priority=False, lang='English'):
    now = datetime.now()
    pred_df = predict_crowd(temple, 1)
    base = TEMPLE_DATA[temple]['base_footfall']
    surge_threshold = base * 2
    surge_penalty = 60 if (not pred_df.empty and pred_df['predicted_footfall'].iloc[0] > surge_threshold) else 0
    base_wait = np.random.randint(30, 120)
    est_wait = base_wait + (0 if priority else 15) - surge_penalty
    slot = (now + timedelta(minutes=est_wait)).strftime('%H:%M')
    slot_type = 'Free' if est_wait < 45 else 'Paid'
    entry = {'temple': temple, 'user_id': user_id, 'join_time': now, 'priority': priority, 'lang': lang, 'slot': slot, 'status': 'Waiting', 'est_wait': est_wait, 'slot_type': slot_type}
    st.session_state.queue_data.append(entry)
    add_log(f"Queue joined: User {user_id} at {temple}")
    return TRANSLATIONS[lang]['token_issued'].format(est_wait, slot) + f" ({slot_type} - Dynamic Slot)"

# Map
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
        drone_path = [[data['lat'], data['lng']], [data['lat'] + 0.002, data['lng'] - 0.001], [data['lat'] + 0.001, data['lng'] + 0.001]]
        folium.PolyLine(drone_path, color="blue", weight=2.5, popup="Drone Patrol Path").add_to(m)
        folium.Marker(drone_path[-1], popup="Drone Live Pos w/ Kit", icon=folium.Icon(color='blue')).add_to(m)
    return m

# UI
st.set_page_config(page_title="Yatra Sevak - Live Simulations", layout="wide")
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
live_mode = st.sidebar.checkbox(t['live_mode'])
if live_mode:
    time.sleep(5)
    st.rerun()
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

st.title(f"{t['title']} - {temple}")

# Live Footfall Counter
pred_df = predict_crowd(temple, 1)
st.session_state.live_footfall += np.random.randint(50, 200)
st.metric(t['current_footfall'], f"{st.session_state.live_footfall:,}", delta=f"+{np.random.randint(50, 200)}/min", help="Live from Sensors")

# Init Surveillance Defaults
if 'init_surveillance' not in st.session_state:
    alert, density = simulate_monitoring(temple)
    st.session_state.init_surveillance = True

if role == t['pilgrim_app']:
    tabs = st.tabs([t['home_info'], t['join_queue'], t['sos_nav'], t['surveillance'], t['traffic'], t['accessibility'], t['medical_map']])
    
    with tabs[0]:  # #6
        st.header(f"{t['temple_info_wait']} - {temple}")
        if not pred_df.empty:
            st.dataframe(pred_df[['date', 'predicted_footfall']].style.background_gradient(cmap='Blues'))
        col1, col2, col3 = st.columns(3)
        with col1: st.success(f"🕐 {t['temple_timings']}")
        with col2: st.info(f"🏥 {t['facilities']}")
        with col3: st.error(f"📞 {t['emergency_contacts']}")
        st.info(f"🗺️ {t['routes']}")
        weather_temp = np.random.normal(28, 2)
        st.info(t['current_weather'].format(weather_temp))
        st_folium(create_map(temple, 'parking'), width=700, height=500, key=f"pilgrim_home_map_{temple}")
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
            add_log("SOS drone dispatched to remote area")
            st.success(t['drone_dispatch'])
            st_folium(create_map(temple, 'drone'), width=700, height=500, key=f"pilgrim_sos_drone_{temple}")
    
    with tabs[3]:  # #3
        st.header(f"{t['surveillance']} - {temple}")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(t['cctv_feed'])
            # Fake Live CCTV
            try:
                st.video("https://archive.org/download/TempleCrowdSim/TempleCrowdLoop.mp4")
            except:
                fig, ax = plt.subplots(figsize=(6,4))
                circle = plt.Circle((0.5, 0.5), st.session_state.density, color='red', alpha=0.5)
                ax.add_patch(circle)
                ax.set_title('CCTV Density Overlay')
                ax.set_xlim(0,1); ax.set_ylim(0,1)
                st.pyplot(fig)
            st.caption(f"Live at {datetime.now().strftime('%H:%M:%S')} - Density: {st.session_state.density*100:.0f}%")
        with col2:
            st.subheader(t['drone_view'])
            if st.button(t['scan_now']):
                alert, density = simulate_monitoring(temple)
                fig, ax = plt.subplots(figsize=(5,4))
                ax.pie([density, 1-density], labels=[t['crowded'], t['safe']], autopct='%1.1f%%', colors=['#ff6b6b', '#4ecdc4'])
                ax.set_title('Drone Analytics (#3)')
                st.pyplot(fig)
                st.metric("Drones Active", "4/5", delta="Patrolling")
            st_folium(create_map(temple, 'drone'), width=700, height=500, key=f"pilgrim_surveillance_drone_{temple}")
            if 'alert' in locals() and alert:
                st.error(t['panic_detected'].format(alert['location']))
    
    with tabs[4]:  # #5
        st.header(f"{t['parking_mobility']} - {temple}")
        st_folium(create_map(temple, 'parking'), width=700, height=500, key=f"pilgrim_traffic_map_{temple}")
        data = TEMPLE_DATA[temple]
        st.info(t['empty_spots'].format(int(data['base_footfall']/5000)))
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
        st.header(f"{t['voice_nav']'}'
