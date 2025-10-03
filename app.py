# yatra_sevak_prototype.py
"""
Yatra Sevak - Enhanced Hackathon Prototype (single-file Streamlit app)
Run: streamlit run yatra_sevak_prototype.py

Notes:
- All original UI strings (translations) are preserved exactly.
- This file completes the previously-cut script and adds a Streamlit-only CCTV mock feed (OpenCV -> st.image).
- Requirements: streamlit, pandas, numpy, scikit-learn, matplotlib, folium, streamlit_folium, opencv-python
"""

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
import io
import base64
import json
import uuid
import math
from collections import deque
import time

# OpenCV import (used for CCTV mock feed)
try:
    import cv2
    OPENCV_AVAILABLE = True
except Exception:
    OPENCV_AVAILABLE = False

# ------------------------------
# KEEP YOUR ORIGINAL TRANSLATIONS EXACTLY (no modifications)
# ------------------------------
english_trans = {
    'title': '🛕 Yatra Sevak: Multi-Temple Management (4 Sites)',
    'select_temple': 'Select Temple',
    'home_info': 'Home & Temple Info ',
    'join_queue': 'Smart Queue & Ticketing ',
    'sos_nav': 'Emergency & Safety ',
    'surveillance': 'IoT & Surveillance ',
    'traffic': 'Traffic & Mobility ',
    'accessibility': 'Accessibility Features ',
    'prediction': 'AI Crowd Prediction ',
    'pilgrim_app': 'Pilgrim View',
    'authority_dashboard': 'Authority Dashboard',
    'language': 'Language / ભાષા / भाषा',
    'view_as': 'View As',
    'temple_info_wait': 'Engagement: Timings, Routes, Facilities ',
    'current_weather': 'Weather (for ): 28°C (Sim). Routes Below.',
    'virtual_darshan': 'Virtual Queue Management',
    'elderly_priority': 'Priority for Elderly/Disabled ',
    'join_btn': 'Get Digital Darshan Pass',
    'simulate_turn': 'Simulate Your Turn',
    'token_issued': 'Pass Issued! Wait: {} mins. Slot: {}. Real-time Update.',
    'your_turn': 'Your Turn! Proceed.',
    'emergency_sos': 'SOS Button ',
    'press_sos': '🚨 Press SOS',
    'sos_sent': 'SOS Sent! First Responders Alerted. Drone Dispatched.',
    'voice_guide': 'Voice-Guided Navigation ',
    'audio_sim': "Voice: 'Turn left 50m to priority entry.'",
    'surge_alert': 'Surge Forecast: Limiting Slots (#1 → #2)',
    'scan_now': 'Scan CCTV/Sensors/Drones',
    'crowded': 'Crowded (High Density)',
    'safe': 'Safe',
    'panic_detected': '🚨 Panic at {}! Triggered Alert (#3 → #4). Notify App .',
    'active_queues': 'Queues & Alerts (#2, #4)',
    'no_alerts': 'No Alerts.',
    'dispatch': 'Dispatch Responders',
    'dispatched': 'Dispatched! (Police/Medical).',
    'parking_mobility': 'Parking Guidance & Shuttle ',
    'empty_spots': 'Empty Spots: {}/10. Police-Integrated Flow.',
    'footer': 'Scalable to 4 Temples: Ambaji, Dwarka, Pavagadh, Somnath. All 7 Features Integrated. ❤️',
    'predicted_crowd': 'Predicted Footfall',
    'temple_timings': 'Timings: 5AM-9PM ',
    'facilities': 'Facilities: Restrooms, Food, Medical ',
    'emergency_contacts': 'Contacts: Police 100, Medical 108 ',
    'routes': 'Routes: Gate → Hall → Exit ',
    'medical_map': 'Medical Mapping ',
    'barricades': 'Smart Barricades ',
    'drone_dispatch': 'Drone Dispatched w/ Camera/Speaker/Kit ',
    'dynamic_slots': 'Dynamic Slots: Free if Low Demand ',
    'voice_nav': 'Voice Mode for Visually Impaired ',
    'shuttle_schedule': 'Shuttle Coordination ',
    'traffic_flow': 'Dynamic Traffic '
}

TRANSLATIONS = {
    'English': english_trans,
    'Gujarati': {
        **english_trans,
        'title': '🛕 યાત્રા સેવક: મલ્ટી-મંદિર વ્યવસ્થાપન (4 સ્થળો)',
        'select_temple': 'મંદિર પસંદ કરો',
        'home_info': 'ઘર અને મંદિર માહિતી (#6)',
        'join_queue': 'સ્માર્ટ કતાર અને ٹિકિટિંગ (#2)',
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
        'traffic_flow': 'ડાયનેમિક ટ્રાફિક (#5)'
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
        'traffic_flow': 'डायनामिक ट्राफिक (#5)'
    }
}

# ------------------------------
# Temple Data
# ------------------------------
TEMPLE_DATA = {
    'Somnath': {'lat': 20.888, 'lng': 70.401, 'base_footfall': 50000},
    'Dwarka': {'lat': 22.238, 'lng': 68.968, 'base_footfall': 25000},
    'Ambaji': {'lat': 24.333, 'lng': 72.850, 'base_footfall': 25000},
    'Pavagadh': {'lat': 22.461, 'lng': 73.512, 'base_footfall': 6000}
}

# ------------------------------
# Session State defaults
# ------------------------------
if 'queue_data' not in st.session_state: st.session_state.queue_data = []
if 'alerts' not in st.session_state: st.session_state.alerts = []
if 'surge_active' not in st.session_state: st.session_state.surge_active = False
if 'crowd_alert_sent' not in st.session_state: st.session_state.crowd_alert_sent = False
if 'drone_dispatched' not in st.session_state: st.session_state.drone_dispatched = False
if 'iot_state' not in st.session_state:
    st.session_state.iot_state = {
        'parking_spots': {t: int(max(2, TEMPLE_DATA[t]['base_footfall']//5000)) for t in TEMPLE_DATA},
        'sensor_stream': deque(maxlen=200),  # last sensor readings
        'wheelchairs': {t: {} for t in TEMPLE_DATA}  # id -> loc
    }
if 'models' not in st.session_state: st.session_state.models = {}
if 'ml_train_cache' not in st.session_state: st.session_state.ml_train_cache = {}
# CCTV controls in session
if 'cctv' not in st.session_state:
    st.session_state.cctv = {'running': False, 'source': 0, 'cap': None}

# ------------------------------
# ML training & prediction (kept from previous)
# ------------------------------
@st.cache_data
def train_crowd_model(base_footfall, temple_name):
    rng = np.random.RandomState(42 + abs(hash(temple_name)) % 1000)
    dates = pd.date_range(start='2023-01-01', end='2025-12-31', freq='D')
    n = len(dates)
    festivals = set([
        '2025-01-14', '2025-02-26', '2025-10-20', '2025-11-15', '2025-09-29',
        '2024-10-15', '2024-11-04', '2023-11-12'
    ])
    is_festival = np.array([1 if d.strftime('%Y-%m-%d') in festivals else 0 for d in dates])
    temp = rng.normal(28, 6, n).clip(10, 42)
    humidity = rng.uniform(30, 90, n)
    weekend = np.array([1 if d.weekday() >= 5 else 0 for d in dates])
    holiday = weekend | is_festival
    month = np.array([d.month for d in dates])
    seasonal_factor = 1 + 0.15 * np.sin((month - 1) / 12 * 2 * np.pi)
    festival_boost = is_festival * (base_footfall * 1.5)
    holiday_boost = holiday * (base_footfall * 0.25)
    weather_factor = ((30 - temp) / 15).clip(-0.5, 1.0)
    noise = rng.normal(0, base_footfall * 0.12, n)
    footfall = (base_footfall * seasonal_factor + festival_boost + holiday_boost + weather_factor * base_footfall * 0.12 + noise).clip(0, base_footfall * 4)
    df = pd.DataFrame({
        'date': dates,
        'footfall': footfall.astype(int),
        'temperature': temp,
        'humidity': humidity,
        'is_festival': is_festival,
        'is_holiday': holiday.astype(int),
        'month': month,
        'dayofweek': [d.weekday() for d in dates]
    })
    features = ['temperature', 'humidity', 'is_festival', 'is_holiday', 'month', 'dayofweek']
    X = df[features]
    y = df['footfall']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)
    st.session_state.models[temple_name] = {'model': model, 'features': features}
    return model, features, df

def get_model(temple):
    if temple not in st.session_state.models:
        train_crowd_model(TEMPLE_DATA[temple]['base_footfall'], temple)
    return st.session_state.models[temple]['model'], st.session_state.models[temple]['features']

def predict_crowd(temple, days_ahead=7, start_date=None):
    model, features = get_model(temple)
    if start_date is None:
        start_date = date.today()
    future_dates = pd.date_range(start=start_date, periods=days_ahead, freq='D')
    rng = np.random.RandomState(100 + abs(hash(temple)) % 1000)
    n = len(future_dates)
    future_festivals = set(['2025-10-20', '2025-11-01', '2025-11-15', '2025-12-25'])
    future_is_fest = np.array([1 if d.strftime('%Y-%m-%d') in future_festivals else 0 for d in future_dates])
    temp = rng.normal(28, 5, n).clip(10, 42)
    humidity = rng.uniform(30, 85, n)
    is_holiday = np.array([1 if d.weekday() >= 5 else 0 for d in future_dates]) | future_is_fest
    future_df = pd.DataFrame({
        'date': future_dates,
        'temperature': temp,
        'humidity': humidity,
        'is_festival': future_is_fest.astype(int),
        'is_holiday': is_holiday.astype(int),
        'month': [d.month for d in future_dates],
        'dayofweek': [d.weekday() for d in future_dates]
    })
    X_future = future_df[features]
    preds = model.predict(X_future).clip(0)
    future_df['predicted_footfall'] = preds.astype(int)
    return future_df

# ------------------------------
# Queue utilities
# ------------------------------
def compute_est_wait(base, predicted_today, priority=False, surge_active=False):
    ratio = predicted_today / max(1, base)
    est = int(max(5, 30 + (ratio - 1) * 60))
    if priority:
        est = max(3, int(est * 0.6))
    if surge_active:
        est = est + 30
    return est

def issue_pass(temple, user_id, priority, lang):
    now = datetime.now()
    pred = predict_crowd(temple, 1, start_date=date.today())
    predicted_today = int(pred['predicted_footfall'].iloc[0]) if not pred.empty else TEMPLE_DATA[temple]['base_footfall']
    base = TEMPLE_DATA[temple]['base_footfall']
    est_wait = compute_est_wait(base, predicted_today, priority, st.session_state.surge_active)
    slot_time = (now + timedelta(minutes=est_wait)).strftime('%H:%M')
    slot_type = 'Free' if est_wait < 45 else 'Paid'
    token = str(uuid.uuid4())[:8]
    entry = {
        'pass_id': token,
        'temple': temple,
        'user_id': user_id,
        'join_time': now.isoformat(),
        'priority': priority,
        'lang': lang,
        'slot': slot_time,
        'status': 'Waiting',
        'est_wait': est_wait,
        'slot_type': slot_type,
        'predicted_today': predicted_today
    }
    st.session_state.queue_data.append(entry)
    return entry

def get_token_text(entry):
    t = entry
    return f"Pass:{t['temple']}-User{t['user_id']}|PassID:{t['pass_id']}|Slot:{t['slot']}|Wait:{t['est_wait']}min|Type:{t['slot_type']}"

def download_bytes(name, data, mime='text/csv'):
    if isinstance(data, (pd.DataFrame, list, dict)):
        if isinstance(data, pd.DataFrame):
            b = data.to_csv(index=False).encode('utf-8')
        else:
            b = json.dumps(data, default=str, indent=2).encode('utf-8')
    elif isinstance(data, str):
        b = data.encode('utf-8')
    else:
        b = bytes(data)
    href = f"data:{mime};base64," + base64.b64encode(b).decode()
    return href

# ------------------------------
# IoT / Surveillance Simulation (kept)
# ------------------------------
def simulate_iot_activity(temple, ticks=1):
    s = st.session_state.iot_state
    base = TEMPLE_DATA[temple]['base_footfall']
    for _ in range(ticks):
        density = np.clip(np.random.beta(2, 5) + (0.5 if st.session_state.surge_active else 0) + (0.2 if st.session_state.crowd_alert_sent else 0), 0, 1)
        timestamp = datetime.now().isoformat()
        reading = {'temple': temple, 'timestamp': timestamp, 'density': float(density)}
        s['sensor_stream'].append(reading)
        if np.random.rand() < 0.05:
            wid = f"wc-{str(uuid.uuid4())[:6]}"
            s['wheelchairs'][temple][wid] = {
                'last_seen': timestamp,
                'lat': TEMPLE_DATA[temple]['lat'] + np.random.uniform(-0.002, 0.002),
                'lng': TEMPLE_DATA[temple]['lng'] + np.random.uniform(-0.002, 0.002),
                'status': 'parked'
            }
        for wid, w in list(s['wheelchairs'][temple].items()):
            if np.random.rand() < 0.3:
                w['lat'] += np.random.uniform(-0.0005, 0.0005)
                w['lng'] += np.random.uniform(-0.0005, 0.0005)
                w['last_seen'] = timestamp
                w['status'] = np.random.choice(['moving', 'parked'])
            if (datetime.now() - datetime.fromisoformat(w['last_seen'])).total_seconds() > 3600:
                del s['wheelchairs'][temple][wid]
    return s['sensor_stream'][-1] if s['sensor_stream'] else {'density': 0.0}

def detect_panic_from_stream(temple):
    s = st.session_state.iot_state
    readings = [r for r in s['sensor_stream'] if r['temple'] == temple]
    if len(readings) < 6:
        return None
    recent = readings[-6:]
    densities = [r['density'] for r in recent]
    if densities[-1] - np.median(densities[:-1]) > 0.35 and densities[-1] > 0.6:
        alert = {
            'type': 'Panic Detected',
            'location': np.random.choice(['Main Gate', 'Darshan Hall', 'Parking']),
            'temple': temple,
            'time': datetime.now().isoformat(),
            'severity': 'High',
            'density': densities[-1]
        }
        st.session_state.alerts.append(alert)
        st.session_state.crowd_alert_sent = True
        return alert
    return None

# ------------------------------
# Map creation
# ------------------------------
def create_map(temple, feature='parking'):
    data = TEMPLE_DATA[temple]
    m = folium.Map(location=[data['lat'], data['lng']], zoom_start=15, control_scale=True)
    folium.Marker([data['lat'], data['lng']], popup=f"{temple} Temple", icon=folium.Icon(color='red')).add_to(m)
    capacity = max(2, int(TEMPLE_DATA[temple]['base_footfall']//5000))
    occupancy = np.random.randint(0, capacity+1)
    for i in range(capacity):
        lat = data['lat'] + 0.001 * (i % 2) * (1 if i%3==0 else -1)
        lng = data['lng'] + 0.001 * (i % 3) * (1 if i%2==0 else -1)
        popup = "Empty Parking" if i >= occupancy else "Occupied"
        color = 'green' if i >= occupancy else 'gray'
        folium.CircleMarker([lat, lng], radius=6, color=color, fill=True, popup=popup).add_to(m)
    if feature == 'medical':
        folium.Marker([data['lat'] - 0.002, data['lng'] + 0.002], popup="Medical Center", icon=folium.Icon(color='orange')).add_to(m)
    if feature == 'drone' and st.session_state.drone_dispatched:
        folium.Marker([data['lat'] + 0.0015, data['lng'] - 0.0005], popup="Drone w/ Kit", icon=folium.Icon(color='blue')).add_to(m)
    return m

# ------------------------------
# CCTV helper functions (Streamlit-only using st.image)
# ------------------------------
def start_cctv(source=0):
    if not OPENCV_AVAILABLE:
        st.warning("OpenCV isn't available in this environment. Install opencv-python to enable CCTV mock feed.")
        return None
    # release prior cap if exists
    if st.session_state.cctv.get('cap') is not None:
        try:
            st.session_state.cctv['cap'].release()
        except Exception:
            pass
    cap = cv2.VideoCapture(source)
    st.session_state.cctv['cap'] = cap
    st.session_state.cctv['running'] = True
    st.session_state.cctv['source'] = source
    return cap

def stop_cctv():
    if st.session_state.cctv.get('cap') is not None:
        try:
            st.session_state.cctv['cap'].release()
        except Exception:
            pass
    st.session_state.cctv['cap'] = None
    st.session_state.cctv['running'] = False

def stream_cctv_frame(image_placeholder, fps=10):
    """Read a single frame from cap and update image_placeholder."""
    cap = st.session_state.cctv.get('cap')
    if cap is None or not cap.isOpened():
        image_placeholder.image(np.zeros((480, 640, 3), dtype=np.uint8), caption="No CCTV Source", channels="BGR")
        return False
    success, frame = cap.read()
    if not success:
        # if reading video file ended, restart if source is file path; otherwise show blank
        image_placeholder.image(np.zeros((480, 640, 3), dtype=np.uint8), caption="Frame read failed", channels="BGR")
        return False
    # Convert BGR to RGB for Streamlit
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image_placeholder.image(frame_rgb, caption=f"CCTV Feed ({st.session_state.cctv['source']})", use_column_width=True)
    return True

# ------------------------------
# UI layout
# ------------------------------
st.set_page_config(page_title="Yatra Sevak - 4 Temples (Prototype)", layout="wide")
st.markdown("""
<style>
.main {background-color: #e6f3ff;}
.stTabs [data-baseweb="tab-list"] {gap: 0.5rem; font-size: 1.1rem;}
.stTab > div > div {padding: 1.5rem; border-radius: 10px;}
.metric {background-color: #4CAF50; color: white;}
</style>
""", unsafe_allow_html=True)

# Sidebar
lang = st.sidebar.selectbox(TRANSLATIONS['English']['language'], ['English', 'Gujarati', 'Hindi'])
t = TRANSLATIONS[lang]
temple = st.sidebar.selectbox(t['select_temple'], list(TEMPLE_DATA.keys()))
role = st.sidebar.selectbox(t['view_as'], [t['pilgrim_app'], t['authority_dashboard']])
st.sidebar.title(f"{t['title']} - {temple}")

st.sidebar.header("Demo Integrations")
if st.sidebar.button('Sim Surge: #1 → #2 (Limit Slots)'):
    st.session_state.surge_active = True
    st.experimental_rerun()
if st.sidebar.button('Sim Crowded: #3 → #4 → #6 (Alert App)'):
    simulate_iot_activity(temple, ticks=6)
    a = detect_panic_from_stream(temple)
    if a:
        st.session_state.alerts.append(a)
    st.experimental_rerun()

if st.sidebar.button("Export Queues CSV"):
    qdf = pd.DataFrame(st.session_state.queue_data)
    href = download_bytes("queues.csv", qdf)
    st.sidebar.markdown(f"[Download Queues CSV]({href})", unsafe_allow_html=True)

st.title(f"{t['title']} - {temple}")

# ------------------------------
# Pilgrim View
# ------------------------------
if role == t['pilgrim_app']:
    tabs = st.tabs([t['home_info'], t['join_queue'], t['sos_nav'], t['surveillance'], t['traffic'], t['accessibility'], t['medical_map']])
    with tabs[0]:
        st.header(f"{t['temple_info_wait']} - {temple}")
        pred_df = predict_crowd(temple, 3, start_date=date.today())
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
            st.warning("🚨 Avoid area - High crowd detected! (#6 Push Sim)")

    with tabs[1]:
        st.header(f"{t['virtual_darshan']} - {temple}")
        st.info(t['dynamic_slots'])
        priority = st.checkbox(t['elderly_priority'])
        colA, colB = st.columns([3,1])
        with colA:
            name = st.text_input("Name (Optional)")
            phone = st.text_input("Phone (Optional)")
        with colB:
            if st.button(t['join_btn'], use_container_width=True):
                user_id = len(st.session_state.queue_data) + 1
                entry = issue_pass(temple, user_id, priority, lang)
                st.success(TRANSLATIONS[lang]['token_issued'].format(entry['est_wait'], entry['slot']))
                qr_text = get_token_text(entry)
                fig, ax = plt.subplots(figsize=(3.5,3.5))
                ax.text(0.5, 0.5, qr_text, ha='center', va='center', fontsize=9, wrap=True)
                ax.axis('off')
                st.pyplot(fig)
                href = download_bytes("pass.json", entry, mime='application/json')
                st.markdown(f"[Download Pass (JSON)]({href})", unsafe_allow_html=True)
        if st.button(t['simulate_turn']):
            st.balloons()
            st.success(t['your_turn'])

        # Live queue progress (complete)
        if st.session_state.queue_data:
            q_df = pd.DataFrame([q for q in st.session_state.queue_data if q['temple'] == temple])
            if not q_df.empty:
                for idx, row in q_df.iterrows():
                    join_time = datetime.fromisoformat(row['join_time'])
                    elapsed = max(0, (datetime.now() - join_time).total_seconds()/60.0)
                    est = max(1, row['est_wait'])
                    progress_pct = int(min(100, (elapsed / est) * 100))
                    st.progress(progress_pct/100)
                    wait_left = max(0, int(row['est_wait'] - elapsed))
                    # If wait elapsed, update status
                    if elapsed >= est and row.get('status') != 'Completed':
                        # mark as completed and notify
                        row_index_in_state = None
                        for i, q in enumerate(st.session_state.queue_data):
                            if q['pass_id'] == row['pass_id']:
                                row_index_in_state = i
                                break
                        if row_index_in_state is not None:
                            st.session_state.queue_data[row_index_in_state]['status'] = 'Completed'
                            st.session_state.queue_data[row_index_in_state]['est_wait'] = 0
                            st.toast = None
                        st.success(f"{TRANSLATIONS[lang]['your_turn']} (Pass {row['pass_id']})")
                    st.metric("Wait Left", f"{wait_left} min", f"Slot: {row['slot']}")
        # download temple queue
        qdf_t = pd.DataFrame([q for q in st.session_state.queue_data if q['temple'] == temple])
        if not qdf_t.empty:
            href = download_bytes("queue_temple.csv", qdf_t)
            st.markdown(f"[Download {temple} Queue CSV]({href})", unsafe_allow_html=True)

    with tabs[2]:
        st.header(f"{t['emergency_sos']} - {temple}")
        if st.button(t['press_sos'], type="primary"):
            alert = {
                'type': 'SOS Pressed',
                'location': 'User-Reported',
                'temple': temple,
                'time': datetime.now().isoformat(),
                'severity': 'Critical'
            }
            st.session_state.alerts.append(alert)
            st.session_state.drone_dispatched = True
            st.success(t['sos_sent'])
            st.success(t['drone_dispatch'])
            folium_static(create_map(temple, 'drone'))
            eta = np.random.randint(3, 12)
            st.info(f"Responders ETA: {eta} mins")
            dispatch = {'type': 'Dispatch', 'temple': temple, 'time': datetime.now().isoformat(), 'eta_min': eta}
            st.session_state.alerts.append(dispatch)
            href = download_bytes("alert.json", alert, mime='application/json')
            st.markdown(f"[Download Alert (JSON)]({href})", unsafe_allow_html=True)

    with tabs[3]:
        st.header(f"{t['surveillance']} - {temple}")
        if st.button(t['scan_now']):
            reading = simulate_iot_activity(temple, ticks=4)
            alert = detect_panic_from_stream(temple)
            fig, ax = plt.subplots(figsize=(6,5))
            vals = [reading['density'], 1-reading['density']]
            labels = [t['crowded'], t['safe']]
            ax.pie(vals, labels=labels, autopct='%1.1f%%')
            ax.set_title('CCTV Density (#3)')
            st.pyplot(fig)
            st.metric("Sensors", f"{reading['density']*100:.0f}%", "IoT")
            st.metric("Drones", "Active" if st.session_state.drone_dispatched else "Idle", "AI Analytics")
            if alert:
                st.error(TRANSLATIONS[lang]['panic_detected'].format(alert['location']))
                st.session_state.crowd_alert_sent = True
        recent = [r for r in st.session_state.iot_state['sensor_stream'] if r['temple'] == temple]
        if recent:
            sensor_df = pd.DataFrame(recent[-10:])
            st.dataframe(sensor_df[['timestamp','density']])

    with tabs[4]:
        st.header(f"{t['parking_mobility']} - {temple}")
        folium_static(create_map(temple, 'parking'))
        data = TEMPLE_DATA[temple]
        capacity = max(2, int(data['base_footfall']//5000))
        occupancy = np.random.randint(0, capacity+1)
        empty_spots = capacity - occupancy
        st.info(t['empty_spots'].format(empty_spots))
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

    with tabs[5]:
        st.header(f"{t['voice_nav']} - {temple}")
        if st.button('Start Voice-Guided Mode (#7)'):
            st.info(t['audio_sim'])
            st.audio("data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcDbiIAA==", format="audio/wav")
        st.info("AR Navigation Sim: Priority route highlighted for disabled.")
        if st.button("Request Volunteer Assistance (Priority)"):
            st.success("Volunteer Assigned. ETA 4 mins.")

    with tabs[6]:
        st.header(f"{t['medical_map']} - {temple}")
        folium_static(create_map(temple, 'medical'))
        st.info("Nearest Aid: 200m - Mapped for Quick Response.")

# ------------------------------
# Authority Dashboard
# ------------------------------
elif role == t['authority_dashboard']:
    tabs = st.tabs([t['prediction'], t['surveillance'], t['active_queues'], t['barricades'], t['traffic'], 'Engagement (#6)', t['accessibility']])
    with tabs[0]:
        st.header(f"{t['prediction']} - {temple}")
        pred_df = predict_crowd(temple, 7, start_date=date.today())
        if not pred_df.empty:
            st.dataframe(pred_df.style.background_gradient(cmap='YlOrRd'))
            fig, ax = plt.subplots(figsize=(10,4))
            ax.bar([d.strftime('%Y-%m-%d') for d in pred_df['date']], pred_df['predicted_footfall'])
            ax.set_title(f'Surge Forecast - {temple} (#1: Historical/Weather/Holidays/Festivals)')
            plt.xticks(rotation=45)
            st.pyplot(fig)
            high_surge = pred_df[pred_df['predicted_footfall'] > TEMPLE_DATA[temple]['base_footfall'] * 2]
            if not high_surge.empty:
                st.warning(t['surge_alert'])
                st.session_state.surge_active = True
        model, features = get_model(temple)
        importances = model.feature_importances_
        fi_df = pd.DataFrame({'feature': features, 'importance': importances}).sort_values('importance', ascending=False)
        st.subheader("Model Feature Importance")
        st.dataframe(fi_df)

    with tabs[1]:
        st.header(f"{t['surveillance']} - {temple}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t['scan_now'], use_container_width=True):
                reading = simulate_iot_activity(temple, ticks=6)
                alert = detect_panic_from_stream(temple)
                fig, ax = plt.subplots()
                ax.pie([reading['density'], 1-reading['density']], labels=[t['crowded'], t['safe']], autopct='%1.1f%%')
                st.pyplot(fig)
                if alert:
                    st.error(TRANSLATIONS[lang]['panic_detected'].format(alert['location']))
        with col2:
            last = [r for r in st.session_state.iot_state['sensor_stream'] if r['temple'] == temple]
            dens = last[-1]['density'] if last else 0.0
            st.metric("IoT Sensors", f"{dens*100:.0f}% Density")
            st.metric("CCTV Feeds", "Live", "AI Analytics")
            st.metric("Drones", "4/5 Deployed", "Auto Patrol")

        # CCTV Mock Feed inside Surveillance tab
        st.subheader("CCTV Mock Feed (Streamlit)")
        c1, c2 = st.columns([3,1])
        with c2:
            st.write("CCTV Controls")
            source_option = st.radio("Source", ("Webcam (0)", "Sample Video (file)"), index=1 if not OPENCV_AVAILABLE else 0)
            if source_option == "Webcam (0)":
                source_val = 0
            else:
                uploaded = st.file_uploader("Upload video file (mp4/mov)", type=['mp4','mov','avi'])
                source_val = uploaded if uploaded is not None else "sample_video"
            # Start/Stop CCTV
            if st.button("Start CCTV Feed"):
                if OPENCV_AVAILABLE:
                    # if user uploaded file, create a temporary path
                    if isinstance(source_val, str) and source_val == "sample_video":
                        # fallback to built-in sample: attempt to open packaged sample or show warning
                        st.warning("No sample video provided. Upload a video file to stream, or ensure OpenCV + webcam available.")
                        start_cctv(0)
                    elif hasattr(source_val, "read"):
                        # write uploaded to temp file
                        tfile = f"/tmp/{uuid.uuid4().hex}.mp4"
                        with open(tfile, "wb") as f:
                            f.write(source_val.read())
                        start_cctv(tfile)
                    else:
                        start_cctv(source_val)
                else:
                    st.warning("OpenCV not installed - cannot start CCTV.")
            if st.button("Stop CCTV Feed"):
                stop_cctv()

        # display area column
        with c1:
            img_placeholder = st.empty()
            # If CCTV running, stream a few frames (non-blocking-ish)
            if st.session_state.cctv.get('running'):
                # stream for a limited number of frames per rerun to avoid blocking
                for _ in range(5):
                    ok = stream_cctv_frame(img_placeholder, fps=8)
                    if not ok:
                        break
                    time.sleep(0.12)
            else:
                # show last captured frame or a placeholder
                if OPENCV_AVAILABLE:
                    img_placeholder.image(np.zeros((480, 640, 3), dtype=np.uint8), caption="CCTV Idle", channels="BGR")
                else:
                    st.info("OpenCV not available. Install opencv-python to enable CCTV mock feed.")

        # recent alerts
        a_df = pd.DataFrame([a for a in st.session_state.alerts if a.get('temple') == temple])
        if not a_df.empty:
            st.subheader("Recent Alerts")
            st.dataframe(a_df)

    with tabs[2]:
        st.header(f"{t['active_queues']} - {temple}")
        q_df = pd.DataFrame([q for q in st.session_state.queue_data if q.get('temple') == temple])
        if not q_df.empty:
            st.dataframe(q_df)
            sel = st.multiselect("Select Pass IDs to Prioritize/Cancel", q_df['pass_id'].tolist())
            if st.button("Grant Priority"):
                for pid in sel:
                    for q in st.session_state.queue_data:
                        if q['pass_id'] == pid:
                            q['priority'] = True
                st.success("Priority Granted.")
            if st.button("Cancel Selected"):
                st.session_state.queue_data = [q for q in st.session_state.queue_data if q['pass_id'] not in sel]
                st.success("Selected passes cancelled.")
            if st.button("Export Active Queue CSV"):
                href = download_bytes("active_queue.csv", q_df)
                st.markdown(f"[Download Active Queue CSV]({href})", unsafe_allow_html=True)
        else:
            st.info("No active passes.")

    with tabs[3]:
        st.header(f"{t['barricades']} - {temple}")
        surge_threshold = TEMPLE_DATA[temple]['base_footfall'] * 2
        pred = predict_crowd(temple, 3, start_date=date.today())
        next_high = pred[pred['predicted_footfall'] > surge_threshold]
        if not next_high.empty or st.session_state.surge_active:
            statuses = {'Main Gate': 'Locked (High Surge)', 'Darshan Hall': 'Reduced Capacity', 'Exit': 'Active'}
        else:
            statuses = {'Main Gate': 'Open', 'Darshan Hall': 'Open', 'Exit': 'Active'}
        for loc, stat in statuses.items():
            st.metric(loc, stat, delta=f"AI-Enabled (#4)")

    with tabs[4]:
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
        if st.button("Activate Dynamic Reroute"):
            st.success("Dynamic reroute activated; police notified.")

    with tabs[5]:
        st.header(f"Pilgrim Engagement () - {temple}")
        col1, col2, col3 = st.columns(3)
        q_df_t = pd.DataFrame([q for q in st.session_state.queue_data if q.get('temple') == temple])
        col1.metric("Wait Times", f"{np.mean(q_df_t['est_wait']):.0f} min Avg" if not q_df_t.empty else "N/A")
        col2.metric("Notifications Sent", int(st.session_state.crowd_alert_sent) + int(st.session_state.surge_active))
        col3.metric("Active Pilgrims", len(q_df_t))
        st.info(f"{t['temple_timings']} | {t['routes']} | {t['facilities']} | {t['emergency_contacts']}")

    with tabs[6]:
        st.header(f"{t['accessibility']} - {temple}")
        st.checkbox("Enable Priority Queues ()")
        if st.button("Broadcast Voice Nav"):
            st.success("Voice Guide Sent to All Devices ()")
            st.info(t['audio_sim'])

st.markdown("---")
st.caption(t['footer'])

# Cleanup on script end if CCTV was started
def _cleanup():
    if st.session_state.cctv.get('cap') is not None:
        try:
            st.session_state.cctv['cap'].release()
        except Exception:
            pass

# Ensure cleanup when script finishes (best-effort)
_cleanup()

