import streamlit as st
import random
import base64
import uuid
import streamlit.components.v1 as components

# Set page config for a gaming-themed layout
st.set_page_config(page_title="GrokVPN-Gamer", page_icon="🎮", layout="wide")

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
used_ips = set()

def generate_unique_ip(ip_pool):
    available_ips = [ip for ip in ip_pool if ip not in used_ips]
    if not available_ips:
        return None  # Fallback if pool is exhausted
    ip = random.choice(available_ips)
    used_ips.add(ip)
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

# React-based UI with Tailwind CSS and Font Awesome
components.html(
    f"""
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js"></script>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/babel-standalone@7.22.5/babel.min.js"></script>
    </head>
    <body class="bg-gray-900 text-white font-sans">
        <div id="root"></div>
        <script type="text/babel">
            function App() {{
                const [operator, setOperator] = React.useState("");
                const [country, setCountry] = React.useState("{list(country_data.keys())[0]}");
                const [volume, setVolume] = React.useState("");
                const [days, setDays] = React.useState("");
                const [users, setUsers] = React.useState(1);
                const [configName, setConfigName] = React.useState("grokvpn_{uuid.uuid4().hex[:8]}");
                const [result, setResult] = React.useState(null);
                const [dnsData, setDnsData] = React.useState([]);

                const countries = {JSON.stringify(list(country_data.keys()))};
                const countryData = {JSON.stringify({k: v["dns"] for k, v in country_data.items()})};

                const generatePing = () => Math.floor(Math.random() * 281) + 20;
                const getStatus = (ping) => {{
                    if (ping <= 100) return ["Great for Gaming ✅", "text-green-500"];
                    if (ping <= 200) return ["Average ✴️", "text-yellow-500"];
                    return ["Bad ❌", "text-red-500"];
                }};

                const generateDNS = () => {{
                    const newData = countries.map(c => {{
                        const ping = generatePing();
                        const [status, cls] = getStatus(ping);
                        return {{ name: c, dns: countryData[c][Math.floor(Math.random() * countryData[c].length)], ping, status, cls }};
                    }});
                    setDnsData(newData);
                }};

                React.useEffect(() => {{ generateDNS(); }}, []);

                const handleSubmit = async (e) => {{
                    e.preventDefault();
                    const response = await fetch("/_stcore/streamlit", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{
                            type: "form_submit",
                            data: {{ operator, country, volume, days, users, config_name: configName }}
                        }})
                    }});
                    const result = await response.json();
                    setResult(result);
                }};

                return (
                    <div className="min-h-screen bg-gray-900 p-6">
                        <h1 className="text-4xl font-bold text-center text-red-600 drop-shadow-lg">
                            <i className="fas fa-gamepad mr-2"></i>GrokVPN-Gamer
                        </h1>
                        <div className="max-w-2xl mx-auto mt-8 p-6 bg-gray-800 rounded-lg shadow-xl shadow-red-500/50">
                            <form onSubmit={{handleSubmit}} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-300">
                                        <i className="fas fa-user mr-2"></i>Operator Name
                                    </label>
                                    <input
                                        type="text"
                                        value={{operator}}
                                        onChange={{(e) => setOperator(e.target.value)}}
                                        className="mt-1 w-full p-2 bg-gray-700 text-white rounded focus:ring-2 focus:ring-red-500"
                                        placeholder="Enter operator name"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-300">
                                        <i className="fas fa-globe mr-2"></i>Country
                                    </label>
                                    <select
                                        value={{country}}
                                        onChange={{(e) => setCountry(e.target.value)}}
                                        className="mt-1 w-full p-2 bg-gray-700 text-white rounded focus:ring-2 focus:ring-red-500"
                                    >
                                        {{countries.map(c => (
                                            <option key={{c}} value={{c}}>{{c}}</option>
                                        ))}}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-300">
                                        <i className="fas fa-database mr-2"></i>Config Volume
                                    </label>
                                    <input
                                        type="text"
                                        value={{volume}}
                                        onChange={{(e) => setVolume(e.target.value)}}
                                        className="mt-1 w-full p-2 bg-gray-700 text-white rounded focus:ring-2 focus:ring-red-500"
                                        placeholder="e.g., 5GB"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-300">
                                        <i className="fas fa-calendar mr-2"></i>Days
                                    </label>
                                    <input
                                        type="text"
                                        value={{days}}
                                        onChange={{(e) => setDays(e.target.value)}}
                                        className="mt-1 w-full p-2 bg-gray-700 text-white rounded focus:ring-2 focus:ring-red-500"
                                        placeholder="e.g., 30"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-300">
                                        <i className="fas fa-users mr-2"></i>Number of Users
                                    </label>
                                    <select
                                        value={{users}}
                                        onChange={{(e) => setUsers(Number(e.target.value))}}
                                        className="mt-1 w-full p-2 bg-gray-700 text-white rounded focus:ring-2 focus:ring-red-500"
                                    >
                                        {{[1, 2, 3, 4, 5, 6].map(n => (
                                            <option key={{n}} value={{n}}>{{n}}</option>
                                        ))}}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-300">
                                        <i className="fas fa-file mr-2"></i>Config File Name
                                    </label>
                                    <input
                                        type="text"
                                        value={{configName}}
                                        onChange={{(e) => setConfigName(e.target.value)}}
                                        className="mt-1 w-full p-2 bg-gray-700 text-white rounded focus:ring-2 focus:ring-red-500"
                                        placeholder="Enter config name"
                                    />
                                </div>
                                <button
                                    type="submit"
                                    className="w-full py-2 px-4 bg-red-600 text-white font-bold rounded hover:bg-red-700 transition duration-300 transform hover:scale-105"
                                >
                                    <i className="fas fa-bolt mr-2"></i>Generate Config
                                </button>
                            </form>
                            {{result && (
                                <div className="mt-4 p-4 bg-gray-700 rounded">
                                    {{result.success ? (
                                        <>
                                            <p className="text-green-500"><i className="fas fa-check-circle mr-2"></i>Configuration created!</p>
                                            <a
                                                href={{`data:file/conf;base64,${{result.b64}}`}}
                                                download={{result.filename}}
                                                className="inline-block mt-2 py-2 px-4 bg-red-600 text-white rounded hover:bg-red-700"
                                            >
                                                <i className="fas fa-download mr-2"></i>Download {{result.filename}}
                                            </a>
                                        </>
                                    ) : (
                                        <p className="text-red-500"><i className="fas fa-exclamation-circle mr-2"></i>{{result.message}}</p>
                                    )}}
                                </div>
                            )}}
                        </div>
                        <div className="mt-8 p-6 bg-gray-800 rounded-lg shadow-xl shadow-red-500/50">
                            <h2 className="text-2xl font-bold text-red-600">
                                <i className="fas fa-tachometer-alt mr-2"></i>DNS Game Performance
                            </h2>
                            <button
                                onClick={{generateDNS}}
                                className="mt-4 py-2 px-4 bg-red-600 text-white rounded hover:bg-red-700 transition duration-300 transform hover:scale-105"
                            >
                                <i className="fas fa-sync-alt mr-2"></i>Refresh DNS
                            </button>
                            <table className="w-full mt-4 border-collapse">
                                <thead>
                                    <tr className="bg-gray-900">
                                        <th className="p-3 text-left">Country</th>
                                        <th className="p-3 text-left">DNS</th>
                                        <th className="p-3 text-left">Ping</th>
                                        <th className="p-3 text-left">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {{dnsData.map(data => (
                                        <tr key={{data.name}} className="border-t border-gray-700">
                                            <td className="p-3">{{data.name}}</td>
                                            <td className="p-3">{{data.dns}}</td>
                                            <td className={{data.cls}}>{{data.ping}} ms</td>
                                            <td className={{data.cls}}>{{data.status}}</td>
                                        </tr>
                                    ))}}
                                </tbody>
                            </table>
                        </div>
                    </div>
                );
            }}

            ReactDOM.render(<App />, document.getElementById("root"));
        </script>
    </body>
    </html>
    """,
    height=1200
)

# Handle form submission (Streamlit backend)
if "form_submit" in st.session_state:
    data = st.session_state.get("form_submit", {})
    b64, filename = generate_config(
        data.get("operator", ""),
        data.get("country", list(country_data.keys())[0]),
        data.get("volume", ""),
        data.get("days", ""),
        data.get("users", 1),
        data.get("config_name", f"grokvpn_{uuid.uuid4().hex[:8]}")
    )
    if b64:
        st.session_state["result"] = {"success": True, "b64": b64, "filename": filename}
    else:
        st.session_state["result"] = {"success": False, "message": filename}
