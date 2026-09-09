import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import json
import urllib.request
import random
from datetime import datetime, timedelta

st.set_page_config(
    page_title="MOIL Smart Mining Hub",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════
# GLOBAL CSS — FIX KPI CLIPPING / PREMIUM POLISH
# ═══════════════════════════════════════════
st.markdown("""
<style>
/* ---- KPI / st.metric: eliminate "..." truncation, allow wrap ---- */
div[data-testid="stMetric"]{
    background:rgba(255,255,255,0.045);
    border:1px solid rgba(255,255,255,0.10);
    border-radius:12px;
    padding:14px 12px 12px 12px;
    min-height:104px;
}
div[data-testid="stMetric"] label,
div[data-testid="stMetricLabel"]{
    white-space:normal !important;
    overflow:visible !important;
    text-overflow:unset !important;
    font-size:12.5px !important;
    line-height:1.28 !important;
    opacity:0.92;
}
div[data-testid="stMetricLabel"] > div,
div[data-testid="stMetricLabel"] p{
    white-space:normal !important;
    overflow:visible !important;
    text-overflow:unset !important;
}
div[data-testid="stMetricValue"]{
    white-space:normal !important;
    overflow:visible !important;
    text-overflow:unset !important;
    font-size:19px !important;
    line-height:1.22 !important;
    word-break:break-word;
}
div[data-testid="stMetricDelta"]{
    white-space:normal !important;
    overflow:visible !important;
    font-size:12px !important;
}
/* Tabs a touch more spacious so headings don't collide */
button[data-baseweb="tab"]{ font-size:13.5px !important; }
/* Small caption note styling */
.moil-proto-note{
    font-size:11.5px;color:#9aa3af;background:rgba(255,255,255,0.03);
    border:1px dashed rgba(255,255,255,0.15);border-radius:8px;
    padding:8px 12px;margin:6px 0 14px 0;
}
.moil-legend-chip{display:inline-block;margin:2px 10px 2px 0;font-size:12px;color:#e6e6e6;}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# TRANSLATIONS
# ═══════════════════════════════════════════
TRANSLATIONS = {
    "🇬🇧 English": {
        "title": "⛏️ MOIL Smart Mining Hub",
        "subtitle": "AI/ML-based reserve mapping, shortfall prediction & corrective action platform.",
        "select_mine": "🏭 Select Mine", "select_year": "📅 Select Year",
        "all_mines": "All Mines", "all_years": "All Years",
        "avg_reserve": "Avg. Reserve Potential", "total_production": "Total Production (tons)",
        "high_risk": "High Risk Months", "avg_downtime": "Avg. Downtime (hrs)",
        "map_title": "🗺️ Geospatial & Reserve Map",
        "heatmap_tab": "🌡️ Manganese Heatmap", "map_3d_tab": "🌐 3D View",
        "swir_tab": "🔬 SWIR/Spectral", "sar_tab": "📡 SAR Radar",
        "borehole_tab": "🕳️ Boreholes",
        "afforestation_tab": "🌿 Vegetation", "weather_tab": "🌧️ Weather",
        "production_trend": "📈 Production Trend", "actual": "Actual", "predicted": "Predicted",
        "risk_dist": "⚠️ Risk Distribution", "alerts": "🚨 Active Alerts",
        "no_alerts": "✅ No active risks. Operations normal.",
        "fleet_title": "🚛 Fleet & Equipment Status",
        "compliance_title": "🌿 Environmental Compliance",
        "blending_title": "⚗️ Ore Grade Blending Recommendations",
        "simulator_title": "🧪 What-If Scenario Simulator",
        "ai_title": "🤖 AI Mine Manager Assistant",
        "ai_placeholder": "Ask me anything about your mines...",
        "voice_title": "🎙️ Voice Assistant",
        "raw_data": "📋 Raw Data Table",
        "notifications": "🔔 Alerts & Notifications",
        "high_prob": "High Probability", "mod_prob": "Moderate Probability", "low_prob": "Low Probability",
        "mine": "Mine", "year": "Year", "month": "Month",
        "reserve_score": "Reserve Score", "reserve_cat": "Reserve Category",
        "production": "Production (tons)", "pred_production": "Predicted Production",
        "shortfall": "Shortfall Risk", "recommendation": "Recommendation",
        "ndvi": "NDVI", "lst": "Temp (°C)", "soil": "Soil Moisture", "rainfall": "Rainfall (mm)",
        "downtime": "Downtime (hrs)", "blasting": "Blasting Delays",
        "soil_tab": "💧 Soil Moisture",
        "soil_title": "💧 Satellite Soil Moisture — Operational Safety Assessment",
        "soil_subtitle": "Based on NASA SMAP satellite data. Traffic-light system for instant mine operations decision-making.",
        "saturation_level": "Saturation Level",
        "status_optimal": "OPTIMAL — Dry Ground", "status_moderate": "MODERATE — Wet Benches", "status_high": "HIGH — Waterlogging Risk",
        "ops_safe": "✅ Safe for heavy haulage & blasting", "ops_monitor": "⚡ Monitor sump drainage closely", "ops_halt": "🚫 Halt heavy equipment haulage",
        "avg_label": "Avg", "latest_label": "Latest", "period_label": "Period",
        "trend_title": "📈 Soil Moisture — Historical Trend (Yearly/Monthly)",
        "trend_title_year": "📈 Soil Moisture — Monthly Trend for Selected Year",
        "chart_month_axis": "Month", "chart_sm_axis": "Soil Moisture Saturation (%)",
        "legend_low": "🟢 < 50% Saturation — Dry ground. Safe for all heavy vehicle haulage and blasting operations.",
        "legend_mod": "🟡 50–75% Saturation — Wet benches. Monitor sump drainage, restrict loaded dumper speeds.",
        "legend_high": "🔴 > 75% Saturation — High waterlogging risk. Halt heavy equipment. Pit slippage hazard.",
        "no_soil_data": "No soil moisture data available for this selection.",
    },
    "🇮🇳 हिंदी": {
        "title": "⛏️ MOIL स्मार्ट माइनिंग हब",
        "subtitle": "रिज़र्व मैपिंग, शॉर्टफॉल भविष्यवाणी और सुधारात्मक कार्रवाई के लिए AI/ML प्लेटफ़ॉर्म।",
        "select_mine": "🏭 खदान चुनें", "select_year": "📅 वर्ष चुनें",
        "all_mines": "सभी खदानें", "all_years": "सभी वर्ष",
        "avg_reserve": "औसत रिज़र्व क्षमता", "total_production": "कुल उत्पादन (टन)",
        "high_risk": "उच्च जोखिम माह", "avg_downtime": "औसत डाउनटाइम (घंटे)",
        "map_title": "🗺️ भूस्थानिक और रिज़र्व मानचित्र",
        "heatmap_tab": "🌡️ मैंगनीज हीटमैप", "map_3d_tab": "🌐 3D दृश्य",
        "swir_tab": "🔬 SWIR/स्पेक्ट्रल", "sar_tab": "📡 SAR राडार",
        "borehole_tab": "🕳️ बोरहोल",
        "afforestation_tab": "🌿 वनस्पति", "weather_tab": "🌧️ मौसम",
        "production_trend": "📈 उत्पादन प्रवृत्ति", "actual": "वास्तविक", "predicted": "अनुमानित",
        "risk_dist": "⚠️ जोखिम वितरण", "alerts": "🚨 सक्रिय अलर्ट",
        "no_alerts": "✅ कोई सक्रिय जोखिम नहीं।",
        "fleet_title": "🚛 बेड़ा और उपकरण स्थिति",
        "compliance_title": "🌿 पर्यावरण अनुपालन",
        "blending_title": "⚗️ अयस्क ग्रेड मिश्रण सिफारिशें",
        "simulator_title": "🧪 क्या-अगर परिदृश्य सिमुलेटर",
        "ai_title": "🤖 AI खदान प्रबंधक सहायक",
        "ai_placeholder": "खदानों के बारे में कुछ भी पूछें...",
        "voice_title": "🎙️ वॉइस असिस्टेंट",
        "raw_data": "📋 कच्चा डेटा तालिका",
        "notifications": "🔔 सूचनाएं और अलर्ट",
        "high_prob": "उच्च संभावना", "mod_prob": "मध्यम संभावना", "low_prob": "कम संभावना",
        "mine": "खदान", "year": "वर्ष", "month": "माह",
        "reserve_score": "रिज़र्व स्कोर", "reserve_cat": "रिज़र्व श्रेणी",
        "production": "उत्पादन (टन)", "pred_production": "अनुमानित उत्पादन",
        "shortfall": "शॉर्टफॉल जोखिम", "recommendation": "सिफारिश",
        "ndvi": "NDVI", "lst": "तापमान (°C)", "soil": "मृदा नमी", "rainfall": "वर्षा (मिमी)",
        "downtime": "डाउनटाइम (घंटे)", "blasting": "विस्फोट विलंब",
        "soil_tab": "💧 मृदा नमी",
        "soil_title": "💧 सैटेलाइट मृदा नमी — परिचालन सुरक्षा आकलन",
        "soil_subtitle": "NASA SMAP उपग्रह डेटा पर आधारित। खदान संचालन के त्वरित निर्णय के लिए ट्रैफिक-लाइट प्रणाली।",
        "saturation_level": "संतृप्ति स्तर",
        "status_optimal": "इष्टतम — सूखी ज़मीन", "status_moderate": "मध्यम — गीले बेंच", "status_high": "उच्च — जलभराव जोखिम",
        "ops_safe": "✅ भारी परिवहन और विस्फोट के लिए सुरक्षित", "ops_monitor": "⚡ सम्प निकासी की बारीकी से निगरानी करें", "ops_halt": "🚫 भारी उपकरण परिवहन रोकें",
        "avg_label": "औसत", "latest_label": "नवीनतम", "period_label": "अवधि",
        "trend_title": "📈 मृदा नमी — ऐतिहासिक प्रवृत्ति (वार्षिक/मासिक)",
        "trend_title_year": "📈 मृदा नमी — चयनित वर्ष हेतु मासिक प्रवृत्ति",
        "chart_month_axis": "माह", "chart_sm_axis": "मृदा नमी संतृप्ति (%)",
        "legend_low": "🟢 < 50% संतृप्ति — सूखी ज़मीन। सभी भारी वाहन परिवहन और विस्फोट कार्यों के लिए सुरक्षित।",
        "legend_mod": "🟡 50–75% संतृप्ति — गीले बेंच। सम्प निकासी की निगरानी करें, लदे डंपर की गति सीमित करें।",
        "legend_high": "🔴 > 75% संतृप्ति — उच्च जलभराव जोखिम। भारी उपकरण रोकें। गड्ढा धंसने का खतरा।",
        "no_soil_data": "इस चयन के लिए मृदा नमी डेटा उपलब्ध नहीं है।",
    },
    "🌺 తెలుగు": {
        "title": "⛏️ MOIL స్మార్ట్ మైనింగ్ హబ్",
        "subtitle": "రిజర్వ్ మ్యాపింగ్, శార్ట్‌ఫాల్ అంచనా మరియు దిద్దుబాటు చర్యల AI/ML వేదిక.",
        "select_mine": "🏭 గని ఎంచుకోండి", "select_year": "📅 సంవత్సరం",
        "all_mines": "అన్ని గనులు", "all_years": "అన్ని సంవత్సరాలు",
        "avg_reserve": "సగటు రిజర్వ్", "total_production": "మొత్తం ఉత్పత్తి (టన్)",
        "high_risk": "అధిక ప్రమాద నెలలు", "avg_downtime": "సగటు డౌన్‌టైమ్",
        "map_title": "🗺️ జియోస్పేషియల్ & రిజర్వ్ మ్యాప్",
        "heatmap_tab": "🌡️ మాంగనీస్ హీట్‌మ్యాప్", "map_3d_tab": "🌐 3D వీక్షణ",
        "swir_tab": "🔬 SWIR/స్పెక్ట్రల్", "sar_tab": "📡 SAR రాడార్",
        "borehole_tab": "🕳️ బోర్‌హోల్స్",
        "afforestation_tab": "🌿 వృక్షసంపద", "weather_tab": "🌧️ వాతావరణం",
        "production_trend": "📈 ఉత్పత్తి ట్రెండ్", "actual": "వాస్తవ", "predicted": "అంచనా",
        "risk_dist": "⚠️ ప్రమాద పంపిణీ", "alerts": "🚨 హెచ్చరికలు",
        "no_alerts": "✅ ప్రమాదాలు లేవు.",
        "fleet_title": "🚛 ఫ్లీట్ & పరికర స్థితి",
        "compliance_title": "🌿 పర్యావరణ సమ్మతి",
        "blending_title": "⚗️ ధాతువు గ్రేడ్ మిశ్రమ సిఫార్సులు",
        "simulator_title": "🧪 వాట్-ఇఫ్ సిమ్యులేటర్",
        "ai_title": "🤖 AI గని సహాయకుడు",
        "ai_placeholder": "మీ గనుల గురించి అడగండి...",
        "voice_title": "🎙️ వాయిస్ అసిస్టెంట్",
        "raw_data": "📋 డేటా పట్టిక",
        "notifications": "🔔 నోటిఫికేషన్లు",
        "high_prob": "అధిక సంభావ్యత", "mod_prob": "మధ్యస్థ సంభావ్యత", "low_prob": "తక్కువ సంభావ్యత",
        "mine": "గని", "year": "సంవత్సరం", "month": "నెల",
        "reserve_score": "రిజర్వ్ స్కోర్", "reserve_cat": "రిజర్వ్ వర్గం",
        "production": "ఉత్పత్తి (టన్)", "pred_production": "అంచనా ఉత్పత్తి",
        "shortfall": "లోటు ప్రమాదం", "recommendation": "సిఫార్సు",
        "ndvi": "NDVI", "lst": "ఉష్ణోగ్రత (°C)", "soil": "నేల తేమ", "rainfall": "వర్షపాతం (మిమీ)",
        "downtime": "డౌన్‌టైమ్ (గం)", "blasting": "పేలుడు జాప్యం",
        "soil_tab": "💧 నేల తేమ",
        "soil_title": "💧 ఉపగ్రహ నేల తేమ — నిర్వహణ భద్రతా మదింపు",
        "soil_subtitle": "NASA SMAP ఉపగ్రహ డేటా ఆధారంగా. తక్షణ గని నిర్వహణ నిర్ణయాల కోసం ట్రాఫిక్-లైట్ విధానం.",
        "saturation_level": "సంతృప్త స్థాయి",
        "status_optimal": "అనుకూలం — పొడి నేల", "status_moderate": "మధ్యస్థం — తడి బెంచీలు", "status_high": "అధికం — నీటి నిల్వ ప్రమాదం",
        "ops_safe": "✅ భారీ రవాణా మరియు పేలుడుకు సురక్షితం", "ops_monitor": "⚡ డ్రైనేజీని జాగ్రత్తగా పర్యవేక్షించండి", "ops_halt": "🚫 భారీ పరికరాల రవాణా నిలిపివేయండి",
        "avg_label": "సగటు", "latest_label": "తాజా", "period_label": "కాలం",
        "trend_title": "📈 నేల తేమ — చారిత్రక ధోరణి (వార్షిక/నెలవారీ)",
        "trend_title_year": "📈 నేల తేమ — ఎంచుకున్న సంవత్సరానికి నెలవారీ ధోరణి",
        "chart_month_axis": "నెల", "chart_sm_axis": "నేల తేమ సంతృప్తత (%)",
        "legend_low": "🟢 < 50% సంతృప్తత — పొడి నేల. అన్ని భారీ వాహన రవాణా మరియు పేలుడు కార్యకలాపాలకు సురక్షితం.",
        "legend_mod": "🟡 50–75% సంతృప్తత — తడి బెంచీలు. డ్రైనేజీని పర్యవేక్షించండి, లోడెడ్ డంపర్ వేగాన్ని పరిమితం చేయండి.",
        "legend_high": "🔴 > 75% సంతృప్తత — అధిక నీటి నిల్వ ప్రమాదం. భారీ పరికరాలను నిలిపివేయండి. గుంట కుంగే ప్రమాదం.",
        "no_soil_data": "ఈ ఎంపిక కోసం నేల తేమ డేటా అందుబాటులో లేదు.",
    },
    "🌸 मराठी": {
        "title": "⛏️ MOIL स्मार्ट मायनिंग हब",
        "subtitle": "साठा नकाशा, तूट अंदाज आणि सुधारात्मक कृतींसाठी AI/ML प्लॅटफॉर्म.",
        "select_mine": "🏭 खाण निवडा", "select_year": "📅 वर्ष निवडा",
        "all_mines": "सर्व खाणी", "all_years": "सर्व वर्षे",
        "avg_reserve": "सरासरी साठा", "total_production": "एकूण उत्पादन (टन)",
        "high_risk": "उच्च जोखीम महिने", "avg_downtime": "सरासरी डाउनटाइम",
        "map_title": "🗺️ भू-स्थानिक आणि साठा नकाशा",
        "heatmap_tab": "🌡️ मँगनीज हीटमॅप", "map_3d_tab": "🌐 3D दृश्य",
        "swir_tab": "🔬 SWIR/स्पेक्ट्रल", "sar_tab": "📡 SAR रडार",
        "borehole_tab": "🕳️ बोअरहोल",
        "afforestation_tab": "🌿 वनस्पती", "weather_tab": "🌧️ हवामान",
        "production_trend": "📈 उत्पादन कल", "actual": "वास्तविक", "predicted": "अंदाजित",
        "risk_dist": "⚠️ जोखीम वितरण", "alerts": "🚨 सक्रिय सतर्कता",
        "no_alerts": "✅ कोणतेही जोखीम नाही.",
        "fleet_title": "🚛 ताफा आणि उपकरण स्थिती",
        "compliance_title": "🌿 पर्यावरण अनुपालन",
        "blending_title": "⚗️ अयस्क ग्रेड मिश्रण शिफारसी",
        "simulator_title": "🧪 काय-जर परिस्थिती सिम्युलेटर",
        "ai_title": "🤖 AI खाण सहाय्यक",
        "ai_placeholder": "तुमच्या खाणींबद्दल विचारा...",
        "voice_title": "🎙️ व्हॉइस असिस्टंट",
        "raw_data": "📋 डेटा तक्ता",
        "notifications": "🔔 सूचना आणि इशारे",
        "high_prob": "उच्च शक्यता", "mod_prob": "मध्यम शक्यता", "low_prob": "कमी शक्यता",
        "mine": "खाण", "year": "वर्ष", "month": "महिना",
        "reserve_score": "साठा स्कोर", "reserve_cat": "साठा श्रेणी",
        "production": "उत्पादन (टन)", "pred_production": "अंदाजित उत्पादन",
        "shortfall": "तूट जोखीम", "recommendation": "शिफारस",
        "ndvi": "NDVI", "lst": "तापमान (°C)", "soil": "मृदा ओलावा", "rainfall": "पाऊस (मिमी)",
        "downtime": "डाउनटाइम (तास)", "blasting": "स्फोट विलंब",
        "soil_tab": "💧 मृदा ओलावा",
        "soil_title": "💧 उपग्रह मृदा ओलावा — परिचालन सुरक्षा मूल्यांकन",
        "soil_subtitle": "NASA SMAP उपग्रह डेटावर आधारित. खाण कामकाजाच्या त्वरित निर्णयासाठी ट्रॅफिक-लाइट प्रणाली.",
        "saturation_level": "संपृक्तता पातळी",
        "status_optimal": "इष्टतम — कोरडी जमीन", "status_moderate": "मध्यम — ओले बेंच", "status_high": "उच्च — पाणी साचण्याचा धोका",
        "ops_safe": "✅ जड वाहतूक आणि स्फोटासाठी सुरक्षित", "ops_monitor": "⚡ सम्प निचरा बारकाईने तपासा", "ops_halt": "🚫 जड उपकरण वाहतूक थांबवा",
        "avg_label": "सरासरी", "latest_label": "नवीनतम", "period_label": "कालावधी",
        "trend_title": "📈 मृदा ओलावा — ऐतिहासिक कल (वार्षिक/मासिक)",
        "trend_title_year": "📈 मृदा ओलावा — निवडलेल्या वर्षासाठी मासिक कल",
        "chart_month_axis": "महिना", "chart_sm_axis": "मृदा ओलावा संपृक्तता (%)",
        "legend_low": "🟢 < 50% संपृक्तता — कोरडी जमीन. सर्व जड वाहन वाहतूक आणि स्फोट कामांसाठी सुरक्षित.",
        "legend_mod": "🟡 50–75% संपृक्तता — ओले बेंच. सम्प निचरा तपासा, भरलेल्या डंपरचा वेग मर्यादित करा.",
        "legend_high": "🔴 > 75% संपृक्तता — पाणी साचण्याचा उच्च धोका. जड उपकरणे थांबवा. खड्डा खचण्याचा धोका.",
        "no_soil_data": "या निवडीसाठी मृदा ओलावा डेटा उपलब्ध नाही.",
    },
    "🌟 தமிழ்": {
        "title": "⛏️ MOIL ஸ்மார்ட் மைனிங் ஹப்",
        "subtitle": "இருப்பு வரைபடம், குறைபாடு கணிப்பு மற்றும் திருத்த நடவடிக்கைகளுக்கான AI/ML தளம்.",
        "select_mine": "🏭 சுரங்கம் தேர்வு", "select_year": "📅 ஆண்டு தேர்வு",
        "all_mines": "அனைத்து சுரங்கங்கள்", "all_years": "அனைத்து ஆண்டுகள்",
        "avg_reserve": "சராசரி இருப்பு", "total_production": "மொத்த உற்பத்தி (டன்)",
        "high_risk": "அதிக ஆபத்து மாதங்கள்", "avg_downtime": "சராசரி நேர இழப்பு",
        "map_title": "🗺️ புவி-இடஞ்சார் வரைபடம்",
        "heatmap_tab": "🌡️ மாங்கனீஸ் வெப்ப வரைபடம்", "map_3d_tab": "🌐 3D வரைபடம்",
        "swir_tab": "🔬 SWIR/நிறமாலை", "sar_tab": "📡 SAR ரேடார்",
        "borehole_tab": "🕳️ துளை குழிகள்",
        "afforestation_tab": "🌿 தாவரவியல்", "weather_tab": "🌧️ வானிலை",
        "production_trend": "📈 உற்பத்தி போக்கு", "actual": "உண்மையான", "predicted": "கணிக்கப்பட்ட",
        "risk_dist": "⚠️ ஆபத்து விநியோகம்", "alerts": "🚨 எச்சரிக்கைகள்",
        "no_alerts": "✅ ஆபத்துகள் இல்லை.",
        "fleet_title": "🚛 வாகன & பரிகரண நிலை",
        "compliance_title": "🌿 சுற்றுச்சூழல் இணக்கம்",
        "blending_title": "⚗️ தாது தர கலவை பரிந்துரைகள்",
        "simulator_title": "🧪 என்ன-ஆனால் சிமுலேட்டர்",
        "ai_title": "🤖 AI சுரங்க உதவியாளர்",
        "ai_placeholder": "சுரங்கங்கள் பற்றி கேளுங்கள்...",
        "voice_title": "🎙️ குரல் உதவியாளர்",
        "raw_data": "📋 தரவு அட்டவணை",
        "notifications": "🔔 அறிவிப்புகள்",
        "high_prob": "அதிக நிகழ்தகவு", "mod_prob": "மிதமான நிகழ்தகவு", "low_prob": "குறைந்த நிகழ்தகவு",
        "mine": "சுரங்கம்", "year": "ஆண்டு", "month": "மாதம்",
        "reserve_score": "இருப்பு மதிப்பு", "reserve_cat": "இருப்பு வகை",
        "production": "உற்பத்தி (டன்)", "pred_production": "கணிக்கப்பட்ட உற்பத்தி",
        "shortfall": "குறைபாடு ஆபத்து", "recommendation": "பரிந்துரை",
        "ndvi": "NDVI", "lst": "வெப்பநிலை (°C)", "soil": "மண் ஈரப்பதம்", "rainfall": "மழை (மிமீ)",
        "downtime": "நேர இழப்பு (மணி)", "blasting": "வெடிப்பு தாமதம்",
        "soil_tab": "💧 மண் ஈரப்பதம்",
        "soil_title": "💧 செயற்கைக்கோள் மண் ஈரப்பதம் — செயல்பாட்டு பாதுகாப்பு மதிப்பீடு",
        "soil_subtitle": "NASA SMAP செயற்கைக்கோள் தரவை அடிப்படையாகக் கொண்டது. உடனடி சுரங்க இயக்க முடிவுக்கான ட்ராஃபிக்-லைட் அமைப்பு.",
        "saturation_level": "செறிவு நிலை",
        "status_optimal": "உகந்தது — உலர் நிலம்", "status_moderate": "மிதமானது — ஈரமான பெஞ்சுகள்", "status_high": "அதிகம் — நீர்த்தேக்க ஆபத்து",
        "ops_safe": "✅ கனரக போக்குவரத்து மற்றும் வெடிப்புக்கு பாதுகாப்பானது", "ops_monitor": "⚡ வடிகால் வடிகட்டலை உன்னிப்பாகக் கண்காணிக்கவும்", "ops_halt": "🚫 கனரக உபகரண போக்குவரத்தை நிறுத்தவும்",
        "avg_label": "சராசரி", "latest_label": "சமீபத்திய", "period_label": "காலம்",
        "trend_title": "📈 மண் ஈரப்பதம் — வரலாற்று போக்கு (ஆண்டு/மாதம்)",
        "trend_title_year": "📈 மண் ஈரப்பதம் — தேர்ந்தெடுக்கப்பட்ட ஆண்டுக்கான மாதாந்திர போக்கு",
        "chart_month_axis": "மாதம்", "chart_sm_axis": "மண் ஈரப்பத செறிவு (%)",
        "legend_low": "🟢 < 50% செறிவு — உலர் நிலம். அனைத்து கனரக வாகன போக்குவரத்து மற்றும் வெடிப்பு பணிகளுக்கும் பாதுகாப்பானது.",
        "legend_mod": "🟡 50–75% செறிவு — ஈரமான பெஞ்சுகள். வடிகால் வடிகட்டலை கண்காணிக்கவும், ஏற்றப்பட்ட டம்பர் வேகத்தை கட்டுப்படுத்தவும்.",
        "legend_high": "🔴 > 75% செறிவு — அதிக நீர்த்தேக்க ஆபத்து. கனரக உபகரணங்களை நிறுத்தவும். குழி சரிவு ஆபத்து.",
        "no_soil_data": "இந்த தேர்வுக்கு மண் ஈரப்பத தரவு கிடைக்கவில்லை.",
    },
    "🌊 বাংলা": {
        "title": "⛏️ MOIL স্মার্ট মাইনিং হাব",
        "subtitle": "রিজার্ভ ম্যাপিং, ঘাটতি পূর্বাভাস এবং সংশোধনমূলক পদক্ষেপের AI/ML প্ল্যাটফর্ম।",
        "select_mine": "🏭 খনি নির্বাচন", "select_year": "📅 বছর নির্বাচন",
        "all_mines": "সব খনি", "all_years": "সব বছর",
        "avg_reserve": "গড় রিজার্ভ", "total_production": "মোট উৎপাদন (টন)",
        "high_risk": "উচ্চ ঝুঁকির মাস", "avg_downtime": "গড় ডাউনটাইম",
        "map_title": "🗺️ জিওস্পেশিয়াল ও রিজার্ভ ম্যাপ",
        "heatmap_tab": "🌡️ ম্যাঙ্গানিজ হিটম্যাপ", "map_3d_tab": "🌐 3D দৃশ্য",
        "swir_tab": "🔬 SWIR/বর্ণালী", "sar_tab": "📡 SAR রাডার",
        "borehole_tab": "🕳️ বোরহোল",
        "afforestation_tab": "🌿 গাছপালা", "weather_tab": "🌧️ আবহাওয়া",
        "production_trend": "📈 উৎপাদন প্রবণতা", "actual": "প্রকৃত", "predicted": "পূর্বাভাসিত",
        "risk_dist": "⚠️ ঝুঁকি বিতরণ", "alerts": "🚨 সক্রিয় সতর্কতা",
        "no_alerts": "✅ কোনো ঝুঁকি নেই।",
        "fleet_title": "🚛 ফ্লিট ও যন্ত্রপাতি অবস্থা",
        "compliance_title": "🌿 পরিবেশ সম্মতি",
        "blending_title": "⚗️ আকরিক গ্রেড মিশ্রণ পরামর্শ",
        "simulator_title": "🧪 কী-যদি পরিস্থিতি সিমুলেটর",
        "ai_title": "🤖 AI খনি সহায়ক",
        "ai_placeholder": "খনি সম্পর্কে জিজ্ঞাসা করুন...",
        "voice_title": "🎙️ ভয়েস অ্যাসিস্ট্যান্ট",
        "raw_data": "📋 ডেটা টেবিল",
        "notifications": "🔔 বিজ্ঞপ্তি",
        "high_prob": "উচ্চ সম্ভাবনা", "mod_prob": "মাঝারি সম্ভাবনা", "low_prob": "কম সম্ভাবনা",
        "mine": "খনি", "year": "বছর", "month": "মাস",
        "reserve_score": "রিজার্ভ স্কোর", "reserve_cat": "রিজার্ভ বিভাগ",
        "production": "উৎপাদন (টন)", "pred_production": "পূর্বাভাস উৎপাদন",
        "shortfall": "ঘাটতি ঝুঁকি", "recommendation": "সুপারিশ",
        "ndvi": "NDVI", "lst": "তাপমাত্রা (°C)", "soil": "মাটির আর্দ্রতা", "rainfall": "বৃষ্টি (মিমি)",
        "downtime": "ডাউনটাইম (ঘণ্টা)", "blasting": "বিস্ফোরণ বিলম্ব",
        "soil_tab": "💧 মাটির আর্দ্রতা",
        "soil_title": "💧 স্যাটেলাইট মাটির আর্দ্রতা — পরিচালন নিরাপত্তা মূল্যায়ন",
        "soil_subtitle": "NASA SMAP স্যাটেলাইট ডেটার উপর ভিত্তি করে। তাৎক্ষণিক খনি পরিচালন সিদ্ধান্তের জন্য ট্রাফিক-লাইট পদ্ধতি।",
        "saturation_level": "সম্পৃক্তি স্তর",
        "status_optimal": "সর্বোত্তম — শুকনো মাটি", "status_moderate": "মাঝারি — ভেজা বেঞ্চ", "status_high": "উচ্চ — জলাবদ্ধতার ঝুঁকি",
        "ops_safe": "✅ ভারী পরিবহন ও বিস্ফোরণের জন্য নিরাপদ", "ops_monitor": "⚡ সাম্প নিষ্কাশন ঘনিষ্ঠভাবে পর্যবেক্ষণ করুন", "ops_halt": "🚫 ভারী সরঞ্জাম পরিবহন বন্ধ করুন",
        "avg_label": "গড়", "latest_label": "সর্বশেষ", "period_label": "সময়কাল",
        "trend_title": "📈 মাটির আর্দ্রতা — ঐতিহাসিক প্রবণতা (বার্ষিক/মাসিক)",
        "trend_title_year": "📈 মাটির আর্দ্রতা — নির্বাচিত বছরের মাসিক প্রবণতা",
        "chart_month_axis": "মাস", "chart_sm_axis": "মাটির আর্দ্রতা সম্পৃক্তি (%)",
        "legend_low": "🟢 < 50% সম্পৃক্তি — শুকনো মাটি। সমস্ত ভারী যান চলাচল ও বিস্ফোরণ কাজের জন্য নিরাপদ।",
        "legend_mod": "🟡 50–75% সম্পৃক্তি — ভেজা বেঞ্চ। সাম্প নিষ্কাশন পর্যবেক্ষণ করুন, বোঝাই ডাম্পারের গতি সীমিত করুন।",
        "legend_high": "🔴 > 75% সম্পৃক্তি — উচ্চ জলাবদ্ধতার ঝুঁকি। ভারী সরঞ্জাম বন্ধ করুন। গর্ত ধসের ঝুঁকি।",
        "no_soil_data": "এই নির্বাচনের জন্য মাটির আর্দ্রতা ডেটা উপলব্ধ নেই।",
    },
}

# ═══════════════════════════════════════════
# STATIC DATA
# ═══════════════════════════════════════════
MINE_COORDS = {
    "Balaghat_MP":                  {"lat": 21.80, "lon": 80.19, "label": "Balaghat, MP",     "type": "underground", "depth": 383},
    "Nagpur_Maharashtra":           {"lat": 21.20, "lon": 79.15, "label": "Nagpur, MH",       "type": "open-cast",   "depth": 45},
    "Bhandara_Maharashtra":         {"lat": 21.15, "lon": 79.65, "label": "Bhandara, MH",     "type": "open-cast",   "depth": 38},
    "Gujarat_Pani_ExplorationZone": {"lat": 22.60, "lon": 73.40, "label": "Pani, Gujarat",    "type": "exploration", "depth": 0},
}

# (lat, lon, probability, label, level, tonnage_mt, mn_pct_avg, state)
MANGANESE_ZONES = [
    (21.80, 80.19, 0.92, "Balaghat, MP (MOIL)",     "high",     53.47, 44.5, "Madhya Pradesh"),
    (21.20, 79.15, 0.78, "Nagpur, MH (MOIL)",        "high",     18.20, 32.8, "Maharashtra"),
    (21.15, 79.65, 0.72, "Bhandara, MH (MOIL)",      "high",     12.40, 31.0, "Maharashtra"),
    (22.60, 73.40, 0.62, "Pani, Gujarat (MOIL)",     "moderate",  9.51, 22.3, "Gujarat"),
    (20.10, 85.10, 0.85, "Keonjhar, Odisha",         "high",     95.00, 40.2, "Odisha"),
    (22.25, 84.85, 0.80, "Sundargarh, Odisha",       "high",     62.00, 38.5, "Odisha"),
    (19.30, 84.50, 0.75, "Koraput, Odisha",          "high",     34.00, 36.0, "Odisha"),
    (15.85, 74.50, 0.70, "Dharwad, Karnataka",       "moderate", 28.00, 33.5, "Karnataka"),
    (15.20, 75.70, 0.65, "Chitradurga, Karnataka",   "moderate", 18.50, 30.0, "Karnataka"),
    (14.45, 76.00, 0.60, "Bellary, Karnataka",       "moderate", 12.00, 28.5, "Karnataka"),
    (21.50, 78.50, 0.55, "Chhindwara, MP",           "moderate",  8.00, 27.0, "Madhya Pradesh"),
    (22.70, 82.15, 0.50, "Bilaspur, CG",             "moderate",  5.50, 25.5, "Chhattisgarh"),
    (18.50, 76.00, 0.45, "Osmanabad, MH",            "low",       3.20, 22.0, "Maharashtra"),
    (24.00, 88.00, 0.30, "West Bengal",              "low",       1.80, 18.5, "West Bengal"),
    (16.50, 80.60, 0.35, "Krishna, AP",              "low",       2.50, 20.0, "Andhra Pradesh"),
    (25.00, 85.00, 0.25, "Bihar",                    "low",       0.90, 15.0, "Bihar"),
    (26.50, 80.00, 0.20, "Uttar Pradesh",            "low",       0.40, 12.0, "Uttar Pradesh"),
    (10.50, 76.50, 0.30, "Kerala",                   "low",       1.20, 16.5, "Kerala"),
    (11.00, 79.00, 0.25, "Tamil Nadu",               "low",       0.80, 14.0, "Tamil Nadu"),
]

# State-wise political boundaries (approximate centroids for labeling)
INDIA_STATES = [
    {"name": "Madhya Pradesh", "lat": 23.5, "lon": 78.5, "mn_mt": 61.47},
    {"name": "Maharashtra",    "lat": 19.5, "lon": 76.0, "mn_mt": 33.80},
    {"name": "Odisha",         "lat": 20.5, "lon": 85.0, "mn_mt": 191.0},
    {"name": "Karnataka",      "lat": 15.0, "lon": 75.5, "mn_mt": 58.50},
    {"name": "Gujarat",        "lat": 22.3, "lon": 71.5, "mn_mt": 9.51},
    {"name": "Chhattisgarh",   "lat": 21.5, "lon": 82.0, "mn_mt": 5.50},
    {"name": "Andhra Pradesh", "lat": 16.0, "lon": 80.0, "mn_mt": 2.50},
    {"name": "West Bengal",    "lat": 23.0, "lon": 87.5, "mn_mt": 1.80},
    {"name": "Bihar",          "lat": 25.5, "lon": 85.5, "mn_mt": 0.90},
    {"name": "Uttar Pradesh",  "lat": 27.0, "lon": 80.5, "mn_mt": 0.40},
    {"name": "Kerala",         "lat": 10.0, "lon": 76.5, "mn_mt": 1.20},
    {"name": "Tamil Nadu",     "lat": 11.0, "lon": 78.5, "mn_mt": 0.80},
]

BOREHOLE_DATA = [
    {"lat": 21.82, "lon": 80.21, "depth": 120, "mn_pct": 42.5, "label": "BH-001 (Balaghat)", "status": "Completed"},
    {"lat": 21.79, "lon": 80.17, "depth": 95,  "mn_pct": 38.2, "label": "BH-002 (Balaghat)", "status": "Completed"},
    {"lat": 21.81, "lon": 80.22, "depth": 150, "mn_pct": 45.1, "label": "BH-003 (Balaghat)", "status": "Active"},
    {"lat": 21.22, "lon": 79.17, "depth": 60,  "mn_pct": 32.8, "label": "BH-004 (Nagpur)",   "status": "Completed"},
    {"lat": 21.18, "lon": 79.14, "depth": 80,  "mn_pct": 29.5, "label": "BH-005 (Nagpur)",   "status": "Completed"},
    {"lat": 21.16, "lon": 79.67, "depth": 55,  "mn_pct": 31.0, "label": "BH-006 (Bhandara)", "status": "Completed"},
    {"lat": 22.62, "lon": 73.42, "depth": 40,  "mn_pct": 22.3, "label": "BH-007 (Gujarat)",  "status": "Active"},
    {"lat": 22.58, "lon": 73.38, "depth": 35,  "mn_pct": 18.9, "label": "BH-008 (Gujarat)",  "status": "Planned"},
]

FLEET_DATA = [
    {"id": "EX-01", "type": "Excavator",   "mine": "Balaghat",  "status": "Active",       "fuel": 78, "oee": 87, "next_maint": "2026-09-15"},
    {"id": "EX-02", "type": "Excavator",   "mine": "Nagpur",    "status": "Maintenance",  "fuel": 45, "oee": 0,  "next_maint": "2026-09-08"},
    {"id": "EX-03", "type": "Excavator",   "mine": "Bhandara",  "status": "Active",       "fuel": 91, "oee": 82, "next_maint": "2026-09-22"},
    {"id": "DR-01", "type": "Drill Rig",   "mine": "Balaghat",  "status": "Active",       "fuel": 65, "oee": 79, "next_maint": "2026-09-18"},
    {"id": "DR-02", "type": "Drill Rig",   "mine": "Gujarat",   "status": "Active",       "fuel": 88, "oee": 91, "next_maint": "2026-09-25"},
    {"id": "DU-01", "type": "Dumper",      "mine": "Balaghat",  "status": "Active",       "fuel": 72, "oee": 85, "next_maint": "2026-09-12"},
    {"id": "DU-02", "type": "Dumper",      "mine": "Nagpur",    "status": "Idle",         "fuel": 60, "oee": 0,  "next_maint": "2026-09-10"},
    {"id": "DU-03", "type": "Dumper",      "mine": "Bhandara",  "status": "Active",       "fuel": 83, "oee": 88, "next_maint": "2026-09-20"},
    {"id": "DU-04", "type": "Dumper",      "mine": "Nagpur",    "status": "Breakdown",    "fuel": 30, "oee": 0,  "next_maint": "URGENT"},
    {"id": "HL-01", "type": "Haul Truck",  "mine": "Balaghat",  "status": "Active",       "fuel": 55, "oee": 76, "next_maint": "2026-09-14"},
]

INDIA_LON = [68.2,68.1,69.0,70.9,71.0,68.9,68.2,68.0,70.0,74.0,78.0,82.0,86.0,89.0,92.0,92.5,
             91.0,89.5,88.0,86.5,84.0,82.0,80.0,78.5,77.0,75.5,74.0,72.5,71.0,69.5,68.2]
INDIA_LAT = [23.7,25.5,28.0,30.0,32.0,35.5,37.0,37.0,36.5,35.5,33.0,27.0,23.5,23.0,25.0,26.0,
             24.5,22.0,21.5,19.5,18.0,17.0,14.0,12.5,11.0,9.5,8.5,9.5,14.0,20.0,23.7]

MN_CS = [[0.0,"#1a0000"],[0.2,"#c0392b"],[0.4,"#e67e22"],[0.6,"#f1c40f"],[0.8,"#2ecc71"],[1.0,"#0d5e1e"]]
VEG_CS = [[0.0,"#5d4037"],[0.3,"#f57f17"],[0.6,"#aed581"],[0.8,"#2e7d32"],[1.0,"#1b5e20"]]
SWIR_CS = [[0.0,"#0d0221"],[0.25,"#2a1758"],[0.5,"#7b2d8b"],[0.75,"#d44000"],[1.0,"#ffcc00"]]

# Premium dark ("coal/charcoal") plot background — used across all cartesian geo-style charts
COAL_BG = "#07070a"

# ═══════════════════════════════════════════
# PLANTATION / AFFORESTATION PROTOTYPE DATA
# (Prototype/demo values — MOIL does not currently expose validated
#  plantation figures in the base dataset. Clearly labelled as such
#  wherever displayed.)
# ═══════════════════════════════════════════
PLANTATION_DATA = {
    "Balaghat_MP":                  {"target": 12000, "planted": 9200, "survival_rate": 82},
    "Nagpur_Maharashtra":           {"target": 7000,  "planted": 4100, "survival_rate": 74},
    "Bhandara_Maharashtra":         {"target": 4000,  "planted": 3050, "survival_rate": 79},
    "Gujarat_Pani_ExplorationZone": {"target": 2000,  "planted": 650,  "survival_rate": 68},
}

def plantation_metrics(target, planted):
    """Safely compute remaining plants and progress %, guarding against
    missing/zero/invalid values."""
    try:
        target = float(target) if target not in (None, "") else 0.0
    except (TypeError, ValueError):
        target = 0.0
    try:
        planted = float(planted) if planted not in (None, "") else 0.0
    except (TypeError, ValueError):
        planted = 0.0
    planted = max(0.0, planted)
    remaining = max(0.0, target - planted)
    progress = round((planted / target) * 100, 1) if target > 0 else 0.0
    progress = min(progress, 100.0)
    return remaining, progress

# ═══════════════════════════════════════════
# PROSPECTIVITY TIER (5-level, high-contrast, for map markers/legends)
# ═══════════════════════════════════════════
def prospectivity_tier(score):
    """score is a 0-1 model-estimated prospectivity value (NOT a % concentration)."""
    if score >= 0.80:
        return "Very High", "#00e676"
    elif score >= 0.65:
        return "High", "#4caf50"
    elif score >= 0.50:
        return "Moderate", "#ffd54f"
    elif score >= 0.35:
        return "Low", "#ff8a3d"
    else:
        return "Very Low", "#e53935"

def grade_category(mn_pct):
    if mn_pct > 44:
        return "High Grade", "#00e676"
    elif mn_pct >= 35:
        return "Medium Grade", "#ffd54f"
    elif mn_pct >= 25:
        return "Low Grade", "#ff8a3d"
    else:
        return "Very Low Grade", "#e53935"

GRADE_USE_TEXT = {
    "High Grade": "Potentially suitable for higher-grade ore applications, subject to chemistry and processing requirements.",
    "Medium Grade": "May require blending or processing depending on target specifications.",
    "Low Grade": "May require beneficiation or blending depending on mineralogy and end-use requirements.",
    "Very Low Grade": "May require substantial beneficiation or may have limited economic value depending on site conditions.",
}

# ═══════════════════════════════════════════
# REAL INDIA STATE BOUNDARIES (fetched once, cached; graceful offline fallback)
# Public administrative-boundary GeoJSON — used only to draw accurate
# state boundary lines on top of the existing lon/lat charts.
# ═══════════════════════════════════════════
@st.cache_data(ttl=86400, show_spinner=False)
def get_state_boundary_lines():
    """Returns a list of (lons, lats) polyline rings for India's state
    boundaries, extracted directly from a public GeoJSON so that
    `locations`/matching issues can't occur. Returns [] on any failure
    (offline, blocked network, schema change) so callers can fall back
    to the existing approximate outline without breaking the app."""
    url = ("https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/"
           "raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            gj = json.loads(resp.read().decode("utf-8"))
        rings = []
        for feat in gj.get("features", []):
            geom = feat.get("geometry", {})
            gtype = geom.get("type")
            coords = geom.get("coordinates", [])
            if gtype == "Polygon":
                polys = [coords]
            elif gtype == "MultiPolygon":
                polys = coords
            else:
                continue
            for poly in polys:
                for ring in poly:
                    lons = [pt[0] for pt in ring]
                    lats = [pt[1] for pt in ring]
                    rings.append((lons, lats))
        return rings
    except Exception:
        return []

STATE_BOUNDARY_RINGS = get_state_boundary_lines()

def add_boundaries(fig):
    """Adds accurate state boundary lines if available; otherwise falls
    back to the approximate national outline so the chart never breaks."""
    if STATE_BOUNDARY_RINGS:
        for lons, lats in STATE_BOUNDARY_RINGS:
            fig.add_trace(go.Scatter(
                x=lons, y=lats, mode="lines",
                line=dict(color="rgba(190,200,215,0.55)", width=1),
                hoverinfo="skip", showlegend=False))
        # Slightly brighter national outline on top for contrast
        fig.add_trace(go.Scatter(x=INDIA_LON, y=INDIA_LAT, mode="lines",
                      line=dict(color="rgba(230,235,245,0.85)", width=1.6),
                      showlegend=False, hoverinfo="skip"))
    else:
        fig.add_trace(india_outline())

# ═══════════════════════════════════════════
# HEATMAP GRID
# ═══════════════════════════════════════════
@st.cache_data
def build_grids():
    lons = np.linspace(67, 97, 150)
    lats = np.linspace(6, 37, 120)
    LO, LA = np.meshgrid(lons, lats)
    Z = np.zeros_like(LO)
    for (zlat,zlon,prob,_,_,*_rest) in MANGANESE_ZONES:
        d = np.sqrt((LO-zlon)**2+(LA-zlat)**2)
        Z += prob/(d**1.8+0.3)
    Z = (Z-Z.min())/(Z.max()-Z.min())
    mask = ((LO>68)&(LO<97)&(LA>7)&(LA<37)&~((LO<75)&(LA>30))&~((LO>90)&(LA<20))&~((LO<70)&(LA<20)))
    Z_mn = np.where(mask, Z, np.nan)

    Z_veg = np.zeros_like(LO)
    vz = [(21.80,80.19,0.45),(21.20,79.15,0.38),(21.15,79.65,0.42),(22.60,73.40,0.55),
          (20.10,85.10,0.65),(22.25,84.85,0.70),(15.85,74.50,0.60),(10.50,76.50,0.75),(11.00,79.00,0.68),
          (28.50,77.00,0.20),(26.50,80.00,0.15),(25.00,85.00,0.25),(16.50,80.60,0.50),(19.30,84.50,0.58)]
    for (vlat,vlon,vp) in vz:
        d = np.sqrt((LO-vlon)**2+(LA-vlat)**2)
        Z_veg += vp/(d**1.5+0.4)
    Z_veg = (Z_veg-Z_veg.min())/(Z_veg.max()-Z_veg.min())
    Z_veg_m = np.where(mask, Z_veg, np.nan)

    # SWIR (simulate MnO2 spectral signature — inverse of vegetation, high in rock-exposed zones)
    Z_swir = np.zeros_like(LO)
    swir_z = [(21.80,80.19,0.88),(21.20,79.15,0.75),(21.15,79.65,0.70),(22.60,73.40,0.60),
              (20.10,85.10,0.82),(22.25,84.85,0.78),(15.85,74.50,0.65),(15.20,75.70,0.60)]
    for (slat,slon,sp) in swir_z:
        d = np.sqrt((LO-slon)**2+(LA-slat)**2)
        Z_swir += sp/(d**2.0+0.25)
    Z_swir = (Z_swir-Z_swir.min())/(Z_swir.max()-Z_swir.min())
    Z_swir_m = np.where(mask, Z_swir, np.nan)

    # SAR (simulate ground deformation / pit stability)
    Z_sar = np.zeros_like(LO)
    np.random.seed(42)
    noise = np.random.normal(0, 0.05, Z_sar.shape)
    for (zlat,zlon,prob,_,_,*_rest) in MANGANESE_ZONES:
        d = np.sqrt((LO-zlon)**2+(LA-zlat)**2)
        Z_sar += (prob*0.7)/(d**1.6+0.3)
    Z_sar = (Z_sar-Z_sar.min())/(Z_sar.max()-Z_sar.min()) + noise*0.3
    Z_sar = np.clip(Z_sar,0,1)
    Z_sar_m = np.where(mask, Z_sar, np.nan)

    return lons, lats, Z_mn, Z_veg_m, Z_swir_m, Z_sar_m

lons_grid, lats_grid, Z_mn, Z_veg, Z_swir, Z_sar = build_grids()

# ═══════════════════════════════════════════
# WEATHER
# ═══════════════════════════════════════════
def gen_weather():
    # Deterministic per calendar day: same date always produces the same
    # 7-day outlook instead of a new random forecast on every Streamlit rerun.
    today = datetime.now()
    rng = random.Random(today.toordinal())
    base = [5,8,20,80,180,280,350,300,200,60,10,5]
    out = []
    for i in range(7):
        d = today+timedelta(days=i)
        rain = max(0, base[d.month-1]/30+rng.gauss(0,base[d.month-1]/40))
        temp = 28+rng.gauss(0,3)+(2 if d.month in [4,5,6] else 0)
        hum = min(95,40+rain*0.3+rng.gauss(0,5))
        if rain>25: cond,alert="⛈️ Heavy Rain",True
        elif rain>10: cond,alert="🌧️ Rain",True
        elif rain>3: cond,alert="🌦️ Light Rain",False
        elif hum>70: cond,alert="⛅ Cloudy",False
        else: cond,alert="☀️ Sunny",False
        out.append({"date":d.strftime("%a %d %b"),"cond":cond,"rain":round(rain,1),
                    "temp":round(temp,1),"hum":round(hum),"alert":alert,
                    "impact":"⚠️ Halt outdoor ops" if rain>25 else ("⚡ Monitor drainage" if rain>10 else "✅ Normal ops")})
    return out

weather_data = gen_weather()

# ═══════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════
@st.cache_data
def load_data():
    return pd.read_csv("manganese_final_dataset.csv")

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ 'manganese_final_dataset.csv' not found. Place it in the same folder as app.py.")
    st.stop()

# ═══════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⛏️ MOIL Smart Mining Hub")
    lang = st.selectbox("🌐 Language / भाषा", list(TRANSLATIONS.keys()))
    T = TRANSLATIONS[lang]
    st.markdown("---")
    mine_opts = [T["all_mines"]]+sorted(df["mine"].unique().tolist())
    selected_mine = st.selectbox(T["select_mine"], mine_opts)
    year_opts = [T["all_years"]]+sorted(df["year"].unique().tolist())
    selected_year = st.selectbox(T["select_year"], year_opts)
    st.markdown("---")
    st.markdown(f"### {T['notifications']}")
    rain_alerts = [w for w in weather_data if w["alert"]]
    if rain_alerts:
        for w in rain_alerts[:3]:
            st.warning(f"**{w['date']}**: {w['cond']}\n\n💧 {w['rain']}mm expected\n\n{w['impact']}")
    else:
        st.success("✅ No rain alerts next 7 days")
    # Fleet alerts
    broken = [f for f in FLEET_DATA if f["status"]=="Breakdown"]
    maint = [f for f in FLEET_DATA if f["status"]=="Maintenance"]
    if broken:
        for b in broken:
            st.error(f"🔴 **{b['id']}** ({b['type']}) BREAKDOWN at {b['mine']}")
    if maint:
        for m in maint:
            st.warning(f"🟠 **{m['id']}** ({m['type']}) in Maintenance at {m['mine']}")
    st.markdown("---")
    st.caption("SIH 2026 · Problem 26009 · Ministry of Steel / MOIL Ltd.")

T = TRANSLATIONS[lang]

# Filter
filtered_df = df.copy()
if selected_mine != T["all_mines"]:
    filtered_df = filtered_df[filtered_df["mine"]==selected_mine]
if selected_year != T["all_years"]:
    filtered_df = filtered_df[filtered_df["year"]==int(selected_year)]

# ═══════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════
st.title(T["title"])
st.markdown(T["subtitle"])
st.markdown("---")

# ═══════════════════════════════════════════
# KPI CARDS
# ═══════════════════════════════════════════
k1,k2,k3,k4,k5,k6 = st.columns(6)
avg_prod = filtered_df["production_tons"].mean()
target = avg_prod * 1.1
shortfall_pct = round((target-avg_prod)/target*100,1)
active_fleet = sum(1 for f in FLEET_DATA if f["status"]=="Active")
avg_oee = round(np.mean([f["oee"] for f in FLEET_DATA if f["oee"]>0]),1)

k1.metric(f"📊 {T['avg_reserve']}", f"{filtered_df['reserve_potential_score'].mean():.2f} / 1.00",
          help="Model-estimated prospectivity score, not a measured underground manganese concentration.")
k2.metric(f"⛏️ {T['total_production']}", f"{filtered_df['production_tons'].sum():,.0f} tons")
k3.metric("🎯 Target vs Actual", f"{shortfall_pct}% gap", delta=f"-{shortfall_pct}%")
k4.metric(f"🚨 {T['high_risk']}", f"{int((filtered_df['shortfall_risk']=='High Risk').sum())} months")
k5.metric("🚛 Active Fleet", f"{active_fleet} / {len(FLEET_DATA)}")
k6.metric("⚙️ Avg OEE", f"{avg_oee}%")
st.markdown(
    "<div class='moil-proto-note'>ℹ️ Prototype uses simulated/demo operational and exploration values where "
    "validated MOIL data is unavailable. The system is designed for integration with validated MOIL datasets.</div>",
    unsafe_allow_html=True)
st.markdown("---")

# ═══════════════════════════════════════════
# MAP SECTION
# ═══════════════════════════════════════════
st.subheader(T["map_title"])
tab_2d, tab_3d, tab_swir, tab_sar, tab_bh, tab_veg, tab_soil, tab_wx = st.tabs([
    T["heatmap_tab"], T["map_3d_tab"], T["swir_tab"], T["sar_tab"],
    T["borehole_tab"], T["afforestation_tab"], T["soil_tab"], T["weather_tab"]
])

def india_outline():
    return go.Scatter(x=INDIA_LON,y=INDIA_LAT,mode="lines",
                      line=dict(color="white",width=1.5),showlegend=False,hoverinfo="skip")

def base_layout(title, h=600):
    return dict(height=h,
        xaxis=dict(title="Longitude (°E)",range=[67,98],gridcolor="rgba(255,255,255,0.04)",ticksuffix="°"),
        yaxis=dict(title="Latitude (°N)",range=[6,38],gridcolor="rgba(255,255,255,0.04)",ticksuffix="°",scaleanchor="x",scaleratio=1),
        plot_bgcolor=COAL_BG,paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30,b=10,l=10,r=10),
        title=dict(text=title,font=dict(size=14,color="white"),x=0.5))

def map_legend_html(items):
    """items: list of (glyph, label). Renders a compact readable legend row."""
    chips = "".join(f"<span class='moil-legend-chip'>{g} {l}</span>" for g,l in items)
    return f"<div>{chips}</div>"

# ── 2D Manganese Heatmap
with tab_2d:
    st.markdown(
        "<div class='moil-proto-note'>ℹ️ Prospectivity score reflects model-estimated potential based on "
        "available geological, exploration and satellite evidence. It is <b>not</b> a measured underground "
        "manganese concentration or a confirmed reserve figure. Prototype uses simulated/demo values where "
        "validated MOIL data is unavailable.</div>", unsafe_allow_html=True)
    map_col, info_col = st.columns([3, 1])
    with map_col:
        st.markdown(map_legend_html([
            ("🟢", "Very High / High Prospectivity"), ("🟡", "Moderate Prospectivity"),
            ("🟠", "Low Prospectivity"), ("🔴", "Very Low Prospectivity"),
            ("●", "Mine"), ("◆", "Borehole"), ("▲", "Exploration Point"), ("★", "Priority Prospect"),
        ]), unsafe_allow_html=True)
        fig2d = go.Figure()
        for (zlat,zlon,prob,label,level,tonnage,mn_pct,state) in MANGANESE_ZONES:
            tier_label, mc = prospectivity_tier(prob)
            gcat, _ = grade_category(mn_pct)
            is_mine = label.split("(")[0].strip() in [v["label"].split(",")[0] for v in MINE_COORDS.values()]
            glyph = "★" if prob >= 0.80 else ("●" if is_mine else "▲")
            marker_size = max(12, min(42, int(tonnage**0.52)))
            fig2d.add_trace(go.Scattermap(
                lat=[zlat], lon=[zlon],
                mode="markers+text",
                marker=dict(size=marker_size, color=mc, opacity=0.92),
                text=f"{glyph}  {label.split('(')[0].strip()}",
                textfont=dict(size=11, color="white"),
                textposition="top right",
                name=label,
                showlegend=False,
                hovertemplate=(
                    f"<b>{label.upper()}</b><br>"
                    f"Manganese Prospectivity: <b>{prob*100:.0f} / 100 ({tier_label})</b><br>"
                    f"Model Confidence: <b>{max(55, int(prob*100)-6)}%</b><br>"
                    f"Mn Grade: <b>{mn_pct}% ({gcat})</b><br>"
                    f"Estimated Tonnage: <b>{tonnage:.1f} MT</b><br>"
                    f"State: {state}<br>"
                    f"Evidence: Geological, surface spectral & exploration data<br>"
                    f"Next Step: Field verification / drilling correlation<extra></extra>"
                )
            ))
        fig2d.update_layout(
            map=dict(
                style="carto-darkmatter",
                center=dict(lat=21.0, lon=80.5),
                zoom=4.0
            ),
            height=600,
            margin=dict(t=30, b=0, l=0, r=0),
            title=dict(
                text="🗺️ India Manganese Prospectivity Map — Hover markers for full evidence detail",
                font=dict(size=13, color="#eee"), x=0.5
            ),
            paper_bgcolor=COAL_BG,
        )
        st.plotly_chart(fig2d, use_container_width=True)
        c1, c2, c3 = st.columns(3)
        c1.success("🟢 Very High / High Prospectivity: Balaghat, Odisha belts")
        c2.warning("🟡 Moderate Prospectivity: Karnataka, Nagpur, Bhandara, Gujarat")
        c3.error("🔴 Low / Very Low Prospectivity: UP, Bihar, Tamil Nadu")
        st.caption("Prospectivity score represents model-estimated potential based on available evidence. "
                   "It is not a measured underground manganese concentration or confirmed reserve.")

    with info_col:
        st.markdown("#### 📊 Reserve Summary")
        total_mn = sum(z[5] for z in MANGANESE_ZONES)
        high_mn  = sum(z[5] for z in MANGANESE_ZONES if z[6]>44)
        med_mn   = sum(z[5] for z in MANGANESE_ZONES if 35<=z[6]<=44)
        low_mn   = sum(z[5] for z in MANGANESE_ZONES if z[6]<35)
        st.metric("🌍 Total Estimated Tonnage", f"{total_mn:.0f} MT")
        st.metric("🟢 High Grade (>44% Mn)", f"{high_mn:.0f} MT")
        st.metric("🟡 Medium Grade (35-44%)", f"{med_mn:.0f} MT")
        st.metric("🔴 Low Grade (<35% Mn)", f"{low_mn:.0f} MT")
        st.markdown("---")
        st.markdown("#### 🏆 Top 5 by Estimated Tonnage")
        sorted_zones = sorted(MANGANESE_ZONES, key=lambda x: x[5], reverse=True)[:5]
        for i,(zlat,zlon,prob,label,level,tonnage,mn_pct,state) in enumerate(sorted_zones):
            icon = ["🥇","🥈","🥉","4️⃣","5️⃣"][i]
            gcat, _ = grade_category(mn_pct)
            mc = "🟢" if gcat=="High Grade" else ("🟡" if gcat=="Medium Grade" else ("🟠" if gcat=="Low Grade" else "🔴"))
            st.markdown(
                f"<div style='background:rgba(0,0,0,0.08);padding:8px;border-radius:8px;margin-bottom:6px;font-size:12px;'>"
                f"{icon} <b>{label.split('(')[0].strip()}</b><br>"
                f"{mc} <b>{tonnage:.1f} MT</b> | Mn: {mn_pct}% ({gcat})<br>📍 {state}</div>",
                unsafe_allow_html=True)
        st.markdown("---")
        st.caption("💡 Hover any circle for full details")
        st.caption("⭕ Bigger circle = more reserves (MT)")


# ── 3D Map
with tab_3d:
    fig3 = go.Figure()
    fig3.add_trace(go.Surface(x=lons_grid,y=lats_grid,z=Z_mn,colorscale=MN_CS,showscale=True,
        colorbar=dict(title="Mn Score",tickvals=[0,.25,.5,.75,1],
                      ticktext=["Negligible","Low","Moderate","High","Very High"]),opacity=0.92,
        hovertemplate="Lon: %{x:.1f}° | Lat: %{y:.1f}°<br>Score: %{z:.2f}<extra></extra>"))
    for (zlat,zlon,prob,label,level,*_rest) in MANGANESE_ZONES:
        mc = "#00ff88" if level=="high" else ("#f1c40f" if level=="moderate" else "#e74c3c")
        fig3.add_trace(go.Scatter3d(x=[zlon],y=[zlat],z=[prob+0.08],mode="markers+text",
            marker=dict(size=7 if level=="high" else 5,color=mc,line=dict(color="white",width=1)),
            text=label.split("(")[0].strip(),textposition="top center",
            textfont=dict(size=8,color="white"),showlegend=False,
            hovertemplate=f"<b>{label}</b><br>Score: {prob:.2f}<extra></extra>"))
    fig3.update_layout(height=650,scene=dict(
        xaxis_title="Longitude",yaxis_title="Latitude",zaxis_title="Prospectivity Score",
        bgcolor=COAL_BG,
        xaxis=dict(backgroundcolor=COAL_BG,gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(backgroundcolor=COAL_BG,gridcolor="rgba(255,255,255,0.08)"),
        zaxis=dict(backgroundcolor=COAL_BG,gridcolor="rgba(255,255,255,0.08)",range=[0,1.3]),
        camera=dict(eye=dict(x=1.6,y=-1.9,z=1.3))),
        paper_bgcolor="rgba(0,0,0,0)",margin=dict(t=30,b=10),
        title=dict(text="🌐 India Manganese Prospectivity — 3D Spatial View",font=dict(size=14,color="white"),x=0.5))
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("🖱️ Drag to rotate · Scroll to zoom · Peaks = higher model-estimated prospectivity, not measured reserve depth.")

# ── SWIR Tab
with tab_swir:
    st.markdown("### 🔬 SWIR / Surface Spectral Evidence")
    st.markdown(
        "Multispectral and SWIR (Sentinel-2 bands 11/12) satellite features provide **surface spectral "
        "information**. These indicators are combined with geological, terrain and exploration data to "
        "identify areas with higher manganese prospectivity.")
    st.markdown(
        "<div class='moil-proto-note'>ℹ️ Satellite spectral information provides surface evidence and does "
        "not directly measure underground manganese reserves. Ground investigation, sampling and drilling "
        "are required for confirmation.</div>", unsafe_allow_html=True)
    st.markdown(map_legend_html([("🟨🟧🟥","SWIR Reflectance: Low → Moderate → High"), ("◆","Borehole (color = Mn grade)")]),
                unsafe_allow_html=True)
    fig_swir = go.Figure()
    fig_swir.add_trace(go.Heatmap(x=lons_grid,y=lats_grid,z=Z_swir,colorscale=SWIR_CS,zmin=0,zmax=1,
        colorbar=dict(title="SWIR<br>Reflectance",tickvals=[0,.25,.5,.75,1],
                      ticktext=["Very Low","Low","Moderate","High","Very High"],len=0.85,thickness=14),
        opacity=0.90,hovertemplate="Lon: %{x:.1f}° | Lat: %{y:.1f}°<br>SWIR Reflectance: %{z:.2f}<extra></extra>"))
    add_boundaries(fig_swir)
    for bh in BOREHOLE_DATA:
        gcat,_ = grade_category(bh["mn_pct"])
        color = "#e53935" if bh["mn_pct"]>44 else ("#ffd54f" if bh["mn_pct"]>=25 else "#4caf50")
        fig_swir.add_trace(go.Scatter(x=[bh["lon"]],y=[bh["lat"]],mode="markers",
            marker=dict(size=12,color=color,symbol="diamond",line=dict(color="white",width=2)),
            showlegend=False,
            hovertemplate=(f"<b>{bh['label']}</b><br>Depth: {bh['depth']}m<br>Mn Grade: {bh['mn_pct']}% ({gcat})<br>"
                            f"Exploration Status: {bh['status']}<br>Model Confidence: 78%<extra></extra>")))
    fig_swir.update_layout(**base_layout("🔬 SWIR Spectral Evidence Map (Prototype)"))
    st.plotly_chart(fig_swir, use_container_width=True)
    st.info("💡 Yellow/orange/red zones = higher SWIR reflectance, an indicator combined with other evidence layers — not proof of manganese by itself. Diamonds show borehole assay grade for cross-reference.")
    st.caption("Prototype uses simulated/demo SWIR values where validated satellite-derived scores are unavailable.")

# ── SAR Tab
with tab_sar:
    st.markdown("### 📡 SAR Radar Analysis")
    st.markdown("""**SAR (Synthetic Aperture Radar)** penetrates monsoon cloud cover and can be used as a prototype indicator for:
    - Ground deformation around mine pits
    - Surface / ground condition monitoring
    - Active pit accessibility during heavy rain""")
    st.markdown(
        "<div class='moil-proto-note'>ℹ️ SAR indicators shown here are prototype signals. They do not "
        "guarantee the absence of subsidence risk — findings require field verification.</div>",
        unsafe_allow_html=True)
    st.markdown(map_legend_html([("🔴","Underground mine"), ("🔵","Open-cast mine"), ("🟦🟩🟧🟥","SAR indicator: Stable → Deformation")]),
                unsafe_allow_html=True)
    fig_sar = go.Figure()
    fig_sar.add_trace(go.Heatmap(x=lons_grid,y=lats_grid,z=Z_sar,
        colorscale=[[0,"#001f3f"],[0.3,"#0074D9"],[0.6,"#2ECC40"],[0.85,"#FF851B"],[1.0,"#FF4136"]],
        zmin=0,zmax=1,
        colorbar=dict(title="SAR<br>Indicator",tickvals=[0,.25,.5,.75,1],
                      ticktext=["Stable","Low","Moderate","High","Anomaly"],len=0.85,thickness=14),
        opacity=0.88,hovertemplate="Lon: %{x:.1f}° | Lat: %{y:.1f}°<br>SAR Indicator: %{z:.2f}<extra></extra>"))
    add_boundaries(fig_sar)
    for (mn,mc) in MINE_COORDS.items():
        sym = "circle" if mc["type"]=="underground" else "square"
        col = "#ff6b6b" if mc["type"]=="underground" else "#74b9ff"
        anomaly_note = "No significant anomaly detected in the prototype indicator" if mc["depth"] < 300 else "Elevated signal — requires field verification"
        fig_sar.add_trace(go.Scatter(x=[mc["lon"]],y=[mc["lat"]],mode="markers+text",
            marker=dict(size=14,color=col,symbol=sym,line=dict(color="white",width=2)),
            text=f"  {mc['label']}",textposition="middle right",
            textfont=dict(size=9,color="white"),showlegend=False,
            hovertemplate=(f"<b>{mc['label']}</b><br>Type: {mc['type']}<br>Depth: {mc['depth']}m<br>"
                            f"Observation: {anomaly_note}<extra></extra>")))
    fig_sar.update_layout(**base_layout("📡 SAR Radar — Ground Condition Indicator (Prototype)"))
    st.plotly_chart(fig_sar, use_container_width=True)
    st.info("💡 🔴 Circle = Underground mine · 🔵 Square = Open-cast. Higher SAR indicator values suggest a signal worth field verification — this prototype does not confirm or rule out subsidence risk.")

# ── Borehole Tab
with tab_bh:
    st.markdown("### 🕳️ Borehole Log & Assay Data — Core Drilling Results")
    st.markdown(
        "<div class='moil-proto-note'>ℹ️ Borehole depth and Mn grade values shown are prototype/demo assay "
        "values for illustration; the system is designed for integration with validated MOIL drilling data.</div>",
        unsafe_allow_html=True)
    st.markdown(map_legend_html([("🔴","Mineralized (>44% Mn)"), ("🟡","Low-grade (25–44% Mn)"),
                                  ("🟢","Exploration-grade (<25% Mn)"), ("⭕","Active"), ("✖","Planned")]),
                unsafe_allow_html=True)
    bh_cols = st.columns([2,1])
    with bh_cols[0]:
        fig_bh = go.Figure()
        fig_bh.add_trace(go.Heatmap(x=lons_grid,y=lats_grid,z=Z_mn,colorscale=MN_CS,zmin=0,zmax=1,
            colorbar=dict(title="Prospectivity<br>Score",len=0.7,thickness=12),opacity=0.55,showscale=True))
        add_boundaries(fig_bh)
        for i,bh in enumerate(BOREHOLE_DATA):
            gcat,_ = grade_category(bh["mn_pct"])
            col = "#e53935" if bh["mn_pct"]>44 else ("#ffd54f" if bh["mn_pct"]>=25 else "#4caf50")
            sym = "circle" if bh["status"]=="Completed" else ("circle-open" if bh["status"]=="Active" else "x")
            bh_id = f"BH-{i+1:03d}"
            mine_lbl = bh["label"].split("(")[-1].replace(")","").strip()
            state_lookup = {"Balaghat":"Madhya Pradesh","Nagpur":"Maharashtra","Bhandara":"Maharashtra","Gujarat":"Gujarat"}
            bh_state = state_lookup.get(mine_lbl, "—")
            fig_bh.add_trace(go.Scatter(x=[bh["lon"]],y=[bh["lat"]],mode="markers+text",
                marker=dict(size=14,color=col,symbol=sym,line=dict(color="white",width=2)),
                text=f"  {bh['label'].split('(')[0]}",textposition="middle right",
                textfont=dict(size=8,color="white"),showlegend=False,
                hovertemplate=(f"<b>{bh_id}</b><br>Mine/Zone: {mine_lbl}<br>State: {bh_state}<br>"
                                f"Lat/Lon: {bh['lat']:.2f}, {bh['lon']:.2f}<br>Depth: {bh['depth']} m<br>"
                                f"Mn Grade: {bh['mn_pct']}% ({gcat})<br>Exploration Status: {bh['status']}"
                                f"<br><i>Prototype data</i><extra></extra>")))
        fig_bh.update_layout(**base_layout("🕳️ Core Drilling & Borehole Assay Locations (Prototype Data)", h=520))
        st.plotly_chart(fig_bh, use_container_width=True)

    with bh_cols[1]:
        st.markdown("#### 📋 Borehole Log")
        bh_disp = []
        for i,bh in enumerate(BOREHOLE_DATA):
            gcat,_ = grade_category(bh["mn_pct"])
            bh_disp.append({"Borehole": f"BH-{i+1:03d}", "Depth (m)": bh["depth"],
                             "Mn Grade %": bh["mn_pct"], "Grade Category": gcat, "Status": bh["status"]})
        bh_df = pd.DataFrame(bh_disp)
        st.dataframe(bh_df, use_container_width=True, hide_index=True)
        avg_mn = np.mean([b["mn_pct"] for b in BOREHOLE_DATA])
        max_mn = max(b["mn_pct"] for b in BOREHOLE_DATA)
        st.metric("Avg Mn Grade", f"{avg_mn:.1f}%")
        st.metric("Peak Mn Grade", f"{max_mn:.1f}%", delta="BH-003 Balaghat")
        st.caption("🔴 Mineralized · 🟡 Low-grade · 🟢 Exploration-grade — ⭕ Active · ✖ Planned · filled = Completed")

# ── Vegetation Tab
with tab_veg:
    st.markdown("### 🌿 Vegetation Health & Afforestation Status")
    st.markdown(
        "NDVI is used for **vegetation and environmental monitoring**, including mine rehabilitation, "
        "land-cover assessment and afforestation tracking. It is not a direct manganese indicator.")
    v1,v2 = st.columns([3,1])
    with v1:
        fig_veg_map = go.Figure()
        fig_veg_map.add_trace(go.Heatmap(x=lons_grid,y=lats_grid,z=Z_veg,colorscale=VEG_CS,zmin=0,zmax=1,
            colorbar=dict(title="Vegetation<br>Health (NDVI)",tickvals=[0,.25,.5,.75,1],
                          ticktext=["Bare","Sparse","Moderate","Dense","Very Dense"],len=0.85,thickness=14),
            opacity=0.90,hovertemplate="Lon: %{x:.1f}° | Lat: %{y:.1f}°<br>NDVI: %{z:.2f}<extra></extra>"))
        add_boundaries(fig_veg_map)
        for mn,mc in MINE_COORDS.items():
            row = df[df["mine"]==mn]
            avg_ndvi = row["NDVI"].mean() if len(row)>0 else 0.35
            nc = "#2ecc71" if avg_ndvi>0.35 else ("#f1c40f" if avg_ndvi>0.25 else "#e74c3c")
            fig_veg_map.add_trace(go.Scatter(x=[mc["lon"]],y=[mc["lat"]],mode="markers+text",
                marker=dict(size=14,color=nc,symbol="diamond",line=dict(color="white",width=2)),
                text=f"  {mc['label']}",textposition="middle right",
                textfont=dict(size=9,color="white"),showlegend=False,
                hovertemplate=f"<b>{mc['label']}</b><br>NDVI: {avg_ndvi:.3f}<extra></extra>"))
        fig_veg_map.update_layout(**base_layout("🌿 India Vegetation Map (Satellite NDVI View)", h=500))
        st.plotly_chart(fig_veg_map, use_container_width=True)
    with v2:
        st.markdown("#### Mine Vegetation")
        for mn,mc in MINE_COORDS.items():
            row = df[df["mine"]==mn]
            if not len(row): continue
            avg_ndvi = row["NDVI"].mean()
            trend = row.sort_values("month")["NDVI"].iloc[-3:].mean()-row.sort_values("month")["NDVI"].iloc[:3].mean()
            badge = "🟢 Healthy" if avg_ndvi>0.35 else ("🟠 Monitor" if avg_ndvi>0.25 else "🔴 ACTION")
            st.markdown(f"""<div style='background:rgba(255,255,255,0.06);padding:10px;border-radius:8px;margin-bottom:8px;'>
            <b>{mc['label']}</b><br>🌱 NDVI: <b>{avg_ndvi:.3f}</b><br>{'📈' if trend>0 else '📉'} Trend: {trend:+.3f}<br>{badge}</div>""",
            unsafe_allow_html=True)

    # NDVI trend chart
    aff_df = df.copy()
    aff_df["date"] = pd.to_datetime(aff_df[["year","month"]].assign(day=1))
    aff_df = aff_df.sort_values("date")
    fig_ndvi = go.Figure()
    cols_map = {"Balaghat_MP":"#2ecc71","Nagpur_Maharashtra":"#3498db","Bhandara_Maharashtra":"#e67e22","Gujarat_Pani_ExplorationZone":"#9b59b6"}
    for mn,grp in aff_df.groupby("mine"):
        fig_ndvi.add_trace(go.Scatter(x=grp["date"],y=grp["NDVI"],mode="lines+markers",
            name=MINE_COORDS.get(mn,{}).get("label",mn),
            line=dict(color=cols_map.get(mn,"#fff"),width=2),marker=dict(size=4)))
    fig_ndvi.add_hline(y=0.20,line_dash="dash",line_color="red",annotation_text="🔴 Critical (0.20)")
    fig_ndvi.add_hline(y=0.30,line_dash="dot",line_color="orange",annotation_text="🟠 Warning (0.30)")
    fig_ndvi.update_layout(height=320,xaxis_title="Month",yaxis_title="NDVI",
        plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h",y=1.1),yaxis=dict(range=[0,0.7]))
    st.plotly_chart(fig_ndvi, use_container_width=True)

    # ── Afforestation & Plantation
    st.markdown("---")
    st.markdown("### 🌱 Afforestation & Plantation")
    st.markdown(
        "<div class='moil-proto-note'>ℹ️ Plantation figures below are prototype/demo values used for "
        "illustration. They are not official MOIL statistics.</div>", unsafe_allow_html=True)

    tot_target  = sum(v["target"] for v in PLANTATION_DATA.values())
    tot_planted = sum(v["planted"] for v in PLANTATION_DATA.values())
    tot_remaining, tot_progress = plantation_metrics(tot_target, tot_planted)
    avg_survival = round(np.mean([v["survival_rate"] for v in PLANTATION_DATA.values()]), 1)

    p1,p2,p3,p4,p5 = st.columns(5)
    p1.metric("🌳 Total Plantation Target", f"{tot_target:,.0f}")
    p2.metric("🌱 Plants/Trees Planted", f"{tot_planted:,.0f}")
    p3.metric("⏳ Remaining", f"{tot_remaining:,.0f}")
    p4.metric("📈 Plantation Progress", f"{tot_progress:.0f}%")
    p5.metric("🌿 Avg. Survival Rate", f"{avg_survival:.0f}%")

    pv1, pv2 = st.columns([1.4,1])
    with pv1:
        st.markdown("#### Plantation Target vs Planted (Mine-wise)")
        mine_names = [MINE_COORDS.get(m,{}).get("label", m) for m in PLANTATION_DATA.keys()]
        targets = [v["target"] for v in PLANTATION_DATA.values()]
        planted = [v["planted"] for v in PLANTATION_DATA.values()]
        fig_plant = go.Figure()
        fig_plant.add_trace(go.Bar(name="Target", x=mine_names, y=targets, marker_color="rgba(52,152,219,0.6)"))
        fig_plant.add_trace(go.Bar(name="Planted", x=mine_names, y=planted, marker_color="rgba(46,204,113,0.85)"))
        fig_plant.update_layout(barmode="group", height=320, plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h", y=1.12),
            yaxis_title="Plants / Trees")
        st.plotly_chart(fig_plant, use_container_width=True)
    with pv2:
        st.markdown("#### Mine-wise Plantation Progress")
        for m, v in PLANTATION_DATA.items():
            lbl = MINE_COORDS.get(m, {}).get("label", m)
            remaining, progress = plantation_metrics(v["target"], v["planted"])
            status = "🟢 On Track" if progress >= 70 else ("🟠 Behind Schedule" if progress >= 40 else "🔴 Needs Attention")
            st.markdown(f"""<div style='background:rgba(255,255,255,0.06);padding:10px;border-radius:8px;margin-bottom:8px;'>
            <b>{lbl}</b><br>🌳 Target: <b>{v['target']:,.0f}</b> · 🌱 Planted: <b>{v['planted']:,.0f}</b><br>
            ⏳ Remaining: <b>{remaining:,.0f}</b> · 📈 Progress: <b>{progress:.0f}%</b><br>
            🌿 Survival: <b>{v['survival_rate']}%</b> &nbsp; {status}</div>""", unsafe_allow_html=True)


# ── Soil Moisture Tab
# NOTE: This tab was previously reading straight from the full, unfiltered `df`,
# so it ignored the Mine/Year sidebar selectors entirely and showed the same
# figures no matter what was selected. It now derives every number from
# `df` filtered by the *actual* selected_mine / selected_year (mirroring the
# `filtered_df` pattern used elsewhere), so the cards and chart genuinely
# change with the selectors and there is no random/non-deterministic value —
# every number is a real aggregate pulled from manganese_final_dataset.csv.
with tab_soil:
    st.markdown(f"### {T['soil_title']}")
    st.markdown(T["soil_subtitle"])

    def _sm_pct(series):
        return (series / 0.5 * 100).clip(upper=100)

    # Which mine(s) to show cards for — respects the sidebar Mine filter.
    mines_to_show = list(MINE_COORDS.keys()) if selected_mine == T["all_mines"] else [selected_mine]
    soil_cards = st.columns(len(mines_to_show))

    for i, mn in enumerate(mines_to_show):
        mc_info = MINE_COORDS.get(mn)
        if mc_info is None:
            continue
        # Year-filtered rows for THIS mine (independent of the mine loop,
        # but always respecting the selected_year filter).
        mine_rows = df[df["mine"] == mn]
        if selected_year != T["all_years"]:
            mine_rows = mine_rows[mine_rows["year"] == int(selected_year)]

        with soil_cards[i]:
            if mine_rows.empty:
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.06);border:2px solid #555;
                border-radius:12px;padding:16px;text-align:center;'>
                <div style='font-size:13px;font-weight:bold;color:white;'>{mc_info["label"]}</div>
                <div style='font-size:12px;color:#aaa;margin-top:10px;'>{T["no_soil_data"]}</div>
                </div>""", unsafe_allow_html=True)
                continue

            avg_sm = mine_rows["SoilMoisture"].mean()
            latest_row = mine_rows.sort_values(["year", "month"]).iloc[-1]
            latest_sm = latest_row["SoilMoisture"]
            # Convert to percentage (SMAP volumetric water content 0-0.5 → 0-100%)
            sm_pct = min(100, round(latest_sm / 0.5 * 100, 1))
            sm_avg_pct = min(100, round(avg_sm / 0.5 * 100, 1))
            period_txt = (str(int(selected_year)) if selected_year != T["all_years"]
                          else f"{int(mine_rows['year'].min())}–{int(mine_rows['year'].max())}")

            if sm_pct < 50:
                status_color, status_icon = "#2ecc71", "🟢"
                status_text, ops_msg = T["status_optimal"], T["ops_safe"]
            elif sm_pct <= 75:
                status_color, status_icon = "#f1c40f", "🟡"
                status_text, ops_msg = T["status_moderate"], T["ops_monitor"]
            else:
                status_color, status_icon = "#e74c3c", "🔴"
                status_text, ops_msg = T["status_high"], T["ops_halt"]

            st.markdown(f"""
            <div style='background:rgba(255,255,255,0.06);border:2px solid {status_color};
            border-radius:12px;padding:16px;text-align:center;'>
            <div style='font-size:13px;font-weight:bold;color:white;'>{mc_info["label"]}</div>
            <div style='font-size:10px;color:#888;'>{T["period_label"]}: {period_txt} · {T["latest_label"]}: {int(latest_row["month"])}/{int(latest_row["year"])}</div>
            <div style='font-size:36px;margin:8px 0;'>{status_icon}</div>
            <div style='font-size:28px;font-weight:bold;color:{status_color};'>{sm_pct}%</div>
            <div style='font-size:11px;color:#aaa;'>{T["saturation_level"]}</div>
            <div style='background:{status_color};color:black;border-radius:6px;padding:4px 8px;
            margin:8px 0;font-size:11px;font-weight:bold;'>{status_text}</div>
            <div style='font-size:11px;color:#ddd;'>{ops_msg}</div>
            <div style='font-size:10px;color:#888;margin-top:6px;'>{T["avg_label"]}: {sm_avg_pct}% | {T["latest_label"]}: {sm_pct}%</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Trend chart:
    #  - Year = "All Years" → historical trend across years (mine filter still applies)
    #  - a specific Year selected → monthly trend WITHIN that year only, for the
    #    selected mine(s), so the chart never silently mixes in other years/mines.
    sm_colors = {"Balaghat_MP": "#2ecc71", "Nagpur_Maharashtra": "#3498db",
                 "Bhandara_Maharashtra": "#e67e22", "Gujarat_Pani_ExplorationZone": "#9b59b6"}
    mine_scope_df = df if selected_mine == T["all_mines"] else df[df["mine"] == selected_mine]

    fig_sm = go.Figure()
    if selected_year == T["all_years"]:
        st.markdown(f"#### {T['trend_title']}")
        sm_df = mine_scope_df.copy()
        sm_df["date"] = pd.to_datetime(sm_df[["year", "month"]].assign(day=1))
        sm_df = sm_df.sort_values("date")
        sm_df["sm_pct"] = _sm_pct(sm_df["SoilMoisture"])
        for mine_name, grp in sm_df.groupby("mine"):
            lbl = MINE_COORDS.get(mine_name, {}).get("label", mine_name)
            fig_sm.add_trace(go.Scatter(
                x=grp["date"], y=grp["sm_pct"], mode="lines+markers", name=lbl,
                line=dict(color=sm_colors.get(mine_name, "#fff"), width=2), marker=dict(size=4),
                hovertemplate=f"<b>{lbl}</b><br>{T['chart_sm_axis']}: %{{y:.1f}}%<extra></extra>"))
        x_title = T["chart_month_axis"]
    else:
        st.markdown(f"#### {T['trend_title_year']}")
        sm_df = mine_scope_df[mine_scope_df["year"] == int(selected_year)].copy()
        sm_df["sm_pct"] = _sm_pct(sm_df["SoilMoisture"])
        sm_df = sm_df.sort_values("month")
        for mine_name, grp in sm_df.groupby("mine"):
            lbl = MINE_COORDS.get(mine_name, {}).get("label", mine_name)
            fig_sm.add_trace(go.Scatter(
                x=grp["month"], y=grp["sm_pct"], mode="lines+markers", name=lbl,
                line=dict(color=sm_colors.get(mine_name, "#fff"), width=2), marker=dict(size=6),
                hovertemplate=f"<b>{lbl}</b><br>{T['chart_sm_axis']}: %{{y:.1f}}%<extra></extra>"))
        x_title = T["chart_month_axis"]

    if len(fig_sm.data) == 0:
        st.info(T["no_soil_data"])
    else:
        fig_sm.add_hrect(y0=0, y1=50, fillcolor="rgba(46,204,113,0.08)", line_width=0)
        fig_sm.add_hrect(y0=50, y1=75, fillcolor="rgba(241,196,15,0.08)", line_width=0)
        fig_sm.add_hrect(y0=75, y1=100, fillcolor="rgba(231,76,60,0.08)", line_width=0)
        fig_sm.add_hline(y=50, line_dash="dash", line_color="#f1c40f")
        fig_sm.add_hline(y=75, line_dash="dash", line_color="#e74c3c")
        fig_sm.update_layout(
            height=380, xaxis_title=x_title, yaxis_title=T["chart_sm_axis"],
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=1.1), yaxis=dict(range=[0, 105])
        )
        st.plotly_chart(fig_sm, use_container_width=True)

    st.markdown(
        f"<div class='moil-proto-note'>ℹ️ {T['soil']}: NASA SMAP-derived values from the underlying dataset, "
        f"filtered live to the Mine/Year selected in the sidebar.</div>", unsafe_allow_html=True)

    # Traffic light legend
    leg1, leg2, leg3 = st.columns(3)
    leg1.success(T["legend_low"])
    leg2.warning(T["legend_mod"])
    leg3.error(T["legend_high"])


# ── Weather Tab
with tab_wx:
    st.markdown("### 🌧️ 7-Day Weather Forecast — MOIL Mine Regions")
    heavy = [w for w in weather_data if w["rain"]>25]
    if heavy:
        for w in heavy:
            st.error(f"🚨 **RAIN ALERT — {w['date']}**: {w['rain']}mm expected. {w['impact']}")
    wcols = st.columns(7)
    for col,w in zip(wcols,weather_data):
        bg = "rgba(231,76,60,0.2)" if w["alert"] else "rgba(255,255,255,0.05)"
        bdr = "#e74c3c" if w["alert"] else "rgba(255,255,255,0.1)"
        col.markdown(f"""<div style='background:{bg};padding:10px;border-radius:10px;text-align:center;border:1px solid {bdr};'>
        <div style='font-size:11px;color:#aaa;'>{w['date']}</div>
        <div style='font-size:24px;margin:4px 0'>{w['cond'].split()[0]}</div>
        <div style='font-size:18px;font-weight:bold;color:{"#e74c3c" if w["alert"] else "#2ecc71"}'>{w['temp']}°C</div>
        <div style='font-size:11px;color:#74b9ff'>💧 {w['rain']}mm</div>
        <div style='font-size:11px;color:#aaa'>💦 {w['hum']}%</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("---")
    rains = [w["rain"] for w in weather_data]
    dates = [w["date"] for w in weather_data]
    bcs = ["#e74c3c" if r>25 else ("#f39c12" if r>10 else "#3498db") for r in rains]
    fig_wx = go.Figure()
    fig_wx.add_trace(go.Bar(x=dates,y=rains,marker_color=bcs,text=[f"{r}mm" for r in rains],textposition="outside"))
    fig_wx.add_hline(y=25,line_dash="dash",line_color="red",annotation_text="⚠️ Heavy rain (25mm)")
    fig_wx.add_hline(y=10,line_dash="dot",line_color="orange",annotation_text="⚡ Moderate (10mm)")
    fig_wx.update_layout(height=300,xaxis_title="Day",yaxis_title="Rainfall (mm)",
        plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",showlegend=False)
    st.plotly_chart(fig_wx, use_container_width=True)
    wx1,wx2,wx3 = st.columns(3)
    wx1.metric("☔ 7-day Total Rainfall", f"{sum(rains):.1f} mm")
    wx2.metric("🚨 High-Rain Days", sum(1 for r in rains if r>25))
    wx3.metric("🌡️ Avg Temperature", f"{sum(w['temp'] for w in weather_data)/7:.1f}°C")

st.markdown("---")

# ═══════════════════════════════════════════
# PRODUCTION ANALYTICS
# ═══════════════════════════════════════════
st.subheader(T["production_trend"])

# ── 3-way KPI cards
trend_df = filtered_df.copy()
trend_df["date"] = pd.to_datetime(trend_df[["year","month"]].assign(day=1))
trend_df = trend_df.sort_values("date")
if selected_mine == T["all_mines"]:
    t_agg = trend_df.groupby("date")[["production_tons","predicted_production"]].sum().reset_index()
else:
    t_agg = trend_df[["date","production_tons","predicted_production"]].copy()

avg_actual    = t_agg["production_tons"].mean()
avg_predicted = t_agg["predicted_production"].mean()
avg_target    = avg_actual * 1.12  # 12% above historical = planned quota
t_agg["target"] = avg_target

actual_vs_target   = avg_actual - avg_target
predicted_vs_target= avg_predicted - avg_target

kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    delta_color = "normal" if actual_vs_target >= 0 else "inverse"
    st.metric("🎯 Target Production (Planned)", f"{avg_target:,.0f} tons/mo", help="Official planned quota per month")
with kpi2:
    badge = "🟢 SURPLUS" if actual_vs_target>=0 else "🔴 SHORTFALL"
    st.metric("⛏️ Achieved Production", f"{avg_actual:,.0f} tons/mo",
              delta=f"{actual_vs_target:+,.0f} tons ({actual_vs_target/avg_target*100:+.1f}%)")
with kpi3:
    badge2 = "🟢 On Track" if predicted_vs_target>=0 else "🟠 Below Target"
    st.metric("🔮 AI Predicted Production", f"{avg_predicted:,.0f} tons/mo",
              delta=f"{predicted_vs_target:+,.0f} tons ({predicted_vs_target/avg_target*100:+.1f}%)")

# ── Grouped 3-bar chart
fig_trend = go.Figure()
fig_trend.add_trace(go.Bar(
    name="🎯 Target", x=t_agg["date"], y=t_agg["target"],
    marker_color="rgba(52,152,219,0.7)",
    hovertemplate="<b>Target</b><br>%{x|%b %Y}: %{y:,.0f} tons<extra></extra>"
))
fig_trend.add_trace(go.Bar(
    name="⛏️ Achieved", x=t_agg["date"], y=t_agg["production_tons"],
    marker_color="rgba(46,204,113,0.85)",
    hovertemplate="<b>Achieved</b><br>%{x|%b %Y}: %{y:,.0f} tons<extra></extra>"
))
fig_trend.add_trace(go.Bar(
    name="🔮 Predicted (AI)", x=t_agg["date"], y=t_agg["predicted_production"],
    marker_color="rgba(230,126,34,0.85)",
    hovertemplate="<b>AI Predicted</b><br>%{x|%b %Y}: %{y:,.0f} tons<extra></extra>"
))
fig_trend.update_layout(
    barmode="group", height=420,
    xaxis_title="Month", yaxis_title=T["production"],
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", y=1.05),
    bargap=0.15, bargroupgap=0.05
)
st.plotly_chart(fig_trend, use_container_width=True)
st.markdown("---")


# ═══════════════════════════════════════════
# RISK + ALERTS
# ═══════════════════════════════════════════
col_l,col_r = st.columns([1,2])
with col_l:
    st.subheader(T["risk_dist"])
    rc = filtered_df["shortfall_risk"].value_counts().reset_index()
    rc.columns = ["Risk","Count"]
    fig_pie = go.Figure(go.Pie(labels=rc["Risk"],values=rc["Count"],hole=0.45,
        marker_colors=["#2ecc71" if r=="Low Risk" else ("#f39c12" if r=="Medium Risk" else "#e74c3c") for r in rc["Risk"]]))
    fig_pie.update_layout(height=300,paper_bgcolor="rgba(0,0,0,0)",legend=dict(orientation="h",y=-0.2))
    st.plotly_chart(fig_pie, use_container_width=True)
with col_r:
    st.subheader(T["alerts"])
    alerts_df = filtered_df[filtered_df["shortfall_risk"]!="Low Risk"].sort_values(["year","month"],ascending=False)
    if alerts_df.empty:
        st.success(T["no_alerts"])
    else:
        for _,row in alerts_df.head(6).iterrows():
            icon = "🔴" if row["shortfall_risk"]=="High Risk" else "🟠"
            pct = row.get("shortfall_pct",0)
            st.markdown(f"**{icon} {row['mine']} — {int(row['month']):02d}/{int(row['year'])}** | {row['shortfall_risk']} ({pct:.1f}% below target)")
            st.caption(row["recommendation"])
st.markdown("---")

# ═══════════════════════════════════════════
# OPERATIONAL DELAY & BOTTLENECK RADAR
# ═══════════════════════════════════════════
st.subheader("🚨 Production Delays & Operational Bottlenecks")
st.markdown("Instant visual diagnosis of the three primary production loss drivers — executives can spot the cause in seconds.")

bt1, bt2, bt3 = st.columns(3)

# ── Compute bottleneck metrics from filtered data
total_blast_days  = filtered_df["blasting_delay_days"].sum()
avg_blast_days    = filtered_df["blasting_delay_days"].mean()
blast_tons_lost   = round(total_blast_days * 420, 0)   # ~420 tons lost per delay day

total_rain_mm     = filtered_df["Rainfall_mm"].sum()
avg_rain_mm       = filtered_df["Rainfall_mm"].mean()
heavy_rain_months = int((filtered_df["Rainfall_mm"] > 200).sum())
rain_tons_lost    = round(heavy_rain_months * 1850, 0)

total_downtime    = filtered_df["equipment_downtime_hours"].sum()
avg_downtime      = filtered_df["equipment_downtime_hours"].mean()
downtime_tons_lost= round(total_downtime * 38, 0)      # ~38 tons lost per downtime hour

max_blast  = 30   # max scale for progress bars
max_rain   = 300
max_down   = 60

with bt1:
    blast_pct = min(100, int(avg_blast_days / max_blast * 100))
    blast_color = "#e74c3c" if blast_pct > 60 else ("#f39c12" if blast_pct > 30 else "#2ecc71")
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.05);border:1px solid {blast_color};border-radius:12px;padding:16px;'>
    <div style='font-size:22px;font-weight:bold;'>💥 Blasting Delays</div>
    <div style='font-size:32px;font-weight:bold;color:{blast_color};margin:8px 0;'>{avg_blast_days:.1f} days/mo</div>
    <div style='font-size:12px;color:#aaa;margin-bottom:8px;'>Avg delay days per month across selected mines</div>
    <div style='background:rgba(255,255,255,0.1);border-radius:6px;height:18px;margin-bottom:8px;'>
      <div style='background:{blast_color};width:{blast_pct}%;height:18px;border-radius:6px;'></div>
    </div>
    <div style='font-size:13px;'>📦 Est. Tons Lost: <b style='color:{blast_color};'>{blast_tons_lost:,.0f} tons</b></div>
    <div style='font-size:11px;color:#aaa;margin-top:4px;'>Causes: Weather clearance, misfires, shift delays</div>
    <div style='margin-top:10px;background:rgba(255,255,255,0.08);border-radius:6px;padding:8px;font-size:11px;'>
    💡 <b>Fix:</b> Reschedule blasting to 06:00–09:00 IST dry windows. Pre-position charges during clear weather.
    </div></div>""", unsafe_allow_html=True)

with bt2:
    rain_pct = min(100, int(avg_rain_mm / max_rain * 100))
    rain_color = "#e74c3c" if rain_pct > 60 else ("#f39c12" if rain_pct > 30 else "#2ecc71")
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.05);border:1px solid {rain_color};border-radius:12px;padding:16px;'>
    <div style='font-size:22px;font-weight:bold;'>🌧️ Rainfall Disruptions</div>
    <div style='font-size:32px;font-weight:bold;color:{rain_color};margin:8px 0;'>{avg_rain_mm:.0f} mm/mo</div>
    <div style='font-size:12px;color:#aaa;margin-bottom:8px;'>Avg monthly rainfall across selected mines</div>
    <div style='background:rgba(255,255,255,0.1);border-radius:6px;height:18px;margin-bottom:8px;'>
      <div style='background:{rain_color};width:{rain_pct}%;height:18px;border-radius:6px;'></div>
    </div>
    <div style='font-size:13px;'>📦 Est. Tons Lost: <b style='color:{rain_color};'>{rain_tons_lost:,.0f} tons</b></div>
    <div style='font-size:11px;color:#aaa;margin-top:4px;'>{heavy_rain_months} months with >200mm rain (flooded bench risk)</div>
    <div style='margin-top:10px;background:rgba(255,255,255,0.08);border-radius:6px;padding:8px;font-size:11px;'>
    💡 <b>Fix:</b> Activate sump pumps before monsoon. Shift operations to underground faces during peak rain.
    </div></div>""", unsafe_allow_html=True)

with bt3:
    down_pct = min(100, int(avg_downtime / max_down * 100))
    down_color = "#e74c3c" if down_pct > 60 else ("#f39c12" if down_pct > 30 else "#2ecc71")
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.05);border:1px solid {down_color};border-radius:12px;padding:16px;'>
    <div style='font-size:22px;font-weight:bold;'>⚙️ Equipment Downtime</div>
    <div style='font-size:32px;font-weight:bold;color:{down_color};margin:8px 0;'>{avg_downtime:.1f} hrs/mo</div>
    <div style='font-size:12px;color:#aaa;margin-bottom:8px;'>Avg downtime per month (excavators + dumpers)</div>
    <div style='background:rgba(255,255,255,0.1);border-radius:6px;height:18px;margin-bottom:8px;'>
      <div style='background:{down_color};width:{down_pct}%;height:18px;border-radius:6px;'></div>
    </div>
    <div style='font-size:13px;'>📦 Est. Tons Lost: <b style='color:{down_color};'>{downtime_tons_lost:,.0f} tons</b></div>
    <div style='font-size:11px;color:#aaa;margin-top:4px;'>Total downtime hours in selection: {total_downtime:,.0f} hrs</div>
    <div style='margin-top:10px;background:rgba(255,255,255,0.08);border-radius:6px;padding:8px;font-size:11px;'>
    💡 <b>Fix:</b> Redeploy idle DU-02 from Nagpur. Schedule preventive maintenance pre-monsoon (April/May).
    </div></div>""", unsafe_allow_html=True)

# ── Summary impact bar
st.markdown("---")
total_lost = blast_tons_lost + rain_tons_lost + downtime_tons_lost
total_prod = filtered_df["production_tons"].sum()
loss_pct = round(total_lost / (total_prod + total_lost) * 100, 1)
impact_col1, impact_col2, impact_col3, impact_col4 = st.columns(4)
impact_col1.metric("💥 Blasting Loss", f"{blast_tons_lost:,.0f} tons", delta=f"{blast_tons_lost/(total_lost)*100:.0f}% of losses", delta_color="inverse")
impact_col2.metric("🌧️ Rainfall Loss", f"{rain_tons_lost:,.0f} tons", delta=f"{rain_tons_lost/(total_lost)*100:.0f}% of losses", delta_color="inverse")
impact_col3.metric("⚙️ Downtime Loss", f"{downtime_tons_lost:,.0f} tons", delta=f"{downtime_tons_lost/(total_lost)*100:.0f}% of losses", delta_color="inverse")
impact_col4.metric("📉 Total Est. Loss", f"{total_lost:,.0f} tons", delta=f"{loss_pct}% of potential output", delta_color="inverse")
st.markdown("---")


# ═══════════════════════════════════════════
# FLEET & EQUIPMENT
# ═══════════════════════════════════════════
st.subheader(T["fleet_title"])
fleet_cols = st.columns(5)
status_color = {"Active":"#2ecc71","Idle":"#f39c12","Maintenance":"#e67e22","Breakdown":"#e74c3c"}
for i,eq in enumerate(FLEET_DATA):
    with fleet_cols[i%5]:
        sc = status_color.get(eq["status"],"#aaa")
        fuel_color = "#e74c3c" if eq["fuel"]<40 else ("#f39c12" if eq["fuel"]<60 else "#2ecc71")
        st.markdown(f"""<div style='background:rgba(255,255,255,0.06);border:1px solid {sc};padding:10px;border-radius:10px;margin-bottom:8px;'>
        <div style='font-size:13px;font-weight:bold;color:white;'>{eq['id']} — {eq['type']}</div>
        <div style='font-size:11px;color:#aaa;'>📍 {eq['mine']}</div>
        <div style='margin:5px 0;'>
          <span style='background:{sc};color:black;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:bold;'>{eq['status']}</span>
        </div>
        <div style='font-size:11px;'>⛽ Fuel: <span style='color:{fuel_color};font-weight:bold;'>{eq['fuel']}%</span></div>
        <div style='font-size:11px;'>⚙️ OEE: <b>{eq['oee']}%</b></div>
        <div style='font-size:10px;color:#888;'>🔧 {eq['next_maint']}</div>
        </div>""", unsafe_allow_html=True)

# Fleet recommendations
idle_eq = [f for f in FLEET_DATA if f["status"]=="Idle"]
broken_eq = [f for f in FLEET_DATA if f["status"]=="Breakdown"]
if idle_eq or broken_eq:
    st.markdown("#### 🚛 Fleet Redeployment Recommendations (AI)")
    for eq in idle_eq:
        st.info(f"💡 **{eq['id']}** ({eq['type']}) is IDLE at {eq['mine']}. Consider redeploying to Balaghat or Bhandara to recover lost tonnage from equipment shortfalls.")
    for eq in broken_eq:
        st.error(f"🚨 **{eq['id']}** ({eq['type']}) BREAKDOWN at {eq['mine']}. Dispatch maintenance crew immediately. Redirect haul routes to avoid {eq['mine']} pit dependency until repair complete.")
st.markdown("---")

# ═══════════════════════════════════════════
# ORE GRADE BLENDING
# ═══════════════════════════════════════════
st.subheader(T["blending_title"])
st.markdown("When high-grade pits are inaccessible (rain/downtime), the system recommends blending from secondary stockpiles to maintain required Mn% grade.")
b1,b2,b3 = st.columns(3)
blending_scenarios = [
    {"mine":"Balaghat (Block-1)","primary_mn":44.5,"stockpile_mn":28.0,"target_mn":38.0,"primary_pct":67,"stockpile_pct":33,"status":"Inaccessible (Rain)"},
    {"mine":"Nagpur (Pit-A)","primary_mn":32.8,"stockpile_mn":24.0,"target_mn":30.0,"primary_pct":73,"stockpile_pct":27,"status":"EX-02 Maintenance"},
    {"mine":"Bhandara (Block-3)","primary_mn":31.0,"stockpile_mn":22.5,"target_mn":28.0,"primary_pct":62,"stockpile_pct":38,"status":"Normal Ops"},
]
for col,(b) in zip([b1,b2,b3],blending_scenarios):
    with col:
        achieved = b["primary_mn"]*(b["primary_pct"]/100) + b["stockpile_mn"]*(b["stockpile_pct"]/100)
        ok = achieved >= b["target_mn"]*0.98
        st.markdown(f"""<div style='background:rgba(255,255,255,0.06);border:1px solid {"#2ecc71" if ok else "#e74c3c"};padding:14px;border-radius:10px;'>
        <b>⛏️ {b['mine']}</b><br>
        <span style='font-size:11px;color:#aaa;'>Status: {b['status']}</span><br><br>
        🟦 Primary ore: <b>{b['primary_mn']}% Mn</b> @ {b['primary_pct']}%<br>
        🟨 Stockpile: <b>{b['stockpile_mn']}% Mn</b> @ {b['stockpile_pct']}%<br>
        🎯 Target grade: <b>{b['target_mn']}% Mn</b><br>
        ✅ Achieved: <b style='color:{"#2ecc71" if ok else "#e74c3c"}'>{achieved:.1f}% Mn</b><br>
        <span style='font-size:12px;font-weight:bold;color:{"#2ecc71" if ok else "#e74c3c"};'>{"✅ TARGET ACHIEVED" if ok else "⚠️ TARGET NOT ACHIEVED — increase primary ratio"}</span>
        </div>""", unsafe_allow_html=True)
st.markdown("---")


# ═══════════════════════════════════════════
# ORE GRADE QUALITY PANEL
# ═══════════════════════════════════════════
st.subheader("⚗️ Manganese Ore Grade Quality Analysis")
st.markdown("Classifying reserves by Mn% grade. End-use suitability depends on mineral chemistry, impurities, "
            "mineralogy, processing and specification requirements — Mn% alone does not determine suitability.")

grade_col1, grade_col2, grade_col3 = st.columns([1,1,2])

# Grade classification data
grade_data = {
    "High Grade (>44% Mn)":    {"mt": sum(z[5] for z in MANGANESE_ZONES if z[6]>44),  "color":"#00ff88", "use":"⚙️ " + GRADE_USE_TEXT["High Grade"]},
    "Medium Grade (35-44% Mn)":{"mt": sum(z[5] for z in MANGANESE_ZONES if 35<=z[6]<=44),"color":"#f1c40f","use":"🏭 " + GRADE_USE_TEXT["Medium Grade"]},
    "Low Grade (25-35% Mn)":   {"mt": sum(z[5] for z in MANGANESE_ZONES if 25<=z[6]<35), "color":"#e67e22","use":"🔋 " + GRADE_USE_TEXT["Low Grade"]},
    "Very Low (<25% Mn)":      {"mt": sum(z[5] for z in MANGANESE_ZONES if z[6]<25),  "color":"#e74c3c", "use":"🔧 " + GRADE_USE_TEXT["Very Low Grade"]},
}

# Clear summary table: Grade Category | Mn Range | Zones | Estimated Tonnage | Share
_total_tonnage_all = sum(z[5] for z in MANGANESE_ZONES) or 1
_grade_ranges = {
    "High Grade (>44% Mn)": ">44%", "Medium Grade (35-44% Mn)": "35–44%",
    "Low Grade (25-35% Mn)": "25–35%", "Very Low (<25% Mn)": "<25%",
}
_grade_zone_counts = {
    "High Grade (>44% Mn)": sum(1 for z in MANGANESE_ZONES if z[6]>44),
    "Medium Grade (35-44% Mn)": sum(1 for z in MANGANESE_ZONES if 35<=z[6]<=44),
    "Low Grade (25-35% Mn)": sum(1 for z in MANGANESE_ZONES if 25<=z[6]<35),
    "Very Low (<25% Mn)": sum(1 for z in MANGANESE_ZONES if z[6]<25),
}
grade_table_rows = [{
    "Grade Category": g.split(" (")[0],
    "Mn Range": _grade_ranges[g],
    "Zones": _grade_zone_counts[g],
    "Estimated Tonnage (MT)": round(v["mt"], 1),
    "Share of Total": f"{v['mt']/_total_tonnage_all*100:.1f}%",
} for g, v in grade_data.items()]
st.markdown("#### 📋 Grade Category Summary")
st.dataframe(pd.DataFrame(grade_table_rows), use_container_width=True, hide_index=True)

with grade_col1:
    # Pie chart
    fig_grade_pie = go.Figure(go.Pie(
        labels=list(grade_data.keys()),
        values=[v["mt"] for v in grade_data.values()],
        hole=0.45,
        marker_colors=[v["color"] for v in grade_data.values()],
        textinfo="label+percent",
        textfont=dict(size=9),
        hovertemplate="<b>%{label}</b><br>Reserves: %{value:.1f} MT<br>Share: %{percent}<extra></extra>"
    ))
    fig_grade_pie.update_layout(height=320,paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,margin=dict(t=10,b=10,l=10,r=10),
        title=dict(text="Grade Distribution (MT)",font=dict(size=12,color="white"),x=0.5))
    st.plotly_chart(fig_grade_pie, use_container_width=True)

with grade_col2:
    # Bar chart per mine
    mine_grades = []
    for (zlat,zlon,prob,label,level,tonnage,mn_pct,state) in MANGANESE_ZONES:
        if level in ["high","moderate"]:
            if mn_pct>44: grade="High (>44%)"
            elif mn_pct>35: grade="Medium (35-44%)"
            elif mn_pct>25: grade="Low (25-35%)"
            else: grade="Very Low (<25%)"
            mine_grades.append({"Zone":label.split("(")[0].strip()[:18],"Mn%":mn_pct,"Tonnage":tonnage,"Grade":grade})
    mg_df = pd.DataFrame(mine_grades).sort_values("Mn%",ascending=True)
    grade_colors_map = {"High (>44%)":"#00ff88","Medium (35-44%)":"#f1c40f","Low (25-35%)":"#e67e22","Very Low (<25%)":"#e74c3c"}
    fig_grade_bar = go.Figure()
    fig_grade_bar.add_trace(go.Bar(
        y=mg_df["Zone"],x=mg_df["Mn%"],orientation="h",
        marker_color=[grade_colors_map.get(g,"#aaa") for g in mg_df["Grade"]],
        text=[f"{m}%" for m in mg_df["Mn%"]],textposition="outside",
        hovertemplate="<b>%{y}</b><br>Mn%: %{x}%<extra></extra>"
    ))
    fig_grade_bar.add_vline(x=44,line_dash="dash",line_color="#00ff88",annotation_text="High Grade (44%)")
    fig_grade_bar.add_vline(x=35,line_dash="dot",line_color="#f1c40f",annotation_text="Med Grade (35%)")
    fig_grade_bar.add_vline(x=25,line_dash="dot",line_color="#e67e22",annotation_text="Low Grade (25%)")
    fig_grade_bar.update_layout(height=320,xaxis_title="Mn% Grade",
        plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10,b=10,l=10,r=10),xaxis=dict(range=[0,55]),
        title=dict(text="Mn% Grade by Zone",font=dict(size=12,color="white"),x=0.5))
    st.plotly_chart(fig_grade_bar, use_container_width=True)

with grade_col3:
    st.markdown("#### 🏭 Grade → Industry Suitability")
    for grade_name, gdata in grade_data.items():
        st.markdown(f"""<div style='background:rgba(255,255,255,0.05);border-left:4px solid {gdata["color"]};
        padding:12px;border-radius:6px;margin-bottom:8px;'>
        <b style='color:{gdata["color"]};'>{grade_name}</b><br>
        📦 Available: <b>{gdata["mt"]:.1f} Million Tonnes</b><br>
        {gdata["use"]}
        </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### 💡 Blending Opportunity")
    total_high = sum(z[5] for z in MANGANESE_ZONES if z[6]>44)
    total_low  = sum(z[5] for z in MANGANESE_ZONES if z[6]<35)
    blend_ratio = round(total_high/(total_high+total_low)*100)
    st.info(f"By blending **{blend_ratio}% high-grade** with **{100-blend_ratio}% low-grade** ore, MOIL can work "
            f"toward a consistent 35%+ Mn output across deliveries — subject to actual chemistry and processing "
            f"requirements — maximising utilisation of all reserve grades.")

# ═══════════════════════════════════════════
# SELECTED ZONE — ORE GRADE PANEL
# ═══════════════════════════════════════════
st.markdown("#### 🎯 Selected Zone — Ore Grade Detail")
zone_names = [z[3] for z in MANGANESE_ZONES]
sel_zone_name = st.selectbox("Choose a zone to inspect", zone_names, index=0, key="ore_grade_zone_select")
_z = next(z for z in MANGANESE_ZONES if z[3] == sel_zone_name)
_zlat,_zlon,_zprob,_zlabel,_zlevel,_ztonnage,_zmn,_zstate = _z
_zgrade, _zcolor = grade_category(_zmn)
_ztier, _ = prospectivity_tier(_zprob)
_zconf = max(55, int(_zprob*100)-6)
_zaction = {
    "High Grade": "Prioritize field verification",
    "Medium Grade": "Verify with additional assays; consider blending",
    "Low Grade": "Consider blending or beneficiation studies",
    "Very Low Grade": "Assess economic viability before further investment",
}[_zgrade]
st.markdown(f"""<div style='background:rgba(255,255,255,0.06);border:1px solid {_zcolor};border-radius:12px;
padding:16px;max-width:640px;'>
<div style='font-size:13px;color:#aaa;'>SELECTED ZONE</div>
<div style='font-size:20px;font-weight:bold;color:white;margin-bottom:8px;'>{_zlabel}</div>
<div style='display:flex;flex-wrap:wrap;gap:22px;font-size:13px;'>
<div>Mn Grade<br><b style='font-size:17px;color:{_zcolor};'>{_zmn}%</b></div>
<div>Grade Category<br><b style='font-size:17px;color:{_zcolor};'>{_zgrade}</b></div>
<div>Estimated Tonnage<br><b style='font-size:17px;'>{_ztonnage:.1f} MT</b></div>
<div>Prospectivity<br><b style='font-size:17px;'>{_zprob*100:.0f}/100 ({_ztier})</b></div>
<div>Model Confidence<br><b style='font-size:17px;'>{_zconf}%</b></div>
</div>
<div style='margin-top:10px;font-size:12px;color:#ddd;'>State: {_zstate}</div>
<div style='margin-top:10px;background:rgba(255,255,255,0.08);border-radius:6px;padding:8px;font-size:12px;'>
💡 <b>Recommended Action:</b> {_zaction}
</div></div>""", unsafe_allow_html=True)

st.markdown("---")
# ═══════════════════════════════════════════
# COMPLIANCE
# ═══════════════════════════════════════════
st.subheader(T["compliance_title"])
st.caption("Environmental Indicator — based on prototype thresholds for illustration; not official regulatory limits. Requires Regulatory Verification for compliance decisions.")
mc_df = filtered_df.groupby("mine").agg(
    avg_ndvi=("NDVI","mean"),min_ndvi=("NDVI","min"),
    avg_rain=("Rainfall_mm","mean"),max_rain=("Rainfall_mm","max"),
    avg_temp=("LST_Celsius","mean"),max_temp=("LST_Celsius","max"),
).reset_index()
for _,row in mc_df.iterrows():
    lbl = MINE_COORDS.get(row["mine"],{}).get("label",row["mine"])
    with st.expander(f"📍 {lbl}"):
        c1,c2,c3 = st.columns(3)
        veg = "🔴 INDICATOR: Afforestation Recommended" if row["min_ndvi"]<0.20 else ("🟠 INDICATOR: Monitor Closely" if row["avg_ndvi"]<0.30 else "🟢 INDICATOR: Vegetation Adequate")
        rain = "🔴 INDICATOR: Flood Risk" if row["max_rain"]>500 else ("🟠 INDICATOR: Drainage Attention" if row["avg_rain"]>200 else "🟢 INDICATOR: Normal")
        temp = "🔴 INDICATOR: Severe Heat" if row["max_temp"]>40 else ("🟠 INDICATOR: Elevated Temp" if row["avg_temp"]>35 else "🟢 INDICATOR: Normal")
        c1.markdown(f"**🌱 Vegetation**\n\n{veg}\n\nNDVI avg: `{row['avg_ndvi']:.3f}` | min: `{row['min_ndvi']:.3f}`")
        c2.markdown(f"**🌧️ Rainfall**\n\n{rain}\n\nAvg: `{row['avg_rain']:.0f}mm` | max: `{row['max_rain']:.0f}mm`")
        c3.markdown(f"**🌡️ Temperature**\n\n{temp}\n\nAvg: `{row['avg_temp']:.1f}°C` | max: `{row['max_temp']:.1f}°C`")
        st.caption("Prototype environmental status — requires regulatory verification, not an official compliance ruling.")
st.markdown("---")

# ═══════════════════════════════════════════
# WHAT-IF SIMULATOR
# ═══════════════════════════════════════════
st.subheader(T["simulator_title"])
st.markdown("Simulate operational changes and see predicted impact on production shortfall in real-time.")

s1,s2 = st.columns(2)
with s1:
    sim_mine = st.selectbox("🏭 Select Mine to Simulate", list(MINE_COORDS.keys()),
                            format_func=lambda x: MINE_COORDS[x]["label"])
    extra_excavators = st.slider("➕ Additional Excavators deployed", 0, 5, 0)
    rain_reduction = st.slider("🌧️ Rainfall reduction scenario (mm)", 0, 200, 0, step=10)
    blast_opt = st.slider("💥 Blasting schedule optimization (%)", 0, 50, 0, step=5)

with s2:
    mine_data = filtered_df[filtered_df["mine"]==sim_mine] if sim_mine else filtered_df
    base_prod = mine_data["production_tons"].mean() if len(mine_data)>0 else 10000
    base_shortfall = mine_data[mine_data["shortfall_risk"]=="High Risk"].shape[0]

    # Simulation logic
    excavator_boost = extra_excavators * 0.045  # each excavator adds ~4.5% production
    rain_boost = rain_reduction * 0.0008         # reducing rain reduces disruption
    blast_boost = blast_opt * 0.003              # optimizing blasting adds efficiency
    total_boost = excavator_boost + rain_boost + blast_boost
    new_prod = base_prod * (1 + total_boost)
    new_shortfall_months = max(0, int(base_shortfall * (1 - total_boost*2)))
    recovery_pct = round(total_boost*100, 1)

    st.markdown("#### 📊 Scenario Estimate")
    st.caption("Simplified/demo calculation for illustration — not a guaranteed operational outcome.")
    r1,r2,r3 = st.columns(3)
    r1.metric("📦 Baseline Production", f"{base_prod:,.0f} tons/mo")
    r2.metric("📈 Estimated Production", f"{new_prod:,.0f} tons/mo", delta=f"+{recovery_pct}%")
    r3.metric("⚠️ High-Risk Months", f"{new_shortfall_months}", delta=f"-{base_shortfall-new_shortfall_months} months")

    if total_boost > 0:
        st.success(f"""✅ **Scenario Estimate:**
Adding {extra_excavators} excavators + reducing rain impact by {rain_reduction}mm + {blast_opt}% blast optimization
→ **+{recovery_pct}% estimated production recovery** → Estimated output: **{new_prod:,.0f} tons/month**
→ High-risk months estimated to reduce from **{base_shortfall} → {new_shortfall_months}**
_This is a scenario estimate based on simplified assumptions, not a causal guarantee._""")
    else:
        st.info("👈 Adjust the sliders on the left to generate a scenario estimate.")

    # Comparison chart
    fig_sim = go.Figure()
    fig_sim.add_trace(go.Bar(x=["Baseline","With Changes"],y=[base_prod,new_prod],
        marker_color=["#e74c3c","#2ecc71"],text=[f"{base_prod:,.0f}",f"{new_prod:,.0f}"],textposition="outside"))
    fig_sim.update_layout(height=280,yaxis_title="Production (tons)",
        plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",showlegend=False)
    st.plotly_chart(fig_sim, use_container_width=True)
st.markdown("---")

# ═══════════════════════════════════════════
# AI ASSISTANT
# ═══════════════════════════════════════════
st.subheader(T["ai_title"])
mine_ctx = df.groupby("mine").agg(
    avg_reserve=("reserve_potential_score","mean"), total_prod=("production_tons","sum"),
    high_risk=("shortfall_risk",lambda x:(x=="High Risk").sum()),
    avg_ndvi=("NDVI","mean"), avg_rain=("Rainfall_mm","mean"), avg_temp=("LST_Celsius","mean"),
).reset_index().to_string()

_plant_ctx = "; ".join(
    f"{MINE_COORDS.get(m,{}).get('label',m)}: target {v['target']:,}, planted {v['planted']:,}, "
    f"remaining {plantation_metrics(v['target'],v['planted'])[0]:,.0f}, "
    f"progress {plantation_metrics(v['target'],v['planted'])[1]:.0f}%, survival {v['survival_rate']}%"
    for m, v in PLANTATION_DATA.items()
)

system_prompt = f"""You are an expert AI assistant for MOIL Limited, India's largest manganese ore producer.
Help mine managers understand:
- Manganese prospectivity and geological data (SWIR spectral evidence, borehole assay data) — always describe
  the prospectivity score as a model-estimated score out of 100, NEVER as a measured underground % concentration
  or confirmed reserve.
- Mn grade and grade category (High >44%, Medium 35-44%, Low 25-35%, Very Low <25%) — end-use suitability
  depends on chemistry/processing, not Mn% alone.
- Production shortfall risks and predictions
- Equipment fleet status and redeployment recommendations
- Environmental/vegetation monitoring (NDVI is a vegetation/rehabilitation indicator, not a manganese detector)
- Afforestation & plantation status: target, planted, remaining, progress %, survival rate
- Weather impacts on mining operations
- Ore grade blending recommendations
- What-if scenario estimates (present as estimates, not guarantees)

Real satellite data (NDVI, SWIR, SAR, temperature, soil moisture, rainfall) from Google Earth Engine covers 4 MOIL mines.
Current mine data: {mine_ctx}
Plantation/afforestation data (prototype/demo values, NOT official MOIL statistics): {_plant_ctx}
Key facts: MOIL proven reserves ~53.47 million tonnes (prospectivity-based estimate). FY30 target: 3.5 million tons/year.
Borehole data shows Mn% grades: Balaghat (38-45%), Nagpur (30-33%), Bhandara (31%), Gujarat (19-22%).
Fleet: EX-02 in maintenance at Nagpur. DU-04 breakdown at Nagpur. DU-02 idle at Nagpur.
NEVER present synthetic/demo/prototype values as official MOIL data — always note when a figure is a prototype value.
ANSWER IN THE SAME LANGUAGE the user writes in (Hindi→Hindi, Telugu→Telugu, Marathi→Marathi, Tamil→Tamil, Bengali→Bengali, English→English).
Be specific, data-driven, concise (3-5 sentences max unless asked for more)."""

ai_tab1, ai_tab2 = st.tabs(["💬 "+("Text Chat" if lang=="🇬🇧 English" else "चैट"), T["voice_title"]])

with ai_tab1:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])
    user_input = st.chat_input(T["ai_placeholder"])
    if user_input:
        st.session_state.chat_history.append({"role":"user","content":user_input})
        st.chat_message("user").write(user_input)
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analysing mine data..."):
                try:
                    msgs = [{"role":m["role"],"content":m["content"]} for m in st.session_state.chat_history]
                    payload = json.dumps({"model":"claude-sonnet-4-6","max_tokens":1000,
                        "system":system_prompt,"messages":msgs}).encode("utf-8")
                    req = urllib.request.Request("https://api.anthropic.com/v1/messages",data=payload,
                        headers={"Content-Type":"application/json","anthropic-version":"2023-06-01",
                                 "anthropic-dangerous-direct-browser-access":"true"},method="POST")
                    with urllib.request.urlopen(req) as resp:
                        result = json.loads(resp.read().decode("utf-8"))
                        reply = result["content"][0]["text"]
                except Exception:
                    q = user_input.lower()
                    if "balaghat" in q: reply="Balaghat MP is MOIL's deepest and most productive mine (383m underground). Reserve score 0.92, Mn% grade 38-45% from borehole data. NDVI is healthy at ~0.38. Monsoon months (Jun-Sep) cause 25% production dips — recommend pre-positioning backup excavators before June."
                    elif "nagpur" in q: reply="Nagpur Maharashtra (open-cast, ~45m depth) scores 0.78 reserve potential. Currently experiencing fleet issues: EX-02 in maintenance and DU-04 breakdown. Recommend deploying DU-02 (currently idle) to recover lost tonnage. Mn% grade 30-33%."
                    elif "bhandara" in q: reply="Bhandara Maharashtra (open-cast) scores 0.68 reserve potential with Mn% grade ~31%. Stable operations currently. Vegetation NDVI at 0.42 — healthy. Watch for monsoon drainage issues as it is open-cast."
                    elif "gujarat" in q: reply="Gujarat Pani Exploration Zone (0.62 score) has confirmed 9.51 million tonnes in recent discovery. Boreholes BH-007 and BH-008 show Mn% 19-22% — lower grade than established mines but viable at scale. Two active/planned drill rigs on site."
                    elif "fleet" in q or "equipment" in q or "excavator" in q or "dumper" in q: reply="Current fleet status: DU-04 is in BREAKDOWN at Nagpur — maintenance crew should be dispatched immediately. EX-02 is in scheduled maintenance at Nagpur. DU-02 is IDLE at Nagpur — recommend redeploying it to Balaghat or Bhandara to recover 8-12% tonnage."
                    elif "blend" in q or "grade" in q or "mn%" in q: reply="Current blending recommendation: Balaghat Block-1 is rain-inaccessible — blend 67% primary ore (44.5% Mn) with 33% stockpile (28% Mn) to achieve 38% Mn target grade. Nagpur is on EX-02 maintenance — blend 73%/27% to maintain 30% Mn target."
                    elif "shortfall" in q or "risk" in q: reply="43 high-risk months detected across all mines, concentrated Jun-Sep. 18% average shortfall expected in Nagpur Block-3 due to DU-04 breakdown + EX-02 maintenance + monsoon forecast. Recommend: deploy DU-02, reschedule blasting to dry windows, blend stockpile ore to maintain grade."
                    elif "plantation" in q or "trees" in q or "plants" in q or "afforest" in q:
                        _tp = sum(v["target"] for v in PLANTATION_DATA.values())
                        _pp = sum(v["planted"] for v in PLANTATION_DATA.values())
                        _rem,_prog = plantation_metrics(_tp,_pp)
                        _best = max(PLANTATION_DATA.items(), key=lambda kv: plantation_metrics(kv[1]["target"],kv[1]["planted"])[1])
                        reply=f"Plantation status (prototype/demo data, not official MOIL statistics): Target {_tp:,.0f}, Planted {_pp:,.0f}, Remaining {_rem:,.0f}, Progress {_prog:.0f}%. Highest progress: {MINE_COORDS.get(_best[0],{}).get('label',_best[0])} at {plantation_metrics(_best[1]['target'],_best[1]['planted'])[1]:.0f}%."
                    elif "prospectivity" in q or "potential score" in q: reply="The manganese prospectivity score (0-100) reflects model-estimated potential based on geological, exploration and satellite evidence. It is not a measured underground manganese concentration or a confirmed reserve — field verification and drilling are required for confirmation."
                    elif "grade category" in q or "mn grade" in q or "ore grade" in q: reply="Grade categories: High Grade >44% Mn, Medium Grade 35-44% Mn, Low Grade 25-35% Mn, Very Low Grade <25% Mn. End-use suitability depends on chemistry, impurities, mineralogy and processing — Mn% alone doesn't determine suitability for a specific application."
                    elif "swir" in q or "spectral" in q: reply="SWIR Band 11/12 analysis shows surface spectral signatures consistent with MnO2-bearing rock at Balaghat (highest reflectance), Odisha belts (Keonjhar, Sundargarh), and Karnataka zones. This is surface evidence, not direct underground detection — cross-referenced with borehole data, Balaghat BH-003 shows a 45.1% Mn assay grade, the highest on record."
                    elif "sar" in q or "radar" in q: reply="Sentinel-1 SAR shows a prototype ground-condition indicator around Balaghat's deep underground workings (383m depth). Cloud penetration during monsoon helps assess pit accessibility at Bhandara and Nagpur open-cast sites. No significant anomaly detected in the prototype indicator currently — this does not replace field verification."
                    elif "weather" in q or "rain" in q: reply="Monsoon season (Jun-Sep) brings 200-400mm monthly rainfall to MOIL regions. Current 7-day forecast shows potential heavy rain events. Recommend: reschedule all outdoor blasting to morning dry windows, activate drainage pumps at open-cast sites (Nagpur, Bhandara), and pre-position underground drilling teams at Balaghat."
                    else: reply="I can help with: manganese prospectivity analysis (SWIR/SAR/borehole evidence), ore grade & blending, fleet status and redeployment, production shortfall prediction, environmental/vegetation monitoring, afforestation & plantation progress, weather impacts, and what-if scenario estimates. Which mine or topic would you like to explore?"
                st.write(reply)
                st.session_state.chat_history.append({"role":"assistant","content":reply})

with ai_tab2:
    # Voice recognition/output locale now defaults to whatever language is
    # currently selected in the sidebar, instead of always defaulting to
    # English regardless of the chosen app language.
    _voice_locale_map = {
        "🇬🇧 English": "en-IN", "🇮🇳 हिंदी": "hi-IN", "🌺 తెలుగు": "te-IN",
        "🌸 मराठी": "mr-IN", "🌟 தமிழ்": "ta-IN", "🌊 বাংলা": "bn-IN",
    }
    _cur_locale = _voice_locale_map.get(lang, "en-IN")

    def _voice_opt(value, text):
        sel = " selected" if value == _cur_locale else ""
        return f'<option value="{value}"{sel}>{text}</option>'

    # Built separately (plain string, NOT an f-string) and substituted with a
    # simple .replace() below — the rest of voice_html is raw JS/CSS full of
    # literal `{ }` characters, so it must stay a normal triple-quoted string.
    _lang_options_html = (
        _voice_opt("en-IN", "🇬🇧 English") + _voice_opt("hi-IN", "🇮🇳 हिंदी") +
        _voice_opt("te-IN", "🌺 తెలుగు") + _voice_opt("mr-IN", "🌸 मराठी") +
        _voice_opt("ta-IN", "🌟 தமிழ்") + _voice_opt("bn-IN", "🌊 বাংলা")
    )

    voice_html="""<div style="background:rgba(255,255,255,0.05);border-radius:14px;padding:24px;font-family:sans-serif;">
<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px;">
<button onclick="startL()" id="mic" style="background:#e74c3c;color:white;border:none;border-radius:10px;padding:14px 28px;font-size:16px;cursor:pointer;font-weight:bold;">🎤 Start Listening</button>
<button onclick="stopL()" id="stp" disabled style="background:#7f8c8d;color:white;border:none;border-radius:10px;padding:14px 24px;font-size:16px;cursor:pointer;">⏹ Stop</button>
<button onclick="clr()" style="background:#2c3e50;color:white;border:none;border-radius:10px;padding:14px 20px;font-size:14px;cursor:pointer;">🗑 Clear</button>
<select id="lng" style="background:#2c3e50;color:white;border:1px solid #555;border-radius:10px;padding:10px 14px;font-size:14px;">
__LANG_OPTIONS__
</select></div>
<div id="sts" style="color:#95a5a6;font-size:14px;margin-bottom:12px;">Click Start Listening and speak your question.</div>
<div id="trn" style="background:rgba(0,0,0,0.3);border-radius:8px;padding:14px;min-height:44px;color:#ecf0f1;font-size:15px;margin-bottom:12px;"><i style="color:#7f8c8d">Your question will appear here...</i></div>
<div id="ans" style="background:rgba(46,204,113,0.1);border:1px solid rgba(46,204,113,0.3);border-radius:8px;padding:14px;min-height:44px;color:#ecf0f1;font-size:15px;display:none;"></div></div>
<script>
let r=null,s=window.speechSynthesis;
const KB={balaghat:"Balaghat MP is MOIL's deepest underground mine at 383 metres, with the highest reserve score of 0.92 and Mn grade of 38 to 45 percent. It is the most productive mine with consistent output, except during monsoon from June to September.",
nagpur:"Nagpur Maharashtra scores 0.78 in reserve potential. It currently has equipment issues with Excavator 02 in maintenance and Dumper 04 in breakdown. Deploying the idle Dumper 02 is recommended to recover lost production tonnage.",
bhandara:"Bhandara Maharashtra has reserve potential 0.68 with Mn grade around 31 percent. Operations are currently stable. It is an open-cast mine and requires drainage monitoring during monsoon.",
gujarat:"Gujarat Pani Exploration Zone confirmed 9.51 million tonnes in discovery. Borehole data shows Mn grade 19 to 22 percent. Two drill rigs are currently active. Further drilling recommended to confirm full reserve extent.",
fleet:"Fleet status: Dumper 04 is in breakdown at Nagpur, dispatch maintenance immediately. Excavator 02 is in scheduled maintenance. Dumper 02 is idle at Nagpur and should be redeployed to Balaghat or Bhandara to recover 8 to 12 percent tonnage.",
blend:"Blending recommendation: For Balaghat Block 1 inaccessible due to rain, blend 67 percent primary ore at 44.5 percent Mn with 33 percent stockpile at 28 percent Mn to achieve 38 percent target grade.",
shortfall:"43 high risk months detected across all mines. 18 percent shortfall expected at Nagpur due to equipment breakdown and monsoon rain. Recommend deploying idle dumper, rescheduling blasting, and blending stockpile ore.",
weather:"Monsoon brings 200 to 400 millimetres monthly. Heavy rain events are forecasted. Recommend rescheduling outdoor blasting to dry morning windows and activating drainage pumps at open cast sites.",
swir:"SWIR spectral analysis shows surface signatures consistent with MnO2-bearing rock at Balaghat, Odisha belts, and Karnataka zones. This is surface evidence, not direct underground detection, and is cross-referenced with borehole assay data showing 45 percent Mn grade at Balaghat Borehole 003.",
risk:"Production shortfall risk is highest during monsoon June to September. Equipment downtime is the second key driver. The What-If simulator shows adding 2 excavators gives an estimated 9 percent recovery of lost production — a scenario estimate, not a guarantee.",
plant:"Plantation status is prototype and demo data, not official MOIL statistics. Across all mines the combined plantation target is about 25 thousand plants, with roughly 17 thousand planted so far, giving around 68 percent progress. Balaghat currently shows the highest plantation progress.",
recommend:"Top recommendations: Redeploy Dumper 02 from Nagpur idle to Balaghat. Reschedule Nagpur blasting to avoid rain windows. Begin blending stockpile ore at Balaghat to maintain Mn grade. Monitor Bhandara drainage for monsoon readiness."};
function ga(q){q=q.toLowerCase();
if(q.includes("balaghat"))return KB.balaghat;if(q.includes("nagpur"))return KB.nagpur;
if(q.includes("bhandara"))return KB.bhandara;if(q.includes("gujarat")||q.includes("pani"))return KB.gujarat;
if(q.includes("fleet")||q.includes("equipment")||q.includes("excavator")||q.includes("dumper"))return KB.fleet;
if(q.includes("plant")||q.includes("tree")||q.includes("afforest"))return KB.plant;
if(q.includes("blend")||q.includes("grade")||q.includes("mn"))return KB.blend;
if(q.includes("shortfall")||q.includes("risk"))return KB.shortfall;
if(q.includes("weather")||q.includes("rain")||q.includes("forecast"))return KB.weather;
if(q.includes("swir")||q.includes("spectral")||q.includes("borehole"))return KB.swir;
if(q.includes("recommend")||q.includes("action")||q.includes("suggest"))return KB.recommend;
return "I can answer questions about Balaghat, Nagpur, Bhandara, Gujarat mines, fleet status, ore blending, plantation progress, shortfall risk, weather impact, SWIR spectral data, and recommendations. Please ask about one of these topics.";}
function spk(t){s.cancel();const u=new SpeechSynthesisUtterance(t);u.lang=document.getElementById("lng").value;u.rate=0.95;s.speak(u);}
function startL(){const SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SR){document.getElementById("sts").innerText="Use Google Chrome for voice support.";return;}
r=new SR();r.lang=document.getElementById("lng").value;r.continuous=false;r.interimResults=true;
r.onstart=()=>{document.getElementById("sts").innerText="🔴 Listening...";document.getElementById("mic").disabled=true;document.getElementById("stp").disabled=false;document.getElementById("trn").innerHTML="<i style='color:#e74c3c'>Listening...</i>";document.getElementById("ans").style.display="none";};
r.onresult=(e)=>{let f="",i="";for(let x=e.resultIndex;x<e.results.length;x++){if(e.results[x].isFinal)f+=e.results[x][0].transcript;else i+=e.results[x][0].transcript;}
document.getElementById("trn").innerText=f||i;
if(f){const a=ga(f);const d=document.getElementById("ans");d.style.display="block";d.innerText="🤖 "+a;spk(a);document.getElementById("sts").innerText="✅ Done. Click Start to ask another question.";}};
r.onerror=(e)=>{document.getElementById("sts").innerText="Error: "+e.error;rst();};r.onend=()=>rst();r.start();}
function stopL(){if(r)r.stop();rst();}
function rst(){document.getElementById("mic").disabled=false;document.getElementById("stp").disabled=true;}
function clr(){s.cancel();document.getElementById("trn").innerHTML="<i style='color:#7f8c8d'>Your question will appear here...</i>";document.getElementById("ans").style.display="none";document.getElementById("sts").innerText="Click Start Listening and speak.";}
</script>"""
    voice_html = voice_html.replace("__LANG_OPTIONS__", _lang_options_html)
    st.components.v1.html(voice_html, height=380, scrolling=False)
    st.caption("🎤 Best in Google Chrome. Select your language before speaking.")
st.markdown("---")

# ═══════════════════════════════════════════
# RAW DATA TABLE (MULTILINGUAL HEADERS)
# ═══════════════════════════════════════════
with st.expander(T["raw_data"]):
    disp = filtered_df[[
        "mine","year","month","NDVI","LST_Celsius","SoilMoisture","Rainfall_mm",
        "equipment_downtime_hours","blasting_delay_days",
        "reserve_potential_score","reserve_category",
        "production_tons","predicted_production","shortfall_risk","recommendation"
    ]].copy()
    disp.columns = [
        T["mine"],T["year"],T["month"],T["ndvi"],T["lst"],T["soil"],T["rainfall"],
        T["downtime"],T["blasting"],T["reserve_score"],T["reserve_cat"],
        T["production"],T["pred_production"],T["shortfall"],T["recommendation"]
    ]
    st.dataframe(disp.sort_values([T["mine"],T["year"],T["month"]]), use_container_width=True)

st.markdown("---")
st.caption("⛏️ MOIL Smart Mining Hub · SIH 2026 · Problem Statement 26009 · Ministry of Steel / MOIL Ltd. · Data: Google Earth Engine (Sentinel-2, Sentinel-1 SAR, MODIS, SMAP, CHIRPS)")
st.caption("Prototype uses simulated/demo operational and exploration values where validated MOIL data is unavailable. "
           "The system is designed for integration with validated MOIL datasets.")
