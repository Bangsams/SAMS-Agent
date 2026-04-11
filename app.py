import streamlit as st
import os
import json
import time
import datetime
import threading
import tempfile
import io
import base64
from dotenv import load_dotenv

load_dotenv()

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SAMS Agent",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── GLOBAL CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,700;1,400&display=swap');

:root {
    --forest:      #1a3a2a;
    --moss:        #2d5a3d;
    --leaf:        #4a8c5c;
    --sage:        #7ab892;
    --mint:        #a8d5b5;
    --cream:       #f0f7f2;
    --gold:        #c8a84b;
    --amber:       #e8b84b;
    --bark:        #5c3d1e;
    --white:       #ffffff;
    --glass:       rgba(255,255,255,0.08);
    --glass-border:rgba(255,255,255,0.15);
    --shadow:      0 8px 32px rgba(26,58,42,0.4);
    --radius:      16px;
    --radius-sm:   10px;
}

html, body, [data-testid="stApp"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: linear-gradient(135deg, #0d2318 0%, #1a3a2a 30%, #0f2d1c 60%, #1e3d2a 100%) !important;
    min-height: 100vh;
    color: var(--cream) !important;
}

/* Animated background pattern */
[data-testid="stApp"]::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        radial-gradient(ellipse 600px 400px at 20% 20%, rgba(74,140,92,0.08) 0%, transparent 70%),
        radial-gradient(ellipse 400px 600px at 80% 80%, rgba(45,90,61,0.12) 0%, transparent 70%),
        radial-gradient(ellipse 300px 300px at 60% 30%, rgba(168,213,181,0.05) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* Leaf pattern overlay */
[data-testid="stApp"]::after {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 5 Q40 15 35 30 Q30 45 20 50 Q15 35 20 20 Q25 10 30 5Z' fill='rgba(74,140,92,0.03)'/%3E%3C/svg%3E");
    background-size: 60px 60px;
    pointer-events: none;
    z-index: 0;
}

/* Main container */
.main .block-container {
    position: relative;
    z-index: 1;
    padding-top: 1rem !important;
    max-width: 1200px !important;
}

/* HEADER */
.sams-header {
    text-align: center;
    padding: 2rem 0 1.5rem;
    position: relative;
}
.sams-header h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 3.2rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, var(--mint) 0%, var(--sage) 40%, var(--gold) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    margin: 0 !important;
    line-height: 1 !important;
}
.sams-header .tagline {
    color: var(--sage);
    font-size: 0.85rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 0.4rem;
    font-weight: 500;
}
.sams-header .leaf-deco {
    font-size: 1.4rem;
    margin: 0 0.5rem;
    animation: sway 3s ease-in-out infinite;
}
@keyframes sway {
    0%,100% { transform: rotate(-5deg); }
    50% { transform: rotate(5deg); }
}

/* TABS */
[data-testid="stTabs"] > div:first-child {
    background: rgba(26,58,42,0.6) !important;
    border-radius: var(--radius) !important;
    padding: 6px !important;
    border: 1px solid var(--glass-border) !important;
    backdrop-filter: blur(20px) !important;
    gap: 4px !important;
    margin-bottom: 1.5rem !important;
}
[data-testid="stTabs"] button {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.5px !important;
    color: var(--sage) !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.55rem 1.2rem !important;
    border: none !important;
    background: transparent !important;
    transition: all 0.25s ease !important;
}
[data-testid="stTabs"] button:hover {
    background: rgba(74,140,92,0.2) !important;
    color: var(--mint) !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    background: linear-gradient(135deg, var(--moss), var(--leaf)) !important;
    color: var(--white) !important;
    box-shadow: 0 4px 16px rgba(74,140,92,0.4) !important;
}
[data-testid="stTabs"] button[aria-selected="true"] p {
    color: var(--white) !important;
}

/* CARDS */
.sams-card {
    background: rgba(26,58,42,0.5);
    border: 1px solid rgba(74,140,92,0.25);
    border-radius: var(--radius);
    padding: 1.5rem;
    backdrop-filter: blur(20px);
    margin-bottom: 1rem;
    box-shadow: var(--shadow);
    transition: border-color 0.3s ease;
}
.sams-card:hover {
    border-color: rgba(122,184,146,0.4);
}
.card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.2rem;
    color: var(--mint);
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── TEXT INPUTS – high contrast for dark & light modes ── */
[data-testid="stTextInput"] > div > div,
[data-testid="stTextArea"] > div > div,
[data-testid="stNumberInput"] > div > div {
    background: rgba(10,30,18,0.85) !important;
    border: 1.5px solid rgba(122,184,146,0.45) !important;
    border-radius: var(--radius-sm) !important;
    backdrop-filter: blur(10px) !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.3) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="stTextInput"] > div > div:focus-within,
[data-testid="stTextArea"] > div > div:focus-within,
[data-testid="stNumberInput"] > div > div:focus-within {
    border-color: var(--sage) !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.3), 0 0 0 3px rgba(122,184,146,0.2) !important;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
    background: transparent !important;
    color: #e8f5ec !important;        /* always bright on dark bg */
    caret-color: var(--sage) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color: rgba(168,213,181,0.5) !important;
}
/* Label above inputs */
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stNumberInput"] label,
[data-testid="stDateInput"] label,
[data-testid="stTimeInput"] label {
    color: var(--sage) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.5px !important;
}

/* DATE & TIME inputs */
[data-testid="stDateInput"] > div > div,
[data-testid="stTimeInput"] > div > div {
    background: rgba(10,30,18,0.85) !important;
    border: 1.5px solid rgba(122,184,146,0.45) !important;
    border-radius: var(--radius-sm) !important;
}
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input {
    color: #e8f5ec !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* SELECT BOX */
[data-testid="stSelectbox"] > div > div {
    background: rgba(10,30,18,0.85) !important;
    border: 1.5px solid rgba(122,184,146,0.45) !important;
    border-radius: var(--radius-sm) !important;
    color: #e8f5ec !important;
}
[data-testid="stSelectbox"] label { color: var(--sage) !important; font-weight: 600 !important; }

/* BUTTONS */
[data-testid="stButton"] button {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.5px !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.55rem 1.4rem !important;
    border: none !important;
    transition: all 0.25s ease !important;
    position: relative !important;
    overflow: hidden !important;
}
[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, var(--moss) 0%, var(--leaf) 100%) !important;
    color: var(--white) !important;
    box-shadow: 0 4px 16px rgba(74,140,92,0.4) !important;
}
[data-testid="stButton"] button[kind="primary"]:hover {
    box-shadow: 0 6px 24px rgba(74,140,92,0.6) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stButton"] button[kind="secondary"] {
    background: rgba(74,140,92,0.15) !important;
    color: var(--sage) !important;
    border: 1px solid rgba(74,140,92,0.35) !important;
}
[data-testid="stButton"] button[kind="secondary"]:hover {
    background: rgba(74,140,92,0.25) !important;
    color: var(--mint) !important;
}

/* METRIC */
[data-testid="metric-container"] {
    background: rgba(26,58,42,0.5) !important;
    border: 1px solid rgba(74,140,92,0.25) !important;
    border-radius: var(--radius) !important;
    padding: 1rem !important;
    backdrop-filter: blur(20px) !important;
}
[data-testid="metric-container"] label { color: var(--sage) !important; font-weight: 600 !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: var(--mint) !important; font-weight: 700 !important; }

/* DATAFRAME */
[data-testid="stDataFrame"] {
    border-radius: var(--radius) !important;
    overflow: hidden !important;
    border: 1px solid rgba(74,140,92,0.25) !important;
}

/* SUCCESS / INFO / WARNING / ERROR */
[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    backdrop-filter: blur(10px) !important;
}

/* SPINNER */
[data-testid="stSpinner"] > div { border-top-color: var(--sage) !important; }

/* STATUS BADGE */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.status-active {
    background: rgba(74,140,92,0.2);
    color: var(--sage);
    border: 1px solid rgba(74,140,92,0.4);
}
.status-idle {
    background: rgba(92,61,30,0.2);
    color: var(--amber);
    border: 1px solid rgba(200,168,75,0.4);
}

/* TOKEN COUNTER */
.token-bar {
    background: rgba(26,58,42,0.8);
    border: 1px solid rgba(74,140,92,0.3);
    border-radius: 8px;
    padding: 0.5rem 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.78rem;
    color: var(--sage);
}
.token-fill {
    height: 4px;
    border-radius: 2px;
    background: linear-gradient(90deg, var(--leaf), var(--gold));
    transition: width 0.5s ease;
}
.token-track {
    flex: 1;
    height: 4px;
    background: rgba(255,255,255,0.1);
    border-radius: 2px;
    overflow: hidden;
}

/* DIVIDER */
.sams-divider {
    border: none;
    border-top: 1px solid rgba(74,140,92,0.2);
    margin: 1rem 0;
}

/* CHAT MESSAGES */
.chat-msg-user {
    background: rgba(45,90,61,0.4);
    border: 1px solid rgba(74,140,92,0.3);
    border-radius: var(--radius-sm) 0 var(--radius-sm) var(--radius-sm);
    padding: 0.7rem 1rem;
    margin: 0.5rem 0 0.5rem 2rem;
    color: var(--cream);
    font-size: 0.88rem;
}
.chat-msg-ai {
    background: rgba(15,40,25,0.6);
    border: 1px solid rgba(122,184,146,0.2);
    border-radius: 0 var(--radius-sm) var(--radius-sm) var(--radius-sm);
    padding: 0.7rem 1rem;
    margin: 0.5rem 2rem 0.5rem 0;
    color: var(--cream);
    font-size: 0.88rem;
}
.msg-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}
.msg-label-user { color: var(--sage); }
.msg-label-ai   { color: var(--gold); }

/* RECORDING ANIMATION */
@keyframes pulse-rec {
    0%,100% { box-shadow: 0 0 0 0 rgba(220,50,50,0.4); }
    50%      { box-shadow: 0 0 0 12px rgba(220,50,50,0); }
}
.rec-dot {
    width: 12px; height: 12px;
    background: #e05555;
    border-radius: 50%;
    display: inline-block;
    animation: pulse-rec 1.2s ease-in-out infinite;
    margin-right: 6px;
}

/* HIDE default streamlit elements */
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stDecoration"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ────────────────────────────────────────────────────────────────
def get_openai_client():
    from openai import OpenAI
    return OpenAI(api_key=get_env("OPENAI_API_KEY"))

def count_tokens_approx(text: str) -> int:
    """~4 chars per token heuristic."""
    return max(1, len(text) // 4)

def tokens_to_usd(tokens: int) -> float:
    # gpt-4o-mini: $0.15/1M input + $0.60/1M output → average ~$0.00000038 per token
    return tokens * 0.00000050

MAX_BUDGET_USD = 0.05

def init_session_state():
    defaults = {
        # Token tracking
        "total_tokens_used": 0,
        "budget_exceeded": False,
        # Todo
        "todo_messages": [],
        "todo_events": [],
        # Finance
        "finance_messages": [],
        "finance_entries": [],          # [{date, description, type, amount}]
        "show_analytics": False,
        # Notes
        "note_messages": [],
        "note_transcriptions": [],
        "recording": False,
        "audio_bytes": None,
        "mic_permission": None,
        "note_title": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# ─── GOOGLE SERVICES ─────────────────────────────────────────────────────────
def get_env(key, default=None):
    """Baca dari st.secrets (Streamlit Cloud) atau os.environ (lokal)."""
    try:
        return st.secrets[key]
    except:
        return os.getenv(key, default)

def get_google_creds():
    """
    Return Google credentials.
    Prioritas:
    1. st.secrets['google_token'] — token OAuth tersimpan di Streamlit Secrets
    2. st.secrets['google_credentials'] — client_id/secret untuk flow baru
    3. File lokal credentials.json (development)
    """
    SCOPES = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request

        # ── OPSI 1: Token lengkap sudah ada di st.secrets ──────────────────
        # Ini dipakai setelah user sudah login sekali dan token disimpan manual
        try:
            token_info = dict(st.secrets["google_token"])
            creds = Credentials(
                token=token_info.get("token"),
                refresh_token=token_info.get("refresh_token"),
                token_uri=token_info.get("token_uri", "https://oauth2.googleapis.com/token"),
                client_id=token_info.get("client_id"),
                client_secret=token_info.get("client_secret"),
                scopes=SCOPES,
            )
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
            return creds
        except (KeyError, Exception):
            pass

        # ── OPSI 2: Buat flow dari credentials di st.secrets ───────────────
        try:
            gc = dict(st.secrets["google_credentials"])
            client_id     = gc.get("client_id")
            client_secret = gc.get("client_secret")
            redirect_uri  = gc.get("redirect_uri", "https://sams-agent-10.streamlit.app/oauth2callback")

            if client_id and client_secret:
                # Tampilkan tombol OAuth di UI
                if "google_auth_code" not in st.session_state:
                    st.session_state.google_auth_code = None

                if not st.session_state.google_auth_code:
                    from google_auth_oauthlib.flow import Flow
                    flow = Flow.from_client_config(
                        {
                            "web": {
                                "client_id": client_id,
                                "client_secret": client_secret,
                                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                "token_uri": "https://oauth2.googleapis.com/token",
                                "redirect_uris": [redirect_uri],
                            }
                        },
                        scopes=SCOPES,
                        redirect_uri=redirect_uri,
                    )
                    auth_url, _ = flow.authorization_url(
                        access_type="offline",
                        include_granted_scopes="true",
                        prompt="consent",
                    )
                    st.session_state._oauth_flow = flow
                    st.warning("⚠️ Koneksi Google diperlukan. Klik tombol di bawah untuk login.")
                    st.markdown(f"""
                    <a href="{auth_url}" target="_blank">
                        <button style="background:linear-gradient(135deg,#2d5a3d,#4a8c5c);
                                       color:white;border:none;padding:10px 24px;border-radius:10px;
                                       font-weight:700;cursor:pointer;font-size:0.9rem;">
                            🔐 Login dengan Google
                        </button>
                    </a>
                    """, unsafe_allow_html=True)

                    auth_code_input = st.text_input(
                        "Setelah login, paste kode dari URL (nilai parameter `code=...`) di sini:",
                        key="oauth_code_input",
                        placeholder="4/0AX4XfWh..."
                    )
                    if st.button("✅ Konfirmasi Login Google", key="confirm_oauth"):
                        if auth_code_input.strip():
                            st.session_state.google_auth_code = auth_code_input.strip()
                            st.rerun()
                    return None

                else:
                    # Tukar code dengan token
                    try:
                        flow = st.session_state.get("_oauth_flow")
                        if flow is None:
                            from google_auth_oauthlib.flow import Flow
                            flow = Flow.from_client_config(
                                {
                                    "web": {
                                        "client_id": client_id,
                                        "client_secret": client_secret,
                                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                        "token_uri": "https://oauth2.googleapis.com/token",
                                        "redirect_uris": [redirect_uri],
                                    }
                                },
                                scopes=SCOPES,
                                redirect_uri=redirect_uri,
                            )
                        import os as _os
                        _os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
                        flow.fetch_token(code=st.session_state.google_auth_code)
                        creds = flow.credentials
                        # Tampilkan token untuk disimpan di Streamlit Secrets
                        token_dict = {
                            "token": creds.token,
                            "refresh_token": creds.refresh_token,
                            "token_uri": creds.token_uri,
                            "client_id": creds.client_id,
                            "client_secret": creds.client_secret,
                        }
                        st.success("✅ Login Google berhasil!")
                        st.info("📋 Simpan token ini di Streamlit Secrets → key: `google_token`")
                        st.code(json.dumps(token_dict, indent=2), language="json")
                        return creds
                    except Exception as e:
                        st.error(f"❌ Gagal tukar token: {e}")
                        st.session_state.google_auth_code = None
                        return None
        except (KeyError, Exception):
            pass

        # ── OPSI 3: File lokal credentials.json (development) ──────────────
        from google_auth_oauthlib.flow import InstalledAppFlow
        creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
        if not os.path.exists(creds_path):
            return None
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as f:
                f.write(creds.to_json())
        return creds

    except Exception as e:
        return None

def add_google_calendar_event(title, description, start_dt, end_dt):
    """Add event to Google Calendar."""
    creds = get_google_creds()
    if not creds:
        return False, "Google credentials not configured."
    try:
        from googleapiclient.discovery import build
        service = build("calendar", "v3", credentials=creds)
        event = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "Asia/Jakarta"},
            "end":   {"dateTime": end_dt.isoformat(),   "timeZone": "Asia/Jakarta"},
            "reminders": {"useDefault": False,
                          "overrides": [{"method":"popup","minutes":30},
                                        {"method":"email","minutes":60}]},
        }
        service.events().insert(calendarId="primary", body=event).execute()
        return True, "Event berhasil ditambahkan ke Google Calendar ✓"
    except Exception as e:
        return False, f"Gagal menambahkan ke Google Calendar: {str(e)}"

def append_to_google_sheet(entries):
    """Append finance entries to Google Sheet."""
    sheet_id = get_env("GOOGLE_SHEET_ID")
    creds = get_google_creds()
    if not creds or not sheet_id:
        return False, "Google Sheet ID atau credentials tidak dikonfigurasi."
    try:
        from googleapiclient.discovery import build
        service = build("sheets", "v4", credentials=creds)
        values = [[e["date"], e["description"], e["type"], e["amount"]] for e in entries]
        body = {"values": values}
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id, range="Sheet1!A:D",
            valueInputOption="USER_ENTERED", body=body
        ).execute()
        return True, "Data tersimpan ke Google Sheets ✓"
    except Exception as e:
        return False, f"Gagal menyimpan ke Google Sheets: {str(e)}"

def upload_audio_to_drive(audio_bytes, filename):
    """Upload audio to Google Drive and return file_id."""
    folder_id = get_env("GOOGLE_DRIVE_FOLDER_ID")
    creds = get_google_creds()
    if not creds:
        return None, "Google credentials tidak dikonfigurasi."
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseUpload
        service = build("drive", "v3", credentials=creds)
        metadata = {"name": filename, "parents": [folder_id] if folder_id else []}
        media = MediaIoBaseUpload(io.BytesIO(audio_bytes), mimetype="audio/wav", resumable=True)
        f = service.files().create(body=metadata, media_body=media, fields="id").execute()
        return f.get("id"), "Audio berhasil diupload ke Google Drive ✓"
    except Exception as e:
        return None, f"Gagal upload ke Drive: {str(e)}"

def delete_drive_file(file_id):
    creds = get_google_creds()
    if not creds or not file_id:
        return
    try:
        from googleapiclient.discovery import build
        service = build("drive", "v3", credentials=creds)
        service.files().delete(fileId=file_id).execute()
    except:
        pass

# ─── AI CALLS ────────────────────────────────────────────────────────────────
SYSTEM_TODO = """Kamu adalah SAMS Todo Agent, asisten cerdas berbahasa Indonesia untuk manajemen jadwal.
Bantu user mencatat, mengorganisir, dan mengingatkan aktivitas mereka.
Ekstrak informasi: judul kegiatan, tanggal, jam mulai, jam selesai, deskripsi.
Jika user memberi informasi kegiatan, balas dengan JSON berikut (dan teks penjelasan):
{"action":"add_event","title":"...","date":"YYYY-MM-DD","start_time":"HH:MM","end_time":"HH:MM","description":"..."}
Jika hanya percakapan biasa, balas normal tanpa JSON.
Selalu ramah, singkat, dan profesional. Gunakan emoji sesekali."""

SYSTEM_FINANCE = """Kamu adalah SAMS Finance Agent, asisten keuangan cerdas berbahasa Indonesia.
Bantu user mencatat pengeluaran dan pemasukan.
Jika user menyebut transaksi, ekstrak dan balas dengan JSON:
{"action":"add_entry","description":"...","type":"pengeluaran|pemasukan","amount":ANGKA_RUPIAH}
Jika user minta analisis, berikan insight keuangan yang berguna.
Gunakan format rupiah (Rp X.XXX) yang benar. Singkat dan informatif."""

SYSTEM_NOTE = """Kamu adalah SAMS Note Agent, asisten pencatat berbahasa Indonesia.
Tugasmu adalah membantu user merapikan dan merangkum hasil transkripsi rekaman suara.
Buat catatan yang terstruktur dengan: ringkasan utama, poin-poin penting, dan action items jika ada.
Format dengan markdown yang bersih."""

def call_ai(system_prompt: str, messages: list, tab_key: str) -> str:
    """Call OpenAI with budget guard."""
    if st.session_state.budget_exceeded:
        return "⚠️ Budget $0.05 untuk sesi ini telah habis. Mohon refresh halaman untuk sesi baru."

    budget_remaining = MAX_BUDGET_USD - tokens_to_usd(st.session_state.total_tokens_used)
    if budget_remaining <= 0:
        st.session_state.budget_exceeded = True
        return "⚠️ Budget $0.05 untuk sesi ini telah habis."

    # Estimate max output tokens from remaining budget
    max_out = min(800, int(budget_remaining / 0.00000060))
    if max_out < 50:
        st.session_state.budget_exceeded = True
        return "⚠️ Budget hampir habis. Refresh untuk sesi baru."

    try:
        client = get_openai_client()
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}] + messages,
            max_tokens=max_out,
            temperature=0.7,
        )
        used = resp.usage.total_tokens if resp.usage else count_tokens_approx(
            system_prompt + " ".join(m["content"] for m in messages)
        )
        st.session_state.total_tokens_used += used
        return resp.choices[0].message.content
    except Exception as e:
        return f"❌ Error AI: {str(e)}"

def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe audio using OpenAI Whisper."""
    if st.session_state.budget_exceeded:
        return "Budget habis."
    try:
        client = get_openai_client()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=f)
        os.unlink(tmp_path)
        # Whisper cost: ~$0.006/min, estimate 5 min → $0.03 per call
        st.session_state.total_tokens_used += 60_000  # conservative token budget hit
        return transcript.text
    except Exception as e:
        return f"Error transkripsi: {str(e)}"

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="sams-header">
    <div>
        <span class="leaf-deco">🌿</span>
        <span style="font-family:'Playfair Display',serif;font-size:3.2rem;font-weight:700;
               background:linear-gradient(135deg,#a8d5b5,#7ab892,#c8a84b);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            SAMS Agent
        </span>
        <span class="leaf-deco">🍃</span>
    </div>
    <div class="tagline">Smart Autonomous Management System · Sustainable Living</div>
</div>
""", unsafe_allow_html=True)

# Token budget bar
used_usd = tokens_to_usd(st.session_state.total_tokens_used)
pct = min(100, int(used_usd / MAX_BUDGET_USD * 100))
bar_color = "#e05555" if pct > 80 else "#c8a84b" if pct > 50 else "#4a8c5c"
st.markdown(f"""
<div class="token-bar">
    <span>💰 Budget Sesi</span>
    <div class="token-track">
        <div class="token-fill" style="width:{pct}%;background:{bar_color};"></div>
    </div>
    <span style="font-weight:700;color:{'#e08888' if pct>80 else '#a8d5b5'}">
        ${used_usd:.4f} / ${MAX_BUDGET_USD:.2f}
    </span>
</div>
""", unsafe_allow_html=True)
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🗓️ Todo Task Agent", "💰 Financial Agent", "🎙️ Note Agent"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 · TODO TASK AGENT
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="sams-card">
        <div class="card-title">🗓️ SAMS Todo Task Agent
            <span style='font-size:0.7rem;color:#7ab892;margin-left:auto;
                  background:rgba(74,140,92,0.15);padding:3px 10px;border-radius:12px;
                  border:1px solid rgba(74,140,92,0.3);'>
                Terintegrasi Google Calendar
            </span>
        </div>
        <p style='color:#7ab892;font-size:0.82rem;margin:0'>
            Ceritakan aktivitas atau agenda Anda — SAMS akan mencatatnya dan menambahkan ke Google Calendar secara otomatis.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Display existing events
    if st.session_state.todo_events:
        st.markdown("<div class='card-title' style='font-size:0.9rem;margin-bottom:0.5rem'>📋 Agenda Tersimpan</div>", unsafe_allow_html=True)
        for i, ev in enumerate(reversed(st.session_state.todo_events[-10:])):
            synced = ev.get("synced", False)
            sync_icon = "☁️ Synced" if synced else "💾 Local"
            st.markdown(f"""
            <div style='background:rgba(26,58,42,0.4);border:1px solid rgba(74,140,92,0.2);
                        border-radius:10px;padding:0.7rem 1rem;margin-bottom:0.4rem;
                        display:flex;align-items:center;gap:0.8rem;'>
                <span style='font-size:1.2rem'>📌</span>
                <div style='flex:1'>
                    <div style='color:#a8d5b5;font-weight:700;font-size:0.88rem'>{ev.get("title","")}</div>
                    <div style='color:#7ab892;font-size:0.75rem'>
                        📅 {ev.get("date","")} · ⏰ {ev.get("start_time","?")}–{ev.get("end_time","?")}
                    </div>
                    {f'<div style="color:#7ab892;font-size:0.73rem;margin-top:2px">{ev.get("description","")}</div>' if ev.get("description") else ""}
                </div>
                <span style='font-size:0.7rem;color:{"#7ab892" if synced else "#c8a84b"};
                             background:{"rgba(74,140,92,0.15)" if synced else "rgba(200,168,75,0.15)"};
                             padding:3px 8px;border-radius:8px;'>
                    {sync_icon}
                </span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr class='sams-divider'>", unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state.todo_messages[-6:]:
        role = msg["role"]
        css = "chat-msg-user" if role == "user" else "chat-msg-ai"
        label_css = "msg-label-user" if role == "user" else "msg-label-ai"
        label = "Anda" if role == "user" else "🌿 SAMS"
        content = msg["content"]
        # Strip JSON from display
        display_content = content
        if role == "assistant" and "{" in content:
            import re
            display_content = re.sub(r'\{[^}]*\}', '', content).strip()
        st.markdown(f"""
        <div class="{css}">
            <div class="msg-label {label_css}">{label}</div>
            {display_content}
        </div>
        """, unsafe_allow_html=True)

    # Input form
    with st.container():
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            todo_input = st.text_input(
                "Tulis kegiatan atau tanya jadwal Anda…",
                placeholder='Contoh: "Besok rapat tim jam 10 pagi sampai 12 siang"',
                key="todo_input_field",
                label_visibility="collapsed"
            )
        with col_btn:
            send_todo = st.button("Kirim →", key="send_todo", type="primary", use_container_width=True)

    if send_todo and todo_input.strip():
        user_msg = todo_input.strip()
        st.session_state.todo_messages.append({"role": "user", "content": user_msg})

        with st.spinner("🌿 SAMS sedang memproses…"):
            reply = call_ai(SYSTEM_TODO, st.session_state.todo_messages[-6:], "todo")

        st.session_state.todo_messages.append({"role": "assistant", "content": reply})

        # Parse JSON action
        if '{"action":"add_event"' in reply:
            import re, json as _json
            m = re.search(r'\{[^}]*"action"\s*:\s*"add_event"[^}]*\}', reply, re.DOTALL)
            if m:
                try:
                    data = _json.loads(m.group())
                    ev_date = datetime.datetime.strptime(data["date"], "%Y-%m-%d").date()
                    ev_start = datetime.datetime.strptime(f"{data['date']} {data['start_time']}", "%Y-%m-%d %H:%M")
                    ev_end   = datetime.datetime.strptime(f"{data['date']} {data['end_time']}",   "%Y-%m-%d %H:%M")
                    ok, gcal_msg = add_google_calendar_event(
                        data["title"], data.get("description",""), ev_start, ev_end
                    )
                    ev_entry = {
                        "title": data["title"],
                        "date": data["date"],
                        "start_time": data["start_time"],
                        "end_time": data["end_time"],
                        "description": data.get("description",""),
                        "synced": ok,
                    }
                    st.session_state.todo_events.append(ev_entry)
                    if ok:
                        st.success(gcal_msg)
                    else:
                        st.info(f"💾 Tersimpan lokal. {gcal_msg}")
                except:
                    pass
        st.rerun()

    # Quick-add form
    with st.expander("➕ Tambah Agenda Manual", expanded=False):
        st.markdown("<div style='color:#7ab892;font-size:0.82rem;margin-bottom:0.8rem'>Form cepat untuk menambah agenda tanpa AI</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            qa_title = st.text_input("Judul Kegiatan", placeholder="Nama agenda…", key="qa_title")
        with c2:
            qa_date  = st.date_input("Tanggal", key="qa_date")
        with c3:
            qa_start = st.time_input("Jam Mulai", key="qa_start", value=datetime.time(9, 0))
        c4, c5 = st.columns(2)
        with c4:
            qa_end  = st.time_input("Jam Selesai", key="qa_end", value=datetime.time(10, 0))
        with c5:
            qa_desc = st.text_input("Deskripsi (opsional)", key="qa_desc")
        if st.button("📅 Tambah ke Kalender", key="qa_submit", type="primary"):
            if qa_title:
                start_dt = datetime.datetime.combine(qa_date, qa_start)
                end_dt   = datetime.datetime.combine(qa_date, qa_end)
                ok, msg  = add_google_calendar_event(qa_title, qa_desc, start_dt, end_dt)
                st.session_state.todo_events.append({
                    "title": qa_title, "date": str(qa_date),
                    "start_time": qa_start.strftime("%H:%M"),
                    "end_time": qa_end.strftime("%H:%M"),
                    "description": qa_desc, "synced": ok,
                })
                st.success(msg) if ok else st.info(f"💾 Disimpan lokal. {msg}")
                st.rerun()
            else:
                st.warning("Masukkan judul kegiatan.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 · FINANCIAL AGENT
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    import pandas as pd

    st.markdown("""
    <div class="sams-card">
        <div class="card-title">💰 SAMS Financial Agent
            <span style='font-size:0.7rem;color:#c8a84b;margin-left:auto;
                  background:rgba(200,168,75,0.12);padding:3px 10px;border-radius:12px;
                  border:1px solid rgba(200,168,75,0.3);'>
                Google Sheets Sync
            </span>
        </div>
        <p style='color:#7ab892;font-size:0.82rem;margin:0'>
            Catat semua pemasukan dan pengeluaran Anda. Data tersimpan real-time di Google Sheets.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Summary metrics
    df = pd.DataFrame(st.session_state.finance_entries) if st.session_state.finance_entries else pd.DataFrame(columns=["date","description","type","amount"])
    if not df.empty:
        df["amount"]   = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        df["date"]     = pd.to_datetime(df["date"], errors="coerce")
        today          = pd.Timestamp.now().normalize()
        this_week      = today - pd.Timedelta(days=today.dayofweek)
        this_month_start = today.replace(day=1)

        def period_sum(df_, period_start, ftype):
            mask = (df_["date"] >= period_start) & (df_["type"] == ftype)
            return df_.loc[mask, "amount"].sum()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📅 Pengeluaran Hari Ini",
                    f"Rp {period_sum(df, today, 'pengeluaran'):,.0f}")
        col2.metric("📆 Pengeluaran Minggu Ini",
                    f"Rp {period_sum(df, this_week, 'pengeluaran'):,.0f}")
        col3.metric("🗓️ Pengeluaran Bulan Ini",
                    f"Rp {period_sum(df, this_month_start, 'pengeluaran'):,.0f}")
        col4.metric("💵 Total Pemasukan",
                    f"Rp {df[df['type']=='pemasukan']['amount'].sum():,.0f}")

    st.markdown("<hr class='sams-divider'>", unsafe_allow_html=True)

    # ── Entry form
    st.markdown("<div class='card-title' style='font-size:0.9rem'>➕ Catat Transaksi</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([3, 1.5, 1, 1])
    with c1:
        fin_desc   = st.text_input("Keterangan", placeholder="Contoh: Makan siang, Gaji, Belanja…", key="fin_desc")
    with c2:
        fin_amount = st.number_input("Jumlah (Rp)", min_value=0, step=1000, key="fin_amount", value=0)
    with c3:
        fin_type   = st.selectbox("Jenis", ["pengeluaran","pemasukan"], key="fin_type")
    with c4:
        fin_date   = st.date_input("Tanggal", key="fin_date", value=datetime.date.today())

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("💾 Simpan Transaksi", key="fin_save", type="primary", use_container_width=True):
            if fin_desc and fin_amount > 0:
                entry = {"date": str(fin_date), "description": fin_desc,
                         "type": fin_type, "amount": fin_amount}
                st.session_state.finance_entries.append(entry)
                ok, msg = append_to_google_sheet([entry])
                st.success(f"✅ Transaksi disimpan! {msg}")
                st.rerun()
            else:
                st.warning("Lengkapi keterangan dan jumlah.")
    with col_b:
        if st.button("🤖 AI Analitik Dashboard", key="fin_analytics", type="secondary", use_container_width=True):
            st.session_state.show_analytics = not st.session_state.show_analytics

    # ── Transaction table
    if not df.empty:
        st.markdown("<hr class='sams-divider'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title' style='font-size:0.9rem'>📊 Riwayat Transaksi</div>", unsafe_allow_html=True)
        display_df = df.copy()
        if "date" in display_df.columns:
            display_df["date"] = display_df["date"].astype(str).str[:10]
        display_df["amount"] = display_df["amount"].apply(lambda x: f"Rp {x:,.0f}")
        display_df.columns = ["Tanggal","Keterangan","Jenis","Jumlah"]
        st.dataframe(display_df.tail(20).iloc[::-1].reset_index(drop=True),
                     use_container_width=True, hide_index=True)

    # ── Analytics
    if st.session_state.show_analytics and not df.empty:
        st.markdown("<hr class='sams-divider'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title' style='font-size:0.9rem'>🤖 Analisis Keuangan SAMS</div>", unsafe_allow_html=True)

        # Charts
        try:
            import plotly.graph_objects as go
            import plotly.express as px

            df_plot = df.copy()
            df_plot["date_str"] = df_plot["date"].dt.strftime("%Y-%m-%d")
            daily = df_plot.groupby(["date_str","type"])["amount"].sum().reset_index()

            fig = go.Figure()
            for ftype, color in [("pengeluaran","#e05555"),("pemasukan","#4a8c5c")]:
                sub = daily[daily["type"]==ftype]
                if not sub.empty:
                    fig.add_trace(go.Bar(
                        x=sub["date_str"], y=sub["amount"],
                        name=ftype.capitalize(), marker_color=color, opacity=0.85
                    ))
            fig.update_layout(
                barmode="group",
                plot_bgcolor="rgba(15,30,20,0.8)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#a8d5b5", family="Plus Jakarta Sans"),
                title=dict(text="Pemasukan vs Pengeluaran per Hari",
                           font=dict(color="#a8d5b5", size=14)),
                xaxis=dict(gridcolor="rgba(74,140,92,0.15)", color="#7ab892"),
                yaxis=dict(gridcolor="rgba(74,140,92,0.15)", color="#7ab892",
                           tickprefix="Rp ", tickformat=",.0f"),
                legend=dict(bgcolor="rgba(26,58,42,0.5)", bordercolor="rgba(74,140,92,0.3)"),
                margin=dict(t=50,b=30,l=10,r=10),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Pie chart
            cat_spend = df_plot[df_plot["type"]=="pengeluaran"].groupby("description")["amount"].sum().nlargest(8)
            if not cat_spend.empty:
                fig2 = go.Figure(go.Pie(
                    labels=cat_spend.index, values=cat_spend.values,
                    hole=0.5,
                    marker=dict(colors=px.colors.sequential.Greens_r[:len(cat_spend)]),
                    textfont=dict(color="#e8f5ec")
                ))
                fig2.update_layout(
                    title=dict(text="Distribusi Pengeluaran",
                               font=dict(color="#a8d5b5", size=14)),
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#a8d5b5"),
                    legend=dict(bgcolor="rgba(26,58,42,0.5)"),
                    margin=dict(t=50,b=10,l=10,r=10),
                )
                st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.warning(f"Chart error: {e}")

        # AI advice
        with st.spinner("🌿 SAMS sedang menganalisis keuangan Anda…"):
            total_out = df[df["type"]=="pengeluaran"]["amount"].sum()
            total_in  = df[df["type"]=="pemasukan"]["amount"].sum()
            top_spend = df[df["type"]=="pengeluaran"].groupby("description")["amount"].sum().nlargest(3).to_dict()
            summary   = (f"Total pengeluaran: Rp {total_out:,.0f}, total pemasukan: Rp {total_in:,.0f}. "
                         f"Pengeluaran terbesar: {top_spend}. "
                         f"Jumlah transaksi: {len(df)}.")
            advice = call_ai(
                SYSTEM_FINANCE,
                [{"role":"user","content":f"Analisis keuangan saya dan beri saran:\n{summary}"}],
                "finance"
            )
        st.markdown(f"""
        <div class='sams-card' style='border-color:rgba(200,168,75,0.3)'>
            <div class='card-title'>🤖 Saran AI SAMS</div>
            <div style='color:#e8f5ec;font-size:0.88rem;line-height:1.6'>{advice.replace(chr(10),'<br>')}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── AI Chat for finance
    st.markdown("<hr class='sams-divider'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title' style='font-size:0.9rem'>💬 Tanya SAMS Finance Agent</div>", unsafe_allow_html=True)

    for msg in st.session_state.finance_messages[-4:]:
        css = "chat-msg-user" if msg["role"]=="user" else "chat-msg-ai"
        label = "Anda" if msg["role"]=="user" else "🌿 SAMS"
        label_css = "msg-label-user" if msg["role"]=="user" else "msg-label-ai"
        content = msg["content"]
        if msg["role"]=="assistant" and "{" in content:
            import re
            content = re.sub(r'\{[^}]*\}', '', content).strip()
        st.markdown(f'<div class="{css}"><div class="msg-label {label_css}">{label}</div>{content}</div>',
                    unsafe_allow_html=True)

    cf1, cf2 = st.columns([5,1])
    with cf1:
        fin_chat_input = st.text_input("Tanya tentang keuangan Anda…",
            placeholder='Contoh: "Berapa total pengeluaran minggu ini?"',
            key="fin_chat_input", label_visibility="collapsed")
    with cf2:
        send_fin = st.button("Kirim →", key="send_fin", type="primary", use_container_width=True)

    if send_fin and fin_chat_input.strip():
        summary_ctx = ""
        if not df.empty:
            total_out = df[df["type"]=="pengeluaran"]["amount"].sum()
            total_in  = df[df["type"]=="pemasukan"]["amount"].sum()
            summary_ctx = f"\n[Konteks: Total pengeluaran Rp {total_out:,.0f}, total pemasukan Rp {total_in:,.0f}]"
        st.session_state.finance_messages.append(
            {"role":"user","content": fin_chat_input.strip() + summary_ctx}
        )
        with st.spinner("💰 SAMS menganalisis…"):
            reply = call_ai(SYSTEM_FINANCE, st.session_state.finance_messages[-4:], "finance")
        st.session_state.finance_messages.append({"role":"assistant","content":reply})

        # Parse auto-add entry
        if '{"action":"add_entry"' in reply:
            import re, json as _json
            m = re.search(r'\{[^}]*"action"\s*:\s*"add_entry"[^}]*\}', reply, re.DOTALL)
            if m:
                try:
                    data = _json.loads(m.group())
                    entry = {"date": str(datetime.date.today()),
                             "description": data["description"],
                             "type": data["type"],
                             "amount": data["amount"]}
                    st.session_state.finance_entries.append(entry)
                    append_to_google_sheet([entry])
                    st.success(f"✅ Transaksi '{data['description']}' (Rp {data['amount']:,.0f}) ditambahkan otomatis!")
                except:
                    pass
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 · NOTE AGENT (SPEECH TO TEXT)
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="sams-card">
        <div class="card-title">🎙️ SAMS Note Agent
            <span style='font-size:0.7rem;color:#7ab892;margin-left:auto;
                  background:rgba(74,140,92,0.12);padding:3px 10px;border-radius:12px;
                  border:1px solid rgba(74,140,92,0.3);'>
                Google Drive + Keep
            </span>
        </div>
        <p style='color:#7ab892;font-size:0.82rem;margin:0'>
            Rekam kuliah atau diskusi — SAMS mengubah suara menjadi catatan terstruktur dan menyimpannya otomatis.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Microphone permission check
    if st.session_state.mic_permission is None:
        st.markdown("""
        <div style='background:rgba(26,58,42,0.6);border:1.5px solid rgba(122,184,146,0.4);
                    border-radius:16px;padding:2rem;text-align:center;margin:1rem 0;'>
            <div style='font-size:3rem;margin-bottom:0.8rem'>🎤</div>
            <div style='font-family:"Playfair Display",serif;font-size:1.3rem;color:#a8d5b5;margin-bottom:0.5rem'>
                Izinkan Akses Mikrofon?
            </div>
            <div style='color:#7ab892;font-size:0.85rem;max-width:400px;margin:0 auto 1.2rem'>
                SAMS memerlukan akses mikrofon untuk merekam percakapan dan mengubahnya menjadi teks.
                Audio akan dihapus otomatis setelah ditranskripsi.
            </div>
        </div>
        """, unsafe_allow_html=True)
        col_y, col_n = st.columns(2)
        with col_y:
            if st.button("✅ Izinkan Mikrofon", type="primary", use_container_width=True, key="allow_mic"):
                st.session_state.mic_permission = True
                st.rerun()
        with col_n:
            if st.button("❌ Tolak", type="secondary", use_container_width=True, key="deny_mic"):
                st.session_state.mic_permission = False
                st.rerun()

    elif st.session_state.mic_permission is False:
        st.error("🚫 Akses mikrofon ditolak. Refresh halaman untuk mencoba lagi, atau gunakan upload file audio.")
        if st.button("🔄 Coba Lagi", key="retry_mic"):
            st.session_state.mic_permission = None
            st.rerun()

    else:
        # ── Recording interface
        st.markdown("<div class='card-title' style='font-size:0.9rem'>🎙️ Sesi Rekaman Baru</div>",
                    unsafe_allow_html=True)

        note_title_val = st.text_input(
            "Judul Catatan",
            placeholder="Contoh: Kuliah Pemrograman AI - 11 April 2026",
            key="note_title_input",
            value=st.session_state.note_title,
        )
        st.session_state.note_title = note_title_val

        st.markdown("""
        <div style='background:rgba(200,168,75,0.08);border:1px solid rgba(200,168,75,0.25);
                    border-radius:10px;padding:0.8rem 1rem;margin:0.5rem 0;font-size:0.8rem;color:#c8a84b;'>
            ⚠️ <strong>Catatan:</strong> Rekaman suara disimpan sementara di Google Drive (maks. 1 jam).
            Setelah berhasil ditranskripsi, file audio akan dihapus otomatis.
        </div>
        """, unsafe_allow_html=True)

        # Upload audio file (browser-compatible alternative to live recording)
        st.markdown("<hr class='sams-divider'>", unsafe_allow_html=True)
        st.markdown("<div style='color:#7ab892;font-size:0.82rem;margin-bottom:0.5rem'>📁 Upload File Audio (WAV/MP3/M4A, maks. 25MB)</div>", unsafe_allow_html=True)

        uploaded_audio = st.file_uploader(
            "Upload Audio", type=["wav","mp3","m4a","ogg","flac"],
            key="audio_upload", label_visibility="collapsed"
        )

        if uploaded_audio:
            st.audio(uploaded_audio, format=uploaded_audio.type)
            st.session_state.audio_bytes = uploaded_audio.read()
            st.success(f"✅ File '{uploaded_audio.name}' siap ditranskripsi ({len(st.session_state.audio_bytes)//1024} KB)")

        if st.session_state.audio_bytes:
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                if st.button("🌿 Transkripsi dengan Whisper AI", type="primary",
                             use_container_width=True, key="transcribe_btn"):
                    if not st.session_state.note_title.strip():
                        st.warning("⚠️ Masukkan judul catatan terlebih dahulu!")
                    else:
                        with st.spinner("🎙️ Mengunggah audio ke Google Drive…"):
                            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"SAMS_{st.session_state.note_title.replace(' ','_')}_{ts}.wav"
                            file_id, drive_msg = upload_audio_to_drive(
                                st.session_state.audio_bytes, filename
                            )
                            st.info(f"☁️ {drive_msg}")

                        with st.spinner("✍️ Transkripsi sedang berjalan…"):
                            transcript = transcribe_audio(st.session_state.audio_bytes)

                        if "Error" not in transcript:
                            with st.spinner("🤖 SAMS merangkum catatan…"):
                                notes = call_ai(
                                    SYSTEM_NOTE,
                                    [{"role":"user","content":
                                      f"Judul: {st.session_state.note_title}\n\nTranskripsi:\n{transcript}"}],
                                    "note"
                                )
                            entry = {
                                "title": st.session_state.note_title,
                                "timestamp": datetime.datetime.now().strftime("%d %b %Y %H:%M"),
                                "transcript": transcript,
                                "notes": notes,
                                "drive_file_id": file_id,
                            }
                            st.session_state.note_transcriptions.append(entry)

                            # Delete drive file
                            if file_id:
                                with st.spinner("🗑️ Menghapus file audio dari Drive…"):
                                    delete_drive_file(file_id)
                                st.success("✅ File audio dihapus dari Google Drive setelah transkripsi.")

                            st.session_state.audio_bytes = None
                            st.session_state.note_title = ""
                            st.rerun()
                        else:
                            st.error(f"❌ {transcript}")
            with col_t2:
                if st.button("🗑️ Hapus Audio", type="secondary", use_container_width=True, key="clear_audio"):
                    st.session_state.audio_bytes = None
                    st.rerun()

        # ── Saved transcriptions
        if st.session_state.note_transcriptions:
            st.markdown("<hr class='sams-divider'>", unsafe_allow_html=True)
            st.markdown("<div class='card-title' style='font-size:0.9rem'>📝 Catatan Tersimpan</div>",
                        unsafe_allow_html=True)
            for i, entry in enumerate(reversed(st.session_state.note_transcriptions)):
                with st.expander(f"📄 {entry['title']} · {entry['timestamp']}"):
                    tab_t, tab_n = st.tabs(["📝 Catatan Terstruktur","📜 Transkripsi Asli"])
                    with tab_t:
                        st.markdown(f"<div style='color:#e8f5ec;font-size:0.88rem;line-height:1.7'>{entry['notes'].replace(chr(10),'<br>')}</div>",
                                    unsafe_allow_html=True)
                    with tab_n:
                        st.markdown(f"<div style='color:#a8d5b5;font-size:0.83rem;line-height:1.6;font-family:monospace;background:rgba(10,30,18,0.5);padding:1rem;border-radius:8px'>{entry['transcript']}</div>",
                                    unsafe_allow_html=True)

        # ── AI Chat for notes
        if st.session_state.note_transcriptions:
            st.markdown("<hr class='sams-divider'>", unsafe_allow_html=True)
            st.markdown("<div class='card-title' style='font-size:0.9rem'>💬 Tanya Tentang Catatan Anda</div>",
                        unsafe_allow_html=True)
            for msg in st.session_state.note_messages[-4:]:
                css = "chat-msg-user" if msg["role"]=="user" else "chat-msg-ai"
                label = "Anda" if msg["role"]=="user" else "🌿 SAMS"
                label_css = "msg-label-user" if msg["role"]=="user" else "msg-label-ai"
                st.markdown(f'<div class="{css}"><div class="msg-label {label_css}">{label}</div>{msg["content"]}</div>',
                            unsafe_allow_html=True)

            cn1, cn2 = st.columns([5,1])
            with cn1:
                note_q = st.text_input("Tanya tentang catatan…",
                    placeholder='Contoh: "Apa poin utama kuliah tadi?"',
                    key="note_chat_input", label_visibility="collapsed")
            with cn2:
                send_note = st.button("Kirim →", key="send_note", type="primary", use_container_width=True)

            if send_note and note_q.strip():
                latest = st.session_state.note_transcriptions[-1]
                ctx = f"[Catatan: {latest['title']}]\n{latest['notes']}"
                st.session_state.note_messages.append(
                    {"role":"user","content": f"{note_q.strip()}\n\n{ctx}"}
                )
                with st.spinner("🌿 SAMS menganalisis catatan…"):
                    reply = call_ai(SYSTEM_NOTE, st.session_state.note_messages[-4:], "note")
                st.session_state.note_messages.append({"role":"assistant","content":reply})
                st.rerun()

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;margin-top:2rem;padding:1.5rem 0;
            border-top:1px solid rgba(74,140,92,0.2);'>
    <div style='font-family:"Playfair Display",serif;font-size:1rem;
                background:linear-gradient(135deg,#a8d5b5,#7ab892);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                margin-bottom:0.3rem;'>
        🌿 SAMS Agent
    </div>
    <div style='color:rgba(122,184,146,0.5);font-size:0.72rem;letter-spacing:1.5px;text-transform:uppercase'>
        Smart Autonomous Management System · Built with ♻️ Sustainable Spirit
    </div>
</div>
""", unsafe_allow_html=True)