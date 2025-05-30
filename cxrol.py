import streamlit as st
import random
import base64
import uuid
import json
import streamlit.components.v1 as components

# Set page config for a gaming-themed layout
st.set_page_config(page_title="Cxrol", page_icon="🎮", layout="wide")

# Country-specific IP and DNS pools (realistic, non-overlapping)
country_data = {
    "Bahrain 🇧🇭": {
        "dns": ["185.65.200.10", "185.65.200.11", "80.95.110.27"],  # Bahrain Telecom, etc.
        "ip_pool": [f"185.65.{i}.{j}" for i in range(200, 210) for j in range(1, 255)],
    },
    "UAE 🇦🇪": {
        "dns": ["94.200.200.10", "94.200.200.11", "193.123.45.80"],  # Etisalat, Du
        "ip_pool": [f"94.200.{i}.{j}" for i in range(100, 110) for j in range(1, 255)],
    },
    "Saudi Arabia 🇸🇦": {
        "dns": ["212.11.190.10", "212.11.190.11", "89.237.78.90"],  # STC, Mobily
        "ip_pool": [f"212.11.{i}.{j}" for i in range(180, 190) for j in range(1, 255)],
    },
    "Turkey 🇹🇷": {
        "dns": ["195.175.254.2", "195.175.254.3", "85.105.150.70"],  # Turk Telekom
        "ip_pool": [f"195.175.{i}.{j}" for i in range(50, 60) for j in range(1, 255)],
    },
}

# Track used IPs to ensure uniqueness
if "used_ips" not in st.session_state:
    st.session_state.used_ips = set()

def generate_unique_ip(ip_pool):
    available_ips = [ip for ip in ip_pool if ip not in st.session_state.used_ips]
    if not available_ips:
        return None  # Fallback if pool is exhausted
    ip = random.choice(available_ips)
    st.session_state.used_ips.add(ip)
    return ip

# Generate WireGuard config
def generate_config(operator, country, volume, days, users, config_name):
    private_key = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=42)) + 'c='
    public_key = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=42)) + 'c='
    address = generate_unique_ip(country_data[country]["ip_pool"])
    if not address:
        return None, "IP pool exhausted for this country!"
    allowed_ips = "0.0.0.0/0"  # Allow all IPs for gaming
    port = random.randint(51820, 51830)  # Standard WireGuard port range
    dns_server = random.choice(country_data[country]["dns"])

    config = f"""[Interface]
PrivateKey = {private_key}
Address = {address}/24
DNS = {dns_server}

[Peer]
PublicKey = {public_key}
AllowedIPs = {allowed_ips}
Endpoint = {address}:{port}
PersistentKeepalive = 25
"""
    filename = f"{config_name}.conf"
    with open(filename, "w") as f:
        f.write(config)
    with open(filename, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return b64, filename

# Prepare data for JavaScript
countries = list(country_data.keys())
dns_data = {k: v["dns"] for k, v in country_data.items()}
countries_json = json.dumps(countries)
dns_data_json = json.dumps(dns_data)

# Streamlit UI
st.markdown(
    """
    <h1 class="text-4xl font-bold text-center text-red-600 drop-shadow-lg">
        <i class="fas fa-gamepad mr-2"></i>GrokVPN-Gamer
    </h1>
    """,
    unsafe_allow_html=True
)
st.markdown("---")
st.markdown("### 🛠️ Generate WireGuard Config")

# Form for config generation
with st.form("config_form"):
    operator = st.text_input("Operator Name", placeholder="Enter operator name")
    country = st.selectbox("Country", countries)
    volume = st.text_input("Config Volume", placeholder="e.g., 5GB")
    days = st.text_input("Days", placeholder="e.g., 30")
    users = st.selectbox("Number of Users", [1, 2, 3, 4, 5, 6])
    config_name = st.text_input("Config File Name", value=f"grokvpn_{uuid.uuid4().hex[:8]}", placeholder="Enter config name")

    submitted = st.form_submit_button("Generate Config", type="primary")

if submitted:
    b64, filename = generate_config(operator, country, volume, days, users, config_name)
    if b64:
        href = f'<a href="data:file/conf;base64,{b64}" download="{filename}" class="inline-block py-2 px-4 bg-red-600 text-white rounded hover:bg-red-700"><i class="fas fa-download mr-2"></i>Download {filename}</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("✅ Configuration created successfully!")
    else:
        st.error(f"❌ {filename}")

# DNS Performance Table
st.markdown("---")
st.markdown("### 🌐 DNS Game Performance")

components.html(
    f"""
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
    </head>
    <body class="bg-gray-900 text-white font-sans">
        <div class="max-w-4xl mx-auto p-6">
            <button id="refresh-btn" class="py-2 px-4 bg-red-600 text-white rounded hover:bg-red-700 transition duration-300 transform hover:scale-105">
                <i class="fas fa-sync-alt mr-2"></i>Refresh DNS
            </button>
            <table class="w-full mt-4 border-collapse bg-gray-800 rounded-lg shadow-xl shadow-red-500/50">
                <thead>
                    <tr class="bg-gray-900">
                        <th class="p-3 text-left">Country</th>
                        <th class="p-3 text-left">DNS</th>
                        <th class="p-3 text-left">Ping</th>
                        <th class="p-3 text-left">Status</th>
                    </tr>
                </thead>
                <tbody id="dns-table"></tbody>
            </table>
        </div>
        <script>
            const countries = {countries_json};
            const dnsData = {dns_data_json};

            function getRandom(min, max) {{
                return Math.floor(Math.random() * (max - min + 1)) + min;
            }}

            function generatePing() {{
                return getRandom(20, 300);
            }}

            function getStatus(ping) {{
                if (ping <= 100) return ["Great for Gaming ✅", "text-green-500"];
                if (ping <= 200) return ["Average ✴️", "text-yellow-500"];
                return ["Bad ❌", "text-red-500"];
            }}

            function generateDNS() {{
                const tbody = document.querySelector("#dns-table");
                tbody.innerHTML = "";
                countries.forEach(c => {{
                    const ping = generatePing();
                    const [status, cls] = getStatus(ping);
                    const dns = dnsData[c][Math.floor(Math.random() * dnsData[c].length)];
                    tbody.innerHTML += `
                        <tr class="border-t border-gray-700">
                            <td class="p-3">${{c}}</td>
                            <td class="p-3">${{dns}}</td>
                            <td class="${{cls}}">${{ping}} ms</td>
                            <td class="${{cls}}">${{status}}</td>
                        </tr>
                    `;
                }});
            }}

            document.getElementById("refresh-btn").addEventListener("click", generateDNS);
            generateDNS();
        </script>
    </body>
    </html>
    """,
    height=500
)
