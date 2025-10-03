import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
from sklearn.model_selection import train_test_split

# Hardcoded Multilingual Support (No external libs needed)
TRANSLATIONS = {
    'English': {
        'title': '🛕 Yatra Sevak: Smart Pilgrimage Management',
        'home_info': 'Home & Temple Info',
        'join_queue': 'Join Virtual Queue',
        'sos_nav': 'Emergency SOS & Navigation',
        'prediction': 'AI Crowd Prediction (#1)',
        'surveillance': 'Live Surveillance (#3)',
        'queue_alerts': 'Queues & Alerts (#2, #4)',
        'traffic': 'Traffic & Parking (#5)',
        'pilgrim_app': 'Pilgrim App',
        'authority_dashboard': 'Authority Dashboard',
        'language': 'Language / ભાષા / भाषा',
        'view_as': 'View As',
        'temple_info_wait': 'Temple Info & Wait Times',
        'current_weather': 'Current Weather: 28°C (Simulated). Routes: Use map below.',
        'virtual_darshan': 'Virtual Darshan Queue',
        'elderly_priority': 'Elderly/Disabled Priority (#7)',
        'join_btn': 'Join Queue',
        'simulate_turn': 'Simulate Your Turn',
        'token_issued': 'Token issued! Est. wait: {} mins. Your slot: {}. Alert when ready.',
        'your_turn': 'Your slot is now! Proceed to entry.',
        'emergency_sos': 'Emergency SOS (#4)',
        'press_sos': '🚨 Press SOS',
        'sos_sent': 'Alert sent! Help en route. Location shared.',
        'voice_guide': 'Voice Guide to Parking',
        'audio_sim': "Audio Guide: 'Turn left in 50m to priority parking.'",
        'surge_alert': 'Surge Alert: Cap queues for {}',
        'scan_now': 'Scan Now',
        'crowded': 'Crowded',
        'safe': 'Safe',
        'panic_detected': '🚨 {} at {}! Severity: {}',
        'active_queues': 'Active Queues & SOS Alerts',
        'no_alerts': 'No active alerts.',
        'dispatch': 'Dispatch Response',
        'dispatched': 'Medical/Police dispatched!',
        'parking_mobility': 'Parking & Mobility',
        'empty_spots': 'Empty spots: 2/10. Integrate with police for shuttles.',
        'footer': 'Scalable to Dwarka/Ambaji. Built with ❤️ for Gujarat\'s heritage.',
        'predicted_crowd': 'Predicted Crowd'
    },
    'Gujarati': {
        'title': '🛕 યાત્રા સેવક: સ્માર્ટ તીર્થયાત્રા વ્યવસ્થાપન',
        'home_info': 'ઘર અને મંદિર માહિતી',
        'join_queue': 'વર્ચ્યુઅલ કતારમાં જોડાઓ',
        'sos_nav': 'ઇમરજન્સી SOS અને નેવિગેશન',
        'prediction': 'AI ભીડ અનુમાન (#1)',
        'surveillance': 'લાઇવ સર્વેલન્સ (#3)',
        'queue_alerts': 'કતારો અને એલર્ટ્સ (#2, #4)',
        'traffic': 'ટ્રાફિક અને પાર્કિંગ (#5)',
        'pilgrim_app': 'તીર્થયાત્રી એપ',
        'authority_dashboard': 'અધિકારી ડેશબોર્ડ',
        'language': 'ભાષા / ભાષા / भाषा',
        'view_as': 'જોવા માટે',
        'temple_info_wait': 'મંદિર માહિતી અને વેઇટ ટાઇમ્સ',
        'current_weather': 'વર્તમાન હવામાન: 28°C (સિમ્યુલેટેડ). માર્ગો: નીચેના મેપનો ઉપયોગ કરો.',
        'virtual_darshan': 'વર્ચ્યુઅલ દર્શન કતાર',
        'elderly_priority': 'વૃદ્ધ/અપંગ પ્રાયોરિટી (#7)',
        'join_btn': 'કતારમાં જોડાઓ',
        'simulate_turn': 'તમારી વાર સિમ્યુલેટ કરો',
        'token_issued': 'ટોકન જારી! અંદાજિત વાટ જુઓ: {} મિનિટ. તમારી સ્લોટ: {}. તૈયાર હોય ત્યારે એલર્ટ.',
        'your_turn': 'તમારી સ્લોટ હવે છે! એન્ટ્રી તરફ આગળ વધો.',
        'emergency_sos': 'ઇમરજન્સી SOS (#4)',
        'press_sos': '🚨 SOS દબાવો',
        'sos_sent': 'એલર્ટ મોકલાયું! મદદ રસ્તે છે. સ્થાન શેર કર્યું.',
        'voice_guide': 'પાર્કિંગ માટે વૉઇસ ગાઇડ',
        'audio_sim': "ઓડિયો ગાઇડ: '50mમાં ડાબી તરફ વળો પ્રાયોરિટી પાર્કિંગ તરફ.'",
        'surge_alert': 'સર્જ અલર્ટ: {} માટે કતારો મર્યાદિત કરો',
        'scan_now': 'હવે સ્કેન કરો',
        'crowded': 'ભીડભાડ',
        'safe': 'સુરક્ષિત',
        'panic_detected': '🚨 {} ની {} પર! તીવ્રતા: {}',
        'active_queues': 'સક્રિય કતારો અને SOS એલર્ટ્સ',
        'no_alerts': 'કોઈ સક્રિય એલર્ટ્સ નથી.',
        'dispatch': 'રિસ્પોન્સ મોકલો',
        'dispatched': 'મેડિકલ/પોલીસ મોકલાયું!',
        'parking_mobility': 'પાર્કિંગ અને મોબિલિટી',
        'empty_spots': 'ખાલી જગ્યાઓ: 2/10. શટલ્સ માટે પોલીસ સાથે એકીકૃત કરો.',
        'footer': 'દ્વારકા/અંબાજી સુધી વિસ્તરણીય. ગુજરાતની વારસાને માટે ❤️ સાથે બનાવ્યું.',
        'predicted_crowd': 'અનુમાનિત ભીડ'
    },
    'Hindi': {
        'title': '🛕 यात्रा सेवक: स्मार्ट तीर्थयात्रा प्रबंधन',
        'home_info': 'घर और मंदिर जानकारी',
        'join_queue': 'वर्चुअल कतार में शामिल हों',
        'sos_nav': 'आपातकालीन SOS और नेविगेशन',
        'prediction': 'AI भीड़ पूर्वानुमान (#1)',
        'surveillance': 'लाइव निगरानी (#3)',
        'queue_alerts': 'कतारें और अलर्ट (#2, #4)',
        'traffic': 'ट्रैफिक और पार्किंग (#5)',
        'pilgrim_app': 'तीर्थयात्री ऐप',
        'authority_dashboard': 'प्राधिकरण डैशबोर्ड',
        'language': 'भाषा / ભાષા / भाषा',
        'view_as': 'देखें के रूप में',
        'temple_info_wait': 'मंदिर जानकारी और वेट टाइम्स',
        'current_weather': 'वर्तमान मौसम: 28°C (सिमुलेटेड). रूट: नीचे मैप का उपयोग करें.',
        'virtual_darshan': 'वर्चुअल दर्शन कतार',
        'elderly_priority': 'वृद्ध/अपंग प्राथमिकता (#7)',
        'join_btn': 'कतार में शामिल हों',
        'simulate_turn': 'अपनी बारी सिमुलेट करें',
        'token_issued': 'टोकन जारी! अनुमानित प्रतीक्षा: {} मिनट. आपकी स्लॉट: {}. तैयार होने पर अलर्ट.',
        'your_turn': 'आपकी स्लॉट अब है! एंट्री की ओर बढ़ें.',
        'emergency_sos': 'आपातकालीन SOS (#4)',
        'press_sos': '🚨 SOS दबाएं',
        'sos_sent': 'अलर्ट भेजा गया! मदद रास्ते में। स्थान साझा किया।',
        'voice_guide': 'पार्किंग के लिए वॉइस गाइड',
        'audio_sim': "ऑडियो गाइड: '50m में बाएं मुड़ें प्राथमिकता पार्किंग की ओर।'",
        'surge_alert': 'सर्ज अलर्ट: {} के लिए कतारें सीमित करें',
        'scan_now': 'अभी स्कैन करें',
        'crowded': 'भीड़भाड़',
        'safe': 'सुरक्षित',
        'panic_detected': '🚨 {} पर {}! गंभीरता: {}',
        'active_queues': 'सक्रिय कतारें और SOS अलर्ट',
        'no_alerts': 'कोई सक्रिय अलर्ट नहीं।',
        'dispatch': 'प्रतिक्रिया भेजें',
        'dispatched': 'मेडिकल/पुलिस भेजा गया!',
        'parking_mobility': 'पार्किंग और गतिशीलता',
        'empty_spots': 'खाली स्थान: 2/10. शटल के लिए पुलिस के साथ एकीकृत करें।',
        'footer': 'द्वारका/अंबाजी तक स्केलेबल। गुजरात की विरासत के लिए ❤️ के साथ बनाया।',
        'predicted_crowd': 'अनुमानित भीड़'
    }
}

# Initialize session state for persistence
if 'queue_data' not in st.session_state:
    st.session_state.queue_data = []
if 'alerts' not in st.session_state:
    st.session_state.alerts = []

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
        today = date(2025, 10, 3)  # Fixed for Oct 3, 2025 demo (today); use date.today() for live
        future_dates = pd.date_range(start=today, periods=days_ahead, freq='D')
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

# Step 2: Smart Queue System (#2, #7)
def join_queue(user_id, priority=False, lang='English'):
    now = datetime.now()
    pred_df = predict_crowd(1)
    surge_penalty = 30 if (not pred_df.empty and pred_df['predicted_footfall'].iloc[0] > 100000) else 0  # Auto-cap on surge (#1 integration)
    base_wait = np.random.randint(30, 120)
    est_wait = base_wait + (0 if priority else 15) - surge_penalty  # Priority reduces wait
    slot = (now + timedelta(minutes=est_wait)).strftime('%H:%M')
    entry = {'user_id': user_id, 'join_time': now, 'priority': priority, 'lang': lang, 'slot': slot, 'status': 'Waiting', 'est_wait': est_wait}
    st.session_state.queue_data.append(entry)
    return TRANSLATIONS[lang]['token_issued'].format(est_wait, slot)

# Step 3: Surveillance & Emergency (#3, #4)
def simulate_monitoring():
    density = np.random.uniform(0.3, 0.9)
    if density > 0.8:
        if np.random.choice([True, False], p=[0.3, 0.7]):
            alert = {'type': 'Panic Detected', 'location': np.random.choice(['Main Gate', 'Darshan Hall', 'Parking']), 'time': datetime.now(), 'severity': 'High'}
            st.session_state.alerts.append(alert)
            return alert, density
    return None, density

# Step 4: Traffic Map (#5) - Folium; fallback plot if not installed
def create_parking_map():
    try:
        m = folium.Map(location=[20.8869, 70.3907], zoom_start=15)  # Somnath
        spots = [(20.887, 70.391), (20.886, 70.390)]  # Empty spots
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

# UI
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
        folium_static(create_parking_map())
    
    with tab2:
        st.header(t['virtual_darshan'])
        priority = st.checkbox(t['elderly_priority'])
        if st.button(t['join_btn']):
            user_id = len(st.session_state.queue_data) + 1
            msg = join_queue(user_id, priority, lang)
            st.success(msg)
        if st.button(t['simulate_turn']):
            st.balloons()
            st.success(t['your_turn'])
    
    with tab3:
        st.header(t['emergency_sos'])
        if st.button(t['press_sos']):
            st.error(t['sos_sent'])
            # Voice sim (#7)
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
        if st.session_state.queue_data:
            q_df = pd.DataFrame(st.session_state.queue_data)
            st.dataframe(q_df)
        if st.session_state.alerts:
            a_df = pd.DataFrame(st.session_state.alerts)
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
