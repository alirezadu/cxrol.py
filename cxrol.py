 import streamlit as st
import random
import base64
import uuid
from datetime import datetime

# تنظیمات صفحه
st.set_page_config(page_title="Cxrol", page_icon="🎮", layout="wide")

# استایل CSS تم مشکی و قرمز با فونت iPhone
st.markdown("""
    <style>
        html, body, .stApp {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
            background-color: #0f0f0f;
            color: #fff;
        }
        h1, h2, h3, h4, h5 {
            color: #ff1a1a;
        }
        .stButton>button {
            background-color: #b30000;
            color: white;
            font-weight: 600;
            border-radius: 8px;
            padding: 8px 16px;
        }
        .stButton>button:hover {
            background-color: #e60000;
            transition: 0.3s;
        }
        .stTextInput>div>div>input, .stSelectbox>div>div>div {
            background-color: #1a1a1a;
            color: white;
            border-radius: 8px;
            padding: 6px 10px;
            border: none;
        }
        .box {
            background-color: #1a1a1a;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 0 10px #b30000cc;
            margin-bottom: 15px;
        }
        a.download-link {
            color:#fff;
            background:#b30000;
            padding:8px 15px;
            border-radius:8px;
            text-decoration:none;
            font-weight:bold;
            display:inline-block;
            margin-top: 10px;
        }
        a.download-link:hover {
            background:#e60000;
            transition: 0.3s;
        }
    </style>
""", unsafe_allow_html=True)

# داده‌های کشورهای انتخابی با IP pool و DNS
country_data = {
    "Saudi Arabia 🇸🇦": {
        "dns": ["212.11.190.10", "212.11.190.11", "89.237.78.90"],
        "ip_pool": [f"212.11.{i}.{j}" for i in range(180, 190) for j in range(1, 255)],
    },
    "UAE 🇦🇪": {
        "dns": ["94.200.200.10", "94.200.200.11", "193.123.45.80"],
        "ip_pool": [f"94.200.{i}.{j}" for i in range(100, 110) for j in range(1, 255)],
    },
    "Bahrain 🇧🇭": {
        "dns": ["185.65.200.10", "185.65.200.11", "80.95.110.27"],
        "ip_pool": [f"185.65.{i}.{j}" for i in range(200, 210) for j in range(1, 255)],
    },
    "Singapore 🇸🇬": {
        "dns": ["202.79.192.10", "202.79.192.11", "103.11.10.10"],
        "ip_pool": [f"202.79.{i}.{j}" for i in range(192, 200) for j in range(1, 255)],
    },
    "Turkey 🇹🇷": {
        "dns": ["195.175.254.2", "195.175.254.3", "85.105.150.70"],
        "ip_pool": [f"195.175.{i}.{j}" for i in range(50, 60) for j in range(1, 255)],
    },
    "Sweden 🇸🇪": {
        "dns": ["195.178.39.39", "195.178.39.40", "193.178.39.39"],
        "ip_pool": [f"195.178.{i}.{j}" for i in range(39, 49) for j in range(1, 255)],
    },
}

# ذخیره IPهای استفاده شده برای جلوگیری از تکرار
if "used_ips" not in st.session_state:
    st.session_state.used_ips = set()

# ذخیره کانفیگ‌ها
if "configs" not in st.session_state:
    st.session_state.configs = {}

def generate_unique_ip(ip_pool):
    available_ips = [ip for ip in ip_pool if ip not in st.session_state.used_ips]
    if not available_ips:
        return None
    ip = random.choice(available_ips)
    st.session_state.used_ips.add(ip)
    return ip

def generate_key(length=44):
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choices(chars, k=length))

def generate_config(country, config_name):
    private_key = generate_key()
    public_key = generate_key()
    address = generate_unique_ip(country_data[country]["ip_pool"])
    if not address:
        return None, "❌ IP addresses for this country are all used!"
    dns_server = random.choice(country_data[country]["dns"])
    port = random.randint(51820, 51830)

    config_text = f"""[Interface]
PrivateKey = {private_key}
Address = {address}/24
DNS = {dns_server}

[Peer]
PublicKey = {public_key}
AllowedIPs = 0.0.0.0/0
Endpoint = {address}:{port}
PersistentKeepalive = 25
"""
    filename = f"{config_name}.conf"
    return config_text, filename

# عنوان برنامه
st.title("🎮 Cxrol - WireGuard Config Generator")

# نمایش تعداد کانفیگ‌ها
st.markdown(f"### 👥 Total Configs Created: {len(st.session_state.configs)}")

with st.form("config_form"):
    country = st.selectbox("Select Country", list(country_data.keys()))
    config_name = st.text_input("Config File Name", value=f"Cxrol_{uuid.uuid4().hex[:8]}")
    submitted = st.form_submit_button("Generate Config")

if submitted:
    config_text, filename_or_error = generate_config(country, config_name)
    if config_text:
        # ذخیره کانفیگ
        st.session_state.configs[filename_or_error] = {
            "country": country,
            "config_text": config_text,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        # لینک دانلود فایل کانفیگ
        b64 = base64.b64encode(config_text.encode()).decode()
        href = f'<a href="data:file/conf;base64,{b64}" download="{filename_or_error}" class="download-link">⬇️ Download {filename_or_error}</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("✅ Configuration created successfully!")
    else:
        st.error(filename_or_error)

# نمایش کانفیگ‌های ساخته شده
st.markdown("---")
st.markdown("### 🗂️ Generated Configurations:")

if st.session_state.configs:
    for fname, details in st.session_state.configs.items():
        st.markdown(f"**{fname}** - {details['country']} - Created at: {details['created_at']}")
else:
    st.info("No configs generated yet.")
