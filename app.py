import streamlit as st
import time
import random
import pandas as pd

st.set_page_config(
   
    page_title="Smart Irrigation System | Simulation",
    page_icon="🌱",
    layout="wide"
)
st.image("banner.png", use_container_width=True)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap" rel="stylesheet">
<style>
    html, body, [class*="st-"], .main {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }

    [data-testid="stMarkdownContainer"] p, 
    [data-testid="stMarkdownContainer"] h1, 
    [data-testid="stMarkdownContainer"] h2, 
    [data-testid="stMarkdownContainer"] h3,
    .stApp div {
        white-space: normal !important;
        word-break: keep-all !important;
        overflow-wrap: break-word !important;
    }

    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        text-align: right !important;
        justify-content: flex-start !important;
    }
</style>
""", unsafe_allow_html=True)




</style>
""", unsafe_allow_html=True)
    html, body, [class*="css"]  {
        direction: rtl;
        text-align: right;
    }
    .stMetric label, .stMetric div {
        direction: rtl;
        text-align: right;
    }
    section[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

if "zones" not in st.session_state:
    st.session_state.zones = {}
if "history" not in st.session_state:
    st.session_state.history = []

st.title(" لوحة تحكم ومحاكي نظام الري الذكي التفاعلي")
st.caption("نظام محاكاة و تخطيط مرن يتيح لك تحديد عدد القطاعات و المسافات و المحاصيل بحرية")

st.sidebar.header(" إعداد المزرعة و القطاعات")

num_zones = st.sidebar.number_input("عدد القطاعات في المزرعة", min_value=1, max_value=12, value=3, step=1)

temp_zones = {}
with st.sidebar.expander("تخصيص بيانات القطاعات و المسافات", expanded=True):
    for i in range(int(num_zones)):
        st.markdown(f"القطاع {i+1}")
        z_crop = st.text_input(f"نوع المحصول", value=f"محصول {i+1}", key=f"crop_{i}")
        z_dist = st.number_input(f"المسافة عن المركز (متر)", min_value=10, max_value=1000, value=(i+1)*50, step=10, key=f"dist_{i}")
        
        zone_key = f"القطاع {i+1} ({z_crop})"
        existing_data = st.session_state.zones.get(zone_key, {})
        temp_zones[zone_key] = {
            "crop": z_crop,
            "distance": z_dist,
            "moisture": existing_data.get("moisture", random.uniform(20.0, 50.0)),
            "ph": existing_data.get("ph", round(random.uniform(6.0, 7.2), 2)),
            "valve": existing_data.get("valve", False),
            "water_used": existing_data.get("water_used", 0)
        }

if st.sidebar.button("تطبيق و بناء المزرعة"):
    st.session_state.zones = temp_zones
    st.session_state.history = []
    st.rerun()

if not st.session_state.zones:
    st.session_state.zones = temp_zones

st.sidebar.markdown("---")
st.sidebar.subheader(" حدود الري و التحكم")

min_threshold = st.sidebar.slider("الحد الأدنى للرطوبة (تشغيل الري %)", 10, 40, 30)
max_threshold = st.sidebar.slider("الحد الأعلى للرطوبة (إيقاف الري %)", 60, 90, 75)

auto_simulate = st.sidebar.checkbox("تشغيل المحاكاة التلقائية الحية", value=False)
tick_button = st.sidebar.button("خطوة محاكاة واحدة")

def run_simulation_step():
    for zone_name, data in st.session_state.zones.items():
        if data["moisture"] < min_threshold:
            data["valve"] = True
        elif data["moisture"] >= max_threshold:
            data["valve"] = False

        if data["valve"]:
            data["moisture"] += random.uniform(3.0, 6.0)
            data["moisture"] = min(data["moisture"], 100.0)
            consumption_factor = max(1.0, data["distance"] / 50.0)
            data["water_used"] += int(random.randint(10, 25) * consumption_factor)
        else:
            data["moisture"] -= random.uniform(1.0, 2.5)
            data["moisture"] = max(data["moisture"], 0.0)

        data["ph"] = round(data["ph"] + random.uniform(-0.02, 0.02), 2)

    timestamp = time.strftime("%H:%M:%S")
    for z_name, z_data in st.session_state.zones.items():
        st.session_state.history.append({
            "Time": timestamp,
            "Zone": z_name,
            "Moisture": round(z_data["moisture"], 1),
            "Valve": 1 if z_data["valve"] else 0
        })

if tick_button or auto_simulate:
    run_simulation_step()

col1, col2, col3, col4 = st.columns(4)

total_active_valves = sum(1 for z in st.session_state.zones.values() if z["valve"])
avg_moisture = sum(z["moisture"] for z in st.session_state.zones.values()) / max(1, len(st.session_state.zones))
total_water = sum(z["water_used"] for z in st.session_state.zones.values())
with col1:
    st.metric("إجمالي القطاعات", len(st.session_state.zones))
with col2:
    st.metric("الصمامات المفتوحة حاليًا", f"{total_active_valves} / {len(st.session_state.zones)}")
with col3:
    st.metric("متوسط رطوبة المزرعة", f"{avg_moisture:.1f}%")
with col4:
    st.metric("إجمالي المياه المستهلكة", f"{total_water} لتر")

st.markdown("---")

st.subheader("حالة القطاعات المباشرة")
zone_items = list(st.session_state.zones.items())
num_cols = 3 if len(zone_items) >= 3 else max(1, len(zone_items))

for i in range(0, len(zone_items), num_cols):
    cols = st.columns(num_cols)
    for j in range(num_cols):
        if i + j < len(zone_items):
            zone_name, data = zone_items[i + j]
            with cols[j]:
                st.markdown(f"### {zone_name}")
                st.caption(f" المسافة عن المركز: {data['distance']} متر")
                if data["valve"]:
                    st.success("جاري الري (الصمام مفتوح)")
                elif data["moisture"] < min_threshold:
                    st.warning(" تربة جافة - تنتظر الري")
                else:
                    st.info(" حالة رطوبة ممتازة")

                st.metric("رطوبة التربة", f"{data['moisture']:.1f}%")
                st.progress(int(data["moisture"]) / 100)
                st.metric("حموضة التربة (pH)", f"{data['ph']}")
                st.caption(f"استهلاك المياه: {data['water_used']} لتر")

st.markdown("---")

col_chart, col_alerts = st.columns([2, 1])

with col_chart:
    st.subheader("حركة الرطوبة عبر الوقت")
    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        st.line_chart(df, x="Time", y="Moisture", color="Zone")
    else:
        st.info("اضغط على 'خطوة محاكاة واحدة' أو فعّل 'المحاكاة التلقائية' لتشغيل المحاكي.")

with col_alerts:
    st.subheader("نظام التنبيهات الذكي")
    alerts_found = False
    for zone_name, data in st.session_state.zones.items():
        if data["ph"] < 6.0 or data["ph"] > 7.2:
            st.error(f" تنبيه pH في {zone_name}: القراءة ({data['ph']}) غير مثالية للنبات!")
            alerts_found = True
        if data["moisture"] < 15.0:
            st.error(f"جفاف شديد في {zone_name}! الرطوبة: {data['moisture']:.1f}%")
            alerts_found = True
            
    if not alerts_found:
        st.success("جميع المؤشرات ضمن الحدود الآمنة.")

if auto_simulate:
    time.sleep(1.5)
    st.rerun()
