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
import time  # Added for real-time simulation

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
    'current_weather': 'Weather (for ): 28°C (Sim). Routes Below.',
    'virtual_darshan': 'Virtual Queue Management (#2)',
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
    'scan_now': 'Scan CCTV/Sensors/Drones (#3)',
    'crowded': 'Crowded (High Density)',
    'safe': 'Safe',
    'panic_detected': '🚨 Panic at {}! Triggered Alert (#3 → #4). Notify App .',
    'active_queues': 'Queues & Alerts (#2, #4)',
    'no_alerts': 'No Alerts.',
    'dispatch': 'Dispatch Responders',
    'dispatched': 'Dispatched! (Police/Medical).',
    'parking_mobility': 'Parking Guidance & Shuttle (#5)',
    'empty_spots': 'Empty Spots: {}/10. Police-Integrated Flow.',
    'footer': 'Scalable to 4 Temples: Ambaji, Dwarka, Pavagadh, Somnath. All 7 Features Integrated. ❤️',
    'predicted_crowd': 'Predicted Footfall (#1)',
    'temple_timings': 'Timings: 5AM-9PM ',
    'facilities': 'Facilities: Restrooms, Food, Medical ',
    'emergency_contacts': 'Contacts: Police 100, Medical 108 ',
    'routes': 'Routes: Gate → Hall → Exit ',
    'medical_map': 'Medical Mapping (#4)',
    'barricades': 'Smart Barricades (#4)',
    'drone_dispatch': 'Drone Dispatched w/ Camera/Speaker/Kit ',
    'dynamic_slots': 'Dynamic Slots: Free if Low Demand ',
    'voice_nav': 'Voice Mode for Visually Impaired ',
    'shuttle_schedule': 'Shuttle Coordination ',
    'traffic_flow': 'Dynamic Traffic ',
    'refresh_queue': 'Refresh Queue Status'
}

TRANSLATIONS = {
    'English': english_trans,
    'Gujarati': {
        **english_trans,
        'title': '🛕 યાત્રા સેવક: મલ્ટી-મંદિર વ્યવસ્થાપન (4 સ્થળો)',
        'select_temple': 'મંદિર પસંદ કરો',
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
        'current_weather': 'હવામાન (#1): 28°C (સિમ). નીચે માર્ગો.',
        'virtual_darshan': 'વર્ચ્યુઅલ કતાર વ્યવસ્થાપન (#2)',
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
        'scan_now': 'CCTV/સેન્સર/ડ્રોન સ્કેન (#3)',
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
        'predicted_crowd': 'અનુમાનિત ભીડ (#1)',
        'temple_timings': 'સમય: 5AM-9PM ',
        'facilities': 'સુવિધાઓ: રેસ્ટરૂમ, ખાવાનું, મેડિકલ ',
        'emergency_contacts': 'સંપર્ક: પોલીસ 100, મેડિકલ 108 ',
        'routes': 'માર્ગ: ગેટ → હોલ → એક્ઝિટ ',
        'medical_map': 'મેડિકલ મેપિંગ (#4)',
        'barricades': 'સ્માર્ટ બેરિકેડ્સ (#4)',
        'drone_dispatch': 'કેમેરા/સ્પીકર/કીટ સાથે ડ્રોન મોકલાયું ',
        'dynamic_slots': 'ડાયનેમિક સ્લોટ્સ: ઓછી માંગમાં મફત ',
        'voice_nav': 'દ્રષ્ટિહીન માટે વૉઇસ મોડ ',
        'shuttle_schedule': 'શટલ કોર્ડિનેશન ',
        'traffic_flow': 'ડાયનેમિક ટ્રાફિક ',
        'refresh_queue': 'કતાર સ્થિતિ તાજી કરો'
    },
    'Hindi': {
        **english_trans,
        'title': '🛕 यात्रा सेवक: मल्टी-मंदिर प्रबंधन (4 स्थल)',
        'select_temple': 'मंदिर चुनें',
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
        'current_weather': 'मौसम (#1): 28°C (सिम). नीचे मार्ग.',
        'virtual_darshan': 'वर्चुअल कतार प्रबंधन (#2)',
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
        'scan_now': 'CCTV/सेंसर/ड्रोन स्कैन (#3)',
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
        'predicted_crowd': 'अनुमानित भीड़ (#1)',
        'temple_timings': 'समय: 5AM-9PM ',
        'facilities': 'सुविधाएं: रेस्टोरूम, खाना, मेडिकल ',
        'emergency_contacts': 'संपर्क: पुलिस 100, मेडिकल 108 ',
        'routes': 'मार्ग: गेट → हॉल → एक्जिट ',
        'medical_map': 'मेडिकल मैपिंग (#4)',
        'barricades': 'स्मार्ट बैरिकेड्स (#4)',
        'drone_dispatch': 'कैमरा/स्पीकर/किट के साथ ड्रोन भेजा ',
        'dynamic_slots': 'डायनामिक स्लॉट्स: कम मांग में मुफ्त ',
        'voice_nav': 'दृष्टिबाधित के लिए वॉइस मोड ',
        'shuttle_schedule': 'शटल कोऑर्डिनेशन ',
        'traffic_flow': 'डायनामिक ट्रैफिक ',
        'refresh_queue': 'कतार स्थिति रिफ्रेश करें'
    }
}
# Session State - Enhanced for usability
if 'queue_data' not in st.session_state: st.session_state.queue_data = []
if 'alerts' not in st.session_state: st.session_state.alerts = []
if 'surge_active' not in st.session_state: st.session_state.surge_active = False
if 'crowd_alert_sent' not in st.session_state: st.session_state.crowd_alert_sent = False
if 'drone_dispatched' not in st.session_state: st.session_state.drone_dispatched = False
if 'density' not in st.session_state: st.session_state.density = 0.0
if 'alert' not in st.session_state: st.session_state.alert = None
if 'user_id' not in st.session_state: st.session_state.user_id = None  # For pilgrim view tracking

# Model with Temple Param (#1) - AI/ML-based Crowd Prediction
@st.cache_data
def load_and_train_model(base_footfall):
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', end='2026-01-01', freq='D')
    n = len(dates)
    festivals = ['2025-01-14', '2025-02-26', '2025-10-20', '2025-11-15', '2025-09-29', '2025-10-07']  # Example festivals
    is_festival = [1 if d.strftime('%Y-%m-%d') in festivals else 0 for d in dates]
    temp = np.random.normal(28, 5, n).clip(15, 40)  # Simulated weather
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
        today = date(2025, 10, 4)  # Set to current date as per prompt
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

# Queue Management (#2) - Smart Queue & Ticketing
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
    return TRANSLATIONS[lang]['token_issued'].format(est_wait, slot) + f" ({slot_type} - Dynamic Slot)"

# Surveillance Simulation (#3) - IoT & Surveillance
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

# Map Creation for Various Features (#4, #5, #7)
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

# UI - Enhanced for Usability with All Features Highlighted
st.set_page_config(page_title="Yatra Sevak - 4 Temples", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
.main {background-color: #e6f3ff;}
.stTabs [data-baseweb="tab-list"] {gap: 0.5rem; font-size: 1.1rem;}
.stTab > div > div {padding: 1.5rem; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);}
.metric {background-color: #4CAF50; color: white; border-radius: 8px; padding: 10px;}
.stButton > button {background-color: #007bff; color: white; border-radius: 8px;}
.stButton > button:hover {background-color: #0056b3;}
.section-header {font-size: 1.5rem; font-weight: bold; color: #333;}
.stProgress > div > div > div > div {background-color: #007bff;}
</style>
""", unsafe_allow_html=True)

lang = st.sidebar.selectbox(TRANSLATIONS['English']['language'], ['English', 'Gujarati', 'Hindi'])
t = TRANSLATIONS[lang]
temple = st.sidebar.selectbox(t['select_temple'], list(TEMPLE_DATA.keys()))
role = st.sidebar.selectbox(t['view_as'], [t['pilgrim_app'], t['authority_dashboard']])
st.sidebar.title(f"{t['title']} - {temple}")

# Sidebar Sims - For Demo and Usability Testing
st.sidebar.header("Demo Simulations (For Testing Features)")
if st.sidebar.button('Simulate Surge (#1 → #2)'):
    st.session_state.surge_active = True
    st.rerun()
if st.sidebar.button('Simulate Crowd Panic (#3 → #4 → #6)'):
    simulate_monitoring(temple)
    st.rerun()
st.sidebar.markdown("---")
st.sidebar.info("Prototype simulates all 7 features: AI Prediction (#1), Queue/Ticketing (#2), Surveillance (#3), Emergency (#4), Traffic (#5), Engagement (#6), Accessibility (#7). No real hardware needed.")

st.title(f"{t['title']} - {temple}")

if role == t['pilgrim_app']:
    if st.session_state.user_id is None:
        st.session_state.user_id = len(st.session_state.queue_data) + 1  # Assign a user ID for tracking
    tabs = st.tabs([t['home_info'], t['join_queue'], t['sos_nav'], t['surveillance'], t['traffic'], t['accessibility'], t['medical_map'], t['prediction']])  # Added dedicated prediction tab for usability
    
    with tabs[0]:  # #6 - Pilgrim Engagement Platforms
        st.markdown(f"<div class='section-header'>{t['temple_info_wait']}</div>", unsafe_allow_html=True)
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
            st.warning(t['surge_alert'])
        if st.session_state.crowd_alert_sent:
            st.warning("🚨 Avoid area - High crowd detected! (#6 Notification)")
    
    with tabs[1]:  # #2 - Smart Queue & Ticketing Systems
        st.markdown(f"<div class='section-header'>{t['virtual_darshan']}</div>", unsafe_allow_html=True)
        st.info(t['dynamic_slots'])
        priority = st.checkbox(t['elderly_priority'])
        if st.button(t['join_btn'], use_container_width=True):
            msg = join_queue(temple, st.session_state.user_id, priority, lang)
            st.success(msg)
            # QR Code Simulation
            qr_text = f"Pass: {temple}-User{st.session_state.user_id} Slot:{st.session_state.queue_data[-1]['slot']}"
            fig, ax = plt.subplots(figsize=(4,4))
            ax.text(0.5, 0.5, qr_text, ha='center', va='center', fontsize=12, bbox=dict(facecolor='white', edgecolor='black', boxstyle='square,pad=1'))
            ax.axis('off')
            st.pyplot(fig)
        if st.button(t['simulate_turn']):
            st.balloons()
            st.success(t['your_turn'])
        if st.session_state.queue_data:
            q_df = pd.DataFrame([q for q in st.session_state.queue_data if q.get('temple') == temple and q.get('user_id') == st.session_state.user_id])
            if not q_df.empty:
                for idx, row in q_df.iterrows():
                    elapsed = (datetime.now() - row['join_time']).total_seconds() / 60
                    remaining = max(0, row['est_wait'] - elapsed)
                    progress = min(1.0, elapsed / row['est_wait'])
                    st.progress(progress)
                    st.metric("Wait Left", f"{remaining:.0f} min", f"Slot: {row['slot']}")
                if st.button(t['refresh_queue']):
                    st.rerun()  # Real-time update
    
    with tabs[2]:  # #4 - Emergency & Safety Solutions
        st.markdown(f"<div class='section-header'>{t['emergency_sos']}</div>", unsafe_allow_html=True)
        if st.button(t['press_sos'], type="primary"):
            st.error(t['sos_sent'])
            st.session_state.drone_dispatched = True
            st.success(t['drone_dispatch'])
            folium_static(create_map(temple, 'drone'))
    
    with tabs[3]:  # #3 - IoT & Surveillance Systems
        st.markdown(f"<div class='section-header'>{t['surveillance']}</div>", unsafe_allow_html=True)
        if st.button(t['scan_now']):
            alert, density = simulate_monitoring(temple)
            fig, ax = plt.subplots(figsize=(6,5))
            ax.pie([density, 1-density], labels=[t['crowded'], t['safe']], autopct='%1.1f%%', colors=['#ff6b6b', '#4ecdc4'], shadow=True, explode=(0.1, 0))
            ax.set_title('CCTV Density (#3)')
            st.pyplot(fig)
            st.metric("Sensors", f"{density*100:.0f}%", "IoT")
            st.metric("Drones", "Active", delta="Monitoring")
            if alert:
                st.error(t['panic_detected'].format(alert['location']))
    
    with tabs[4]:  # #5 - Traffic & Mobility Management
        st.markdown(f"<div class='section-header'>{t['parking_mobility']}</div>", unsafe_allow_html=True)
        folium_static(create_map(temple, 'parking'))
        data = TEMPLE_DATA[temple]
        st.info(t['empty_spots'].format(int(data['base_footfall']/5000)))
        st.subheader(t['shuttle_schedule'])
        schedule = pd.DataFrame({
            'Time': ['10AM', '12PM', '2PM', '4PM'],
            'From': [f"{temple} Parking", 'Main Gate', 'Bus Station', 'Approach Road'],
            'To': ['Temple', f"{temple} Parking", 'Temple', 'Shuttle Hub'],
            'Status': ['On Time', 'Delayed 5min', 'On Time', 'Police Coordinated']
        })
        st.dataframe(schedule.style.background_gradient(cmap='viridis'))
        st.subheader(t['traffic_flow'])
        flow = np.random.choice(['Smooth', 'Moderate', 'Congested'])
        st.metric("Flow Status", flow, "Police Dynamic System")
    
    with tabs[5]:  # #7 - Accessibility Features
        st.markdown(f"<div class='section-header'>{t['voice_guide']}</div>", unsafe_allow_html=True)
        if st.button('Start Voice-Guided Mode (#7)'):
            st.info(t['audio_sim'])
            st.audio("data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcDbiIAA==", format="audio/wav")
        st.info("AR Navigation Sim: Priority route highlighted for disabled/elderly.")
    
    with tabs[6]:  # #4 - Medical Assistance Mapping (Part of Emergency)
        st.markdown(f"<div class='section-header'>{t['medical_map']}</div>", unsafe_allow_html=True)
        folium_static(create_map(temple, 'medical'))
        st.info("Nearest Aid: 200m - Mapped for Quick Response (#4).")
    
    with tabs[7]:  # #1 - Dedicated AI Crowd Prediction for Usability
        st.markdown(f"<div class='section-header'>{t['prediction']}</div>", unsafe_allow_html=True)
        pred_df = predict_crowd(temple, 7)
        if not pred_df.empty:
            st.dataframe(pred_df.style.background_gradient(cmap='YlOrRd'))
            fig, ax = plt.subplots(figsize=(10,5))
            bars = ax.bar([d.strftime('%Y-%m-%d') for d in pred_df['date']], pred_df['predicted_footfall'], color='orange', edgecolor='black')
            ax.set_title(f'Predicted Footfall - {temple} (#1)')
            ax.set_ylabel('Footfall')
            ax.set_xlabel('Date')
            plt.xticks(rotation=45)
            st.pyplot(fig)

elif role == t['authority_dashboard']:
    tabs = st.tabs([t['prediction'], t['surveillance'], t['active_queues'], t['barricades'], t['traffic'], 'Engagement (#6)', t['accessibility'], t['sos_nav']])  # Added SOS for completeness
    
    with tabs[0]:  # #1 - AI/ML-based Crowd Prediction Models
        st.markdown(f"<div class='section-header'>{t['prediction']}</div>", unsafe_allow_html=True)
        pred_df = predict_crowd(temple, 7)
        if not pred_df.empty:
            st.dataframe(pred_df.style.background_gradient(cmap='YlOrRd'))
            fig, ax = plt.subplots(figsize=(10,5))
            bars = ax.bar([d.strftime('%Y-%m-%d') for d in pred_df['date']], pred_df['predicted_footfall'], color='orange', edgecolor='black')
            ax.set_title(f'Surge Forecast - {temple} (#1: Historical/Weather/Holidays/Festivals)')
            ax.set_ylabel('Footfall')
            ax.set_xlabel('Date')
            plt.xticks(rotation=45)
            st.pyplot(fig)
            high_surge = pred_df[pred_df['predicted_footfall'] > TEMPLE_DATA[temple]['base_footfall'] * 2]
            if not high_surge.empty:
                st.warning(t['surge_alert'].format(high_surge['date'].iloc[0].strftime('%Y-%m-%d')))
                st.session_state.surge_active = True
    
    with tabs[1]:  # #3 - IoT & Surveillance Systems
        st.markdown(f"<div class='section-header'>{t['surveillance']}</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t['scan_now'], use_container_width=True):
                st.session_state.alert, st.session_state.density = simulate_monitoring(temple)
                fig, ax = plt.subplots()
                ax.pie([st.session_state.density, 1-st.session_state.density], labels=[t['crowded'], t['safe']], autopct='%1.1f%%', colors=['#ff6b6b', '#4ecdc4'], shadow=True, explode=(0.1, 0))
                st.pyplot(fig)
        with col2:
            st.metric("IoT Sensors", f"{st.session_state.density*100:.0f}% Density")
            st.metric("CCTV Feeds", "Live", "AI Analytics")
            st.metric("Drones", "4/5 Deployed", "Auto Patrol")
        if st.session_state.alert:
            st.error(t['panic_detected'].format(st.session_state.alert['location']))
            st.session_state.crowd_alert_sent = True
    
    with tabs[2]:  # #2 + #4 - Smart Queue & Emergency Alerts
        st.markdown(f"<div class='section-header'>{t['active_queues']}</div>", unsafe_allow_html=True)
        q_df = pd.DataFrame([q for q in st.session_state.queue_data if q.get('temple') == temple])
        if not q_df.empty:
            st.dataframe(q_df.style.background_gradient(cmap='coolwarm'))
        a_df = pd.DataFrame([a for a in st.session_state.alerts if a.get('temple') == temple])
        if not a_df.empty:
            st.dataframe(a_df.style.highlight_max(axis=0))
            if st.button(t['dispatch'], type="primary"):
                st.success(t['dispatched'])
        else:
            st.info(t['no_alerts'])
    
    with tabs[3]:  # #4 - Smart Barricade Systems
        st.markdown(f"<div class='section-header'>{t['barricades']}</div>", unsafe_allow_html=True)
        statuses = {'Main Gate': 'Locked (High Surge)', 'Darshan Hall': 'Open', 'Exit': 'Active'}
        for loc, stat in statuses.items():
            color = 'red' if 'Locked' in stat else 'green' if 'Open' in stat else 'orange'
            st.metric(loc, stat, delta="AI-Enabled (#4)")
    
    with tabs[4]:  # #5 - Traffic & Mobility Management
        st.markdown(f"<div class='section-header'>{t['parking_mobility']}</div>", unsafe_allow_html=True)
        folium_static(create_map(temple, 'parking'))
        data = TEMPLE_DATA[temple]
        st.info(t['empty_spots'].format(int(data['base_footfall']/5000)))
        st.subheader(t['shuttle_schedule'])
        schedule = pd.DataFrame({
            'Time': ['10AM', '12PM', '2PM'],
            'Route': [f"{temple} Parking → Temple", 'Gate → Parking', 'Station → Temple'],
            'Coord': ['Police Cleared', 'On Time', 'Dynamic Reroute']
        })
        st.dataframe(schedule.style.background_gradient(cmap='viridis'))
        st.subheader(t['traffic_flow'])
        light = np.random.choice(['🟢 Green', '🟡 Yellow', '🔴 Red'])
        st.metric("Flow", light, "City Police System")
    
    with tabs[5]:  # #6 - Pilgrim Engagement Platforms
        st.markdown(f"<div class='section-header'>Pilgrim Engagement (#6)</div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        q_df = pd.DataFrame([q for q in st.session_state.queue_data if q.get('temple') == temple])
        col1.metric("Avg Wait Time", f"{np.mean(q_df['est_wait']):.0f} min" if not q_df.empty else "N/A")
        col2.metric("Notifications Sent", int(st.session_state.crowd_alert_sent) + int(st.session_state.surge_active))
        col3.metric("Active Pilgrims", len(q_df))
        st.info(f"{t['temple_timings']} | {t['routes']} | {t['facilities']} | {t['emergency_contacts']}")
    
    with tabs[6]:  # #7 - Accessibility Features
        st.markdown(f"<div class='section-header'>{t['accessibility']}</div>", unsafe_allow_html=True)
        st.checkbox("Enable Priority Queues (#7)")
        if st.button("Broadcast Voice Navigation (#7)"):
            st.success("Voice Guide Broadcasted to Devices (#7)")
            st.info(t['audio_sim'])
    
    with tabs[7]:  # #4 - Emergency & Safety Solutions (Authority View)
        st.markdown(f"<div class='section-header'>{t['sos_nav']}</div>", unsafe_allow_html=True)
        st.info("Monitor SOS Alerts and Dispatch (#4)")
        if st.session_state.drone_dispatched:
            st.success(t['drone_dispatch'])
        folium_static(create_map(temple, 'medical'))

st.markdown("---")
st.caption(t['footer'])

# Auto-refresh for real-time usability (every 30 seconds)
time.sleep(30)
st.rerun()
