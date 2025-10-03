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
# Fix: Define English first, then copy for others
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
        'traffic_flow': 'डायनामिक ट्रैफिक (#5)'
    }
}
# Session State for persistence
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

# Step 1: AI Crowd Prediction Model (#1) - Updated with 2025 data
@st.cache_data
def load_and_train_model():
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', end='2026-01-01', freq='D')  # Extended for 2025
    n = len(dates)
    base_footfall = 50000  # Updated from Somnath stats: >50K daily
    # Key 2025 Gujarat festivals for Somnath peaks
    festivals = ['2025-01-14', '2025-02-26', '2025-10-20', '2025-11-15', '2025-09-29', '2025-10-07']  # Uttarayan, Shivratri, Diwali, Kartik Purnima, Navratri
    is_festival = [1 if d.strftime('%Y-%m-%d') in festivals else 0 for d in dates]
    temp = np.random.normal(28, 5, n).clip(15, 40)
    is_holiday = [(d.weekday() >= 5) or isf for d, isf in zip(dates, is_festival)]
    festival_boost = np.array(is_festival) * 50000  # Peaks to 100K+
    holiday_boost = np.array(is_holiday) * 10000
    weather_factor = (30 - temp) / 10
    noise = np.random.normal(0, 5000, n)
    footfall = (base_footfall + festival_boost + holiday_boost + weather_factor * 5000 + noise).clip(0, 150000)
    
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

model, features, historical_df = load_and_train_model()

def predict_crowd(days_ahead=7):
    try:
        future_dates = pd.date_range(start=datetime.now().date(), periods=days_ahead, freq='D')
        future_n = len(future_dates)
        future_temp = np.random.normal(28, 5, future_n).clip(15, 40)  # TODO: Replace with OpenWeather API
        future_fest = [1 if d.strftime('%Y-%m-%d') in ['2025-10-20', '2025-11-01', '2025-11-15'] else 0 for d in future_dates]  # Upcoming
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

# Step 2: Smart Queue System (#2, #7 - Priority for elderly)
queue_data = []  # Simulated queue: [{'user_id': 1, 'join_time': ts, 'priority': False, 'lang': 'en', 'slot': '10:00'}]

def join_queue(user_id, priority=False, lang='English'):
    now = datetime.now()
    pred_df = predict_crowd(1)
    surge_penalty = 30 if (not pred_df.empty and pred_df['predicted_footfall'].iloc[0] > 100000) else 0  # Auto-cap on surge (#1 integration)
    base_wait = np.random.randint(30, 120)
    est_wait = base_wait + (0 if priority else 15) - surge_penalty  # Priority reduces wait
    slot = (now + timedelta(minutes=est_wait)).strftime('%H:%M')
    entry = {'user_id': user_id, 'join_time': now, 'priority': priority, 'lang': lang, 'slot': slot, 'status': 'Waiting', 'est_wait': est_wait}
    queue_data.append(entry)
    return TRANSLATIONS[lang]['token_issued'].format(est_wait, slot)

# Step 3: Surveillance & Emergency (#3, #4)
alerts = []  # [{'type': 'panic', 'location': 'Main Gate', 'time': ts, 'severity': 'High'}]

def simulate_monitoring():
    density = np.random.uniform(0.3, 0.9)
    if density > 0.8:
        if np.random.choice([True, False], p=[0.3, 0.7]):
            alert = {'type': 'Panic Detected', 'location': np.random.choice(['Main Gate', 'Darshan Hall', 'Parking']), 'time': datetime.now(), 'severity': 'High'}
            alerts.append(alert)
            return alert, density
    return None, density

# Step 4: Traffic Map (#5) - Folium; fallback plot if not installed
def create_parking_map():
    try:
        m = folium.Map(location=[20.8869, 70.3907], zoom_start=15)  # Somnath
        spots = [(20.887, 70.391), (20.886, 70.390)]  # Simulated empty spots
        for spot in spots:
            folium.Marker(spot, popup="Empty Parking", icon=folium.Icon(color='green')).add_to(m)
        folium.Marker([20.8869, 70.3907], popup="Temple").add_to(m)
        return m
    except:
        # Fallback matplotlib plot
        fig, ax = plt.subplots()
        ax.scatter([70.391, 70.390], [20.887, 20.886], c='green', marker='o', s=100)
        ax.scatter(70.3907, 20.8869, c='red', marker='^', s=100)
        ax.set_title('Parking Map (Fallback)')
        ax.set_xlabel('Lon'); ax.set_ylabel('Lat')
        st.pyplot(fig)
        return None

# Streamlit App
st.set_page_config(page_title="Yatra Sevak v2", layout="wide")

# Sidebar
lang = st.sidebar.selectbox(TRANSLATIONS['English']['language'], ['English', 'Gujarati', 'Hindi'])
t = TRANSLATIONS[lang]
role = st.sidebar.selectbox(t['view_as'], [t['pilgrim_app'], t['authority_dashboard']])
st.sidebar.title(t['title'])

if role == t['pilgrim_app']:
    tab1, tab2, tab3 = st.tabs([t['home_info'], t['join_queue'], t['sos_nav']])
    
    with tab1:
        st.header(t['temple_info_wait'])
        pred_df = predict_crowd(3)
        if not pred_df.empty:
            st.dataframe(pred_df[['date', 'predicted_footfall']].rename(columns={'predicted_footfall': t['predicted_crowd']}))
        st.info(t['current_weather'])
        folium_static(create_parking_map())  # Traffic/Parking (#5)
    
    with tab2:
        st.header(t['virtual_darshan'])
        priority = st.checkbox(t['elderly_priority'])
        if st.button(t['join_btn']):
            user_id = len(queue_data) + 1
            msg = join_queue(user_id, priority, lang)
            st.success(t['msg'], lang)
        if st.button(t['simulate_turn']):
            st.balloons()
            st.success(t['your_turn'])
    
    with tab3:
        st.header(t['emergency_sos'])
        if st.button(t['press_sos']):
            st.error(t['sos_sent'])
            # Voice sim for accessibility
            st.info(t['audio_sim'])
        st.header(t['voice_guide'])
        if st.button(t['voice_guide']):
            st.info(t['audio_sim'])

elif role == t['authority_dashboard']:
    tab1, tab2, tab3, tab4 = st.tabs([t['prediction'], t['surveillance'], t['queue_alerts'], t['traffic']])
    
    with tab1:
        st.header(t['prediction'])
        pred_df = predict_crowd(7)
        if not pred_df.empty:
            st.dataframe(pred_df)
            fig, ax = plt.subplots()
            ax.bar([d.strftime('%Y-%m-%d') for d in pred_df['date']], pred_df['predicted_footfall'])
            ax.set_title(t['predicted_crowd'] + ' (Next 7 Days)')
            plt.xticks(rotation=45)
            st.pyplot(fig)
            high_surge = pred_df[pred_df['predicted_footfall'] > 100000]
            if not high_surge.empty:
                st.warning(t['surge_alert'].format(high_surge['date'].iloc[0].strftime('%Y-%m-%d')))
    
    with tab2:
        st.header(t['surveillance'])
        if st.button(t['scan_now']):
            alert, density = simulate_monitoring()
            fig, ax = plt.subplots()
            ax.pie([density, 1-density], labels=[t['crowded'], t['safe']], autopct='%1.1f%%')
            st.pyplot(fig)
            if alert:
                st.error(t['panic_detected'].format(alert['type'], alert['location'], alert['severity']))
    
    with tab3:
        st.header(t['active_queues'])
        if queue_data:
            q_df = pd.DataFrame(queue_data)
            st.dataframe(q_df)
        if alerts:
            a_df = pd.DataFrame(alerts)
            st.dataframe(a_df)
            if st.button(t['dispatch']):
                st.success(t['dispatched'])
        else:
            st.info(t['no_alerts'])
    
    with tab4:
        st.header(t['parking_mobility'])
        folium_static(create_parking_map())
        st.info(t['empty_spots'])

st.markdown("---")
st.caption(t['footer'])
