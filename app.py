"""
SAMS Financial Agent — Google Sheets Integration
=================================================
Persyaratan:
  pip install streamlit openai gspread google-auth pandas plotly

Konfigurasi Streamlit Secrets (.streamlit/secrets.toml):
OPENAI_API_KEY = "sk-proj-..."
GOOGLE_SHEET_ID = "..."
[google_sheets]
sheet_name = "Finance"
[google_calendar]
calendar_id = "your-email@gmail.com"
timezone    = "Asia/Jakarta"
[gcp_service_account]
...
"""

import streamlit as st
import os, json, re, datetime
import pandas as pd
from typing import Optional

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SAMS Agent",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── GLOBAL STYLE ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,700;1,400&display=swap');

:root {
    --forest: #1a3a2a; --moss: #2d5a3d; --leaf: #4a8c5c;
    --sage: #7ab892;   --mint: #a8d5b5; --cream: #f0f7f2;
    --gold: #c8a84b;   --amber: #e8b84b; --red: #e05555;
    --glass: rgba(255,255,255,0.06);
    --glass-border: rgba(255,255,255,0.12);
    --radius: 16px; --radius-sm: 10px;
}

html, body, [data-testid="stApp"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: linear-gradient(135deg, #0d2318 0%, #1a3a2a 40%, #0f2d1c 100%) !important;
    min-height: 100vh;
    color: var(--cream) !important;
}

.main .block-container { padding-top: 1.5rem !important; max-width: 1100px !important; }

.card {
    background: rgba(26,58,42,0.55);
    border: 1px solid rgba(74,140,92,0.25);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    backdrop-filter: blur(18px);
    margin-bottom: 1rem;
    box-shadow: 0 6px 28px rgba(0,0,0,0.35);
}
.card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    color: var(--mint);
    margin-bottom: .7rem;
    display: flex; align-items: center; gap: .5rem;
}

[data-testid="stTextInput"] > div > div,
[data-testid="stNumberInput"] > div > div,
[data-testid="stDateInput"] > div > div,
[data-testid="stSelectbox"] > div > div {
    background: rgba(8,24,14,0.9) !important;
    border: 1.5px solid rgba(122,184,146,0.4) !important;
    border-radius: var(--radius-sm) !important;
}
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTextInput"] input::placeholder,
[data-testid="stNumberInput"] input::placeholder {
    background: transparent !important;
    color: #e8f5ec !important;
    -webkit-text-fill-color: #e8f5ec !important;
    caret-color: #a8d5b5 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    opacity: 1 !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stNumberInput"] input::placeholder {
    color: rgba(168,213,181,0.5) !important;
    -webkit-text-fill-color: rgba(168,213,181,0.5) !important;
}
[data-testid="stSelectbox"] > div > div > div,
[data-testid="stSelectbox"] span {
    color: #e8f5ec !important;
    -webkit-text-fill-color: #e8f5ec !important;
}
[data-testid="stDateInput"] input {
    color: #e8f5ec !important;
    -webkit-text-fill-color: #e8f5ec !important;
}
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stDateInput"] label,
[data-testid="stSelectbox"] label { color: var(--sage) !important; font-weight: 600 !important; font-size: 0.8rem !important; }
[data-testid="stTextInput"] > div > div > div,
[data-testid="stNumberInput"] > div > div > div {
    background: transparent !important;
}

[data-testid="stButton"] button {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    border-radius: var(--radius-sm) !important;
    border: none !important;
    transition: all .2s ease !important;
}
[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, var(--moss), var(--leaf)) !important;
    color: #fff !important;
    box-shadow: 0 4px 16px rgba(74,140,92,0.4) !important;
}
[data-testid="stButton"] button[kind="primary"]:hover { transform: translateY(-1px) !important; }
[data-testid="stButton"] button[kind="secondary"] {
    background: rgba(74,140,92,0.12) !important;
    color: var(--sage) !important;
    border: 1px solid rgba(74,140,92,0.3) !important;
}

[data-testid="metric-container"] {
    background: rgba(26,58,42,0.5) !important;
    border: 1px solid rgba(74,140,92,0.2) !important;
    border-radius: var(--radius) !important;
    padding: 1rem !important;
}
[data-testid="metric-container"] label { color: var(--sage) !important; font-size: .75rem !important; }
[data-testid="stMetricValue"] { color: var(--mint) !important; font-weight: 700 !important; }

.msg-user { background:rgba(45,90,61,.4);border:1px solid rgba(74,140,92,.3);
    border-radius:10px 0 10px 10px;padding:.7rem 1rem;margin:.4rem 0 .4rem 3rem;font-size:.87rem; }
.msg-ai { background:rgba(12,32,20,.65);border:1px solid rgba(122,184,146,.2);
    border-radius:0 10px 10px 10px;padding:.7rem 1rem;margin:.4rem 3rem .4rem 0;font-size:.87rem; }
.msg-lbl { font-size:.68rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:.25rem; }

.divider { border:none;border-top:1px solid rgba(74,140,92,0.18);margin:.8rem 0; }

.pill {
    display:inline-flex;align-items:center;gap:6px;
    padding:3px 11px;border-radius:20px;font-size:.72rem;font-weight:600;letter-spacing:.4px;
}
.pill-green { background:rgba(74,140,92,.18);color:var(--sage);border:1px solid rgba(74,140,92,.35); }
.pill-amber { background:rgba(200,168,75,.14);color:var(--amber);border:1px solid rgba(200,168,75,.35); }
.pill-red   { background:rgba(224,85,85,.14);color:#e08888;border:1px solid rgba(224,85,85,.35); }

#MainMenu, footer, header { visibility:hidden !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def get_secret(key: str, default=None):
    try:
        val = st.secrets[key]
        return str(val) if val is not None else default
    except Exception:
        return os.getenv(key, default)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — GOOGLE SHEETS CLIENT
# ══════════════════════════════════════════════════════════════════════════════

SHEET_TAB = "Finance"
SHEET_HEADERS = ["Tanggal", "Keterangan", "Jenis", "Jumlah (Rp)", "Timestamp Input"]

@st.cache_resource(show_spinner=False)
def get_gspread_client():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        sa = st.secrets["gcp_service_account"]
        info = {
            "type":                        str(sa.get("type", "service_account")),
            "project_id":                  str(sa["project_id"]),
            "private_key_id":              str(sa["private_key_id"]),
            "private_key":                 str(sa["private_key"]).replace("\\n", "\n"),
            "client_email":                str(sa["client_email"]),
            "client_id":                   str(sa["client_id"]),
            "auth_uri":                    str(sa.get("auth_uri", "https://accounts.google.com/o/oauth2/auth")),
            "token_uri":                   str(sa.get("token_uri", "https://oauth2.googleapis.com/token")),
            "auth_provider_x509_cert_url": str(sa.get("auth_provider_x509_cert_url",
                                               "https://www.googleapis.com/oauth2/v1/certs")),
            "client_x509_cert_url":        str(sa.get("client_x509_cert_url", "")),
            "universe_domain":             str(sa.get("universe_domain", "googleapis.com")),
        }
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/calendar",
        ]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds)
    except KeyError as e:
        st.error(f"Field tidak ditemukan di [gcp_service_account]: {e}")
        return None
    except Exception as e:
        st.error(f"Gagal membuat koneksi Google: {e}")
        return None


def get_sheet_tab_name() -> str:
    try:
        name = str(st.secrets["google_sheets"]["sheet_name"])
        return name if name.strip() else SHEET_TAB
    except Exception:
        return SHEET_TAB


@st.cache_resource(show_spinner=False)
def get_worksheet():
    gc = get_gspread_client()
    sheet_id = get_secret("GOOGLE_SHEET_ID")
    if not gc or not sheet_id:
        return None, "Konfigurasi belum lengkap (lihat sidebar)."
    try:
        spreadsheet = gc.open_by_key(sheet_id)
    except Exception as e:
        return None, f"Tidak bisa membuka spreadsheet: {e}"
    tab_name = get_sheet_tab_name()
    try:
        ws = spreadsheet.worksheet(tab_name)
    except Exception:
        ws = spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=10)
        ws.append_row(SHEET_HEADERS, value_input_option="USER_ENTERED")
    try:
        first_row = ws.row_values(1)
        if first_row != SHEET_HEADERS:
            ws.insert_row(SHEET_HEADERS, index=1)
    except Exception:
        pass
    return ws, f"Terhubung ke Google Sheets (tab: {tab_name})"


def sheet_status() -> tuple[bool, str]:
    ws, msg = get_worksheet()
    return (ws is not None), msg


def load_finance_from_sheet() -> list[dict]:
    ws, _ = get_worksheet()
    if ws is None:
        return []
    try:
        rows = ws.get_all_records(expected_headers=SHEET_HEADERS)
        entries = []
        for r in rows:
            try:
                entries.append({
                    "date":        str(r.get("Tanggal", "")),
                    "description": str(r.get("Keterangan", "")),
                    "type":        str(r.get("Jenis", "pengeluaran")),
                    "amount":      float(str(r.get("Jumlah (Rp)", 0)).replace(",", "").replace(".", "").strip() or 0),
                    "ts":          str(r.get("Timestamp Input", "")),
                })
            except Exception:
                pass
        return entries
    except Exception as e:
        st.warning(f"Gagal membaca sheet: {e}")
        return []


def append_finance_to_sheet(entry: dict) -> tuple[bool, str]:
    ws, msg = get_worksheet()
    if ws is None:
        return False, msg
    try:
        ts_now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        row = [entry["date"], entry["description"], entry["type"], entry["amount"], ts_now]
        ws.append_row(row, value_input_option="USER_ENTERED")
        return True, "Tersimpan ke Google Sheets"
    except Exception as e:
        return False, f"Gagal menyimpan: {e}"


def delete_finance_row(sheet_row_index: int) -> tuple[bool, str]:
    ws, msg = get_worksheet()
    if ws is None:
        return False, msg
    try:
        ws.delete_rows(sheet_row_index)
        return True, "Data dihapus dari Google Sheets"
    except Exception as e:
        return False, f"Gagal menghapus: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — AI (OpenAI)
# ══════════════════════════════════════════════════════════════════════════════

MAX_BUDGET_USD = 0.05

def get_openai_api_key() -> str:
    try:
        raw = st.secrets["OPENAI_API_KEY"]
        key = str(raw).strip()
        if key:
            return key
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY", "").strip()

def get_openai_client():
    from openai import OpenAI
    key = get_openai_api_key()
    if not key:
        raise ValueError("OPENAI_API_KEY tidak ditemukan di Secrets maupun environment.")
    if not key.startswith("sk-"):
        raise ValueError(f"OPENAI_API_KEY tidak valid (harus diawali 'sk-'). Nilai saat ini: '{key[:8]}...'")
    return OpenAI(api_key=key)

def tokens_to_usd(tokens: int) -> float:
    return tokens * 0.0000005

SYSTEM_FINANCE = """Kamu adalah SAMS Finance Agent, asisten keuangan cerdas berbahasa Indonesia.
Bantu user mencatat pengeluaran dan pemasukan.

Jika user menyebut transaksi baru, ekstrak informasi dan balas HANYA dengan JSON ini (plus kalimat konfirmasi):
{"action":"add_entry","description":"...","type":"pengeluaran|pemasukan","amount":ANGKA_INTEGER}

Aturan:
- "amount" harus angka INTEGER (tanpa Rp, tanpa koma)
- "type" hanya boleh "pengeluaran" atau "pemasukan"
- Jika tidak ada transaksi, balas normal tanpa JSON

Jika user minta analisis atau saran, berikan insight keuangan yang berguna dan actionable.
Gunakan format rupiah (Rp X.XXX) saat menyebut angka. Singkat, ramah, profesional."""

def call_ai(messages: list) -> str:
    if st.session_state.get("budget_exceeded"):
        return "Budget sesi habis. Refresh halaman untuk memulai sesi baru."
    used_usd = tokens_to_usd(st.session_state.get("total_tokens", 0))
    remaining = MAX_BUDGET_USD - used_usd
    if remaining <= 0:
        st.session_state["budget_exceeded"] = True
        return "Budget sesi habis."
    max_tokens = min(600, int(remaining / 0.0000006))
    if max_tokens < 40:
        st.session_state["budget_exceeded"] = True
        return "Budget hampir habis. Refresh untuk sesi baru."
    try:
        client = get_openai_client()
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": SYSTEM_FINANCE}] + messages,
            max_tokens=max_tokens,
            temperature=0.6,
        )
        used = resp.usage.total_tokens if resp.usage else 200
        st.session_state["total_tokens"] = st.session_state.get("total_tokens", 0) + used
        return resp.choices[0].message.content
    except ValueError as e:
        return f"Konfigurasi API Key bermasalah: {e}"
    except Exception as e:
        err_str = str(e)
        if "401" in err_str or "Unauthorized" in err_str or "invalid_api_key" in err_str.lower():
            return (
                "**OpenAI API Key tidak valid (Error 401)**\n\n"
                "Kemungkinan penyebab:\n"
                "1. Key salah atau sudah kedaluwarsa\n"
                "2. Key belum diisi di Streamlit Secrets\n"
                "3. Ada spasi/karakter tersembunyi di key\n\n"
                "**Solusi:** Buka [platform.openai.com/api-keys](https://platform.openai.com/api-keys) buat key baru paste ke Secrets."
            )
        return f"Error AI: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# PERBAIKAN UTAMA — SYSTEM PROMPT TODO + PARSER JSON ROBUST
# ══════════════════════════════════════════════════════════════════════════════
#
# MASALAH ASAL:
#   Regex lama r'\{[^{}]*"action"\s*:\s*"add_event"[^{}]*\}' GAGAL karena:
#   - [^{}]* tidak mengizinkan newline dalam JSON multi-baris
#   - AI sering mengembalikan JSON dengan line-break di dalam key/value
#   - Tidak ada fallback jika regex pertama gagal
#
# SOLUSI:
#   1. SYSTEM_TODO diperketat: AI diwajibkan menulis JSON dalam SATU BARIS
#      dengan contoh format yang eksplisit
#   2. extract_event_json(): 3 strategi parsing berurutan
#      - Strategi 1: regex dengan [^{}]* (cepat, untuk JSON 1 baris)
#      - Strategi 2: brace-matching manual (untuk JSON multi-baris)
#      - Strategi 3: key-value regex manual (last resort)
#   3. validate_event_data(): normalisasi & validasi sebelum kirim ke Calendar
# ══════════════════════════════════════════════════════════════════════════════

SYSTEM_TODO = """Kamu adalah SAMS Todo Agent, asisten jadwal cerdas berbahasa Indonesia.
Tugasmu: ekstrak informasi kegiatan dari pesan user dan simpan ke Google Calendar.

WAJIB — JIKA ADA KEGIATAN BARU UNTUK DIJADWALKAN:
Tulis kalimat konfirmasi singkat, lalu di baris baru tulis JSON dalam SATU BARIS penuh:
{{"action":"add_event","title":"JUDUL","date":"YYYY-MM-DD","start_time":"HH:MM","end_time":"HH:MM","description":"DESKRIPSI","location":"LOKASI"}}

CONTOH RESPONS YANG BENAR:
Siap! Saya jadwalkan rapat tim untuk besok pagi.
{{"action":"add_event","title":"Rapat Tim","date":"2025-04-14","start_time":"09:00","end_time":"11:00","description":"Rapat tim mingguan","location":"Kantor"}}

ATURAN JSON — WAJIB DIIKUTI:
- Semua 7 key harus ada: action, title, date, start_time, end_time, description, location
- "date" format YYYY-MM-DD. Hari ini: {today}. "besok" = tambah 1 hari dari hari ini
- "start_time" dan "end_time" format HH:MM (24 jam). Contoh: "09:00", "14:30"
- Jika end_time tidak disebutkan, tambahkan 1 jam dari start_time
- "location" dan "description" boleh string kosong "" jika tidak disebutkan
- JSON HARUS dalam satu baris — JANGAN gunakan newline atau indentasi di dalam JSON
- JSON HARUS lengkap dan valid — jangan potong di tengah

JIKA TIDAK ADA KEGIATAN BARU: balas normal tanpa JSON sama sekali.
Gunakan bahasa Indonesia yang ramah dan singkat."""


def extract_event_json(text: str) -> Optional[dict]:
    """
    Ekstrak JSON event dari teks AI dengan 3 strategi fallback.
    Return dict jika berhasil, None jika tidak ada event ditemukan.
    """
    if not text or "add_event" not in text:
        return None

    # Strategi 1: regex [^{}]* — cepat, cocok JSON 1 baris
    for m in re.findall(r'\{[^{}]+\}', text):
        try:
            data = json.loads(m)
            if data.get("action") == "add_event":
                return data
        except Exception:
            pass

    # Strategi 2: brace-matching manual — menangani JSON multi-baris
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[start:i + 1]
                    # Bersihkan whitespace berlebih sebelum parse
                    clean = re.sub(r'\s+', ' ', candidate).strip()
                    try:
                        data = json.loads(clean)
                        if data.get("action") == "add_event":
                            return data
                    except Exception:
                        pass
                    break
        start = text.find("{", start + 1)

    # Strategi 3: ekstrak key-value secara individual (last resort)
    normalized_text = text.replace(" ", "")
    if '"action":"add_event"' in normalized_text:
        extracted = {}
        for key in ["action", "title", "date", "start_time", "end_time", "description", "location"]:
            m = re.search(r'"' + key + r'"\s*:\s*"([^"]*)"', text)
            if m:
                extracted[key] = m.group(1)
        if extracted.get("action") == "add_event" and extracted.get("title") and extracted.get("date"):
            return extracted

    return None


def validate_event_data(data: dict) -> tuple[bool, str, dict]:
    """
    Validasi dan normalisasi data event.
    Return: (valid, pesan_error, data_ternormalisasi)
    """
    today_str = str(datetime.date.today())

    title = str(data.get("title", "")).strip()
    if not title:
        return False, "Judul kegiatan tidak boleh kosong", {}

    date_str = str(data.get("date", today_str)).strip()
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        date_str = today_str  # fallback ke hari ini jika format salah

    start_time = str(data.get("start_time", "09:00")).strip()
    end_time   = str(data.get("end_time",   "10:00")).strip()

    time_re = re.compile(r'^\d{1,2}:\d{2}$')
    if not time_re.match(start_time):
        start_time = "09:00"
    if not time_re.match(end_time):
        try:
            h, mn = map(int, start_time.split(":"))
            end_time = f"{(h + 1) % 24:02d}:{mn:02d}"
        except Exception:
            end_time = "10:00"

    # Pastikan end > start
    try:
        sh, sm = map(int, start_time.split(":"))
        eh, em = map(int, end_time.split(":"))
        if (eh * 60 + em) <= (sh * 60 + sm):
            end_time = f"{(sh + 1) % 24:02d}:{sm:02d}"
    except Exception:
        pass

    return True, "", {
        "title":       title,
        "date":        date_str,
        "start_time":  start_time,
        "end_time":    end_time,
        "description": str(data.get("description", "")).strip(),
        "location":    str(data.get("location",    "")).strip(),
    }


def call_ai_todo(messages: list) -> str:
    """AI call khusus Todo Agent."""
    if st.session_state.get("budget_exceeded"):
        return "Budget sesi habis. Refresh halaman untuk memulai sesi baru."
    used_usd = tokens_to_usd(st.session_state.get("total_tokens", 0))
    remaining = MAX_BUDGET_USD - used_usd
    if remaining <= 0:
        st.session_state["budget_exceeded"] = True
        return "Budget sesi habis."
    max_tokens = min(600, int(remaining / 0.0000006))
    if max_tokens < 40:
        st.session_state["budget_exceeded"] = True
        return "Budget hampir habis. Refresh untuk sesi baru."

    system = SYSTEM_TODO.format(today=str(datetime.date.today()))

    try:
        client = get_openai_client()
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system}] + messages,
            max_tokens=max_tokens,
            temperature=0.3,  # Diturunkan agar format JSON lebih konsisten
        )
        used = resp.usage.total_tokens if resp.usage else 200
        st.session_state["total_tokens"] = st.session_state.get("total_tokens", 0) + used
        return resp.choices[0].message.content
    except ValueError as e:
        return f"Konfigurasi API Key bermasalah: {e}"
    except Exception as e:
        err_str = str(e)
        if "401" in err_str or "Unauthorized" in err_str or "invalid_api_key" in err_str.lower():
            return (
                "**OpenAI API Key tidak valid (Error 401)**\n\n"
                "Buka [platform.openai.com/api-keys](https://platform.openai.com/api-keys) "
                "buat key baru paste ke Streamlit Secrets sebagai OPENAI_API_KEY."
            )
        return f"Error AI: {e}"


# ── GOOGLE CALENDAR HELPERS ──────────────────────────────────────────────────

def get_calendar_id() -> str:
    try:
        return str(st.secrets["google_calendar"]["calendar_id"])
    except Exception:
        return get_secret("GOOGLE_CALENDAR_ID", "primary")


def get_calendar_timezone() -> str:
    try:
        return str(st.secrets["google_calendar"]["timezone"])
    except Exception:
        return "Asia/Jakarta"


@st.cache_resource(show_spinner=False)
def get_calendar_service():
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        sa = st.secrets["gcp_service_account"]
        info = {
            "type":                        str(sa.get("type", "service_account")),
            "project_id":                  str(sa["project_id"]),
            "private_key_id":              str(sa["private_key_id"]),
            "private_key":                 str(sa["private_key"]).replace("\\n", "\n"),
            "client_email":                str(sa["client_email"]),
            "client_id":                   str(sa["client_id"]),
            "auth_uri":                    str(sa.get("auth_uri", "https://accounts.google.com/o/oauth2/auth")),
            "token_uri":                   str(sa.get("token_uri", "https://oauth2.googleapis.com/token")),
            "auth_provider_x509_cert_url": str(sa.get("auth_provider_x509_cert_url",
                                               "https://www.googleapis.com/oauth2/v1/certs")),
            "client_x509_cert_url":        str(sa.get("client_x509_cert_url", "")),
            "universe_domain":             str(sa.get("universe_domain", "googleapis.com")),
        }
        scopes = ["https://www.googleapis.com/auth/calendar"]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return build("calendar", "v3", credentials=creds), None
    except KeyError as e:
        return None, f"Field tidak ditemukan: {e}"
    except Exception as e:
        return None, str(e)


def add_google_calendar_event(title: str, date_str: str, start_time: str,
                               end_time: str, description: str = "",
                               location: str = "") -> tuple[bool, str, str]:
    svc, err = get_calendar_service()
    if svc is None:
        return False, f"Gagal konek Calendar: {err}", ""
    tz = get_calendar_timezone()
    cal_id = get_calendar_id()
    try:
        body = {
            "summary":     title,
            "description": description,
            "location":    location,
            "start":       {"dateTime": f"{date_str}T{start_time}:00", "timeZone": tz},
            "end":         {"dateTime": f"{date_str}T{end_time}:00",   "timeZone": tz},
            "reminders":   {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 30},
                    {"method": "email", "minutes": 60},
                ],
            },
        }
        result = svc.events().insert(calendarId=cal_id, body=body).execute()
        return True, "Event berhasil ditambahkan ke Google Calendar", result.get("htmlLink", "")
    except Exception as e:
        return False, f"Gagal tambah event: {e}", ""


def load_upcoming_events(max_results: int = 20) -> list[dict]:
    svc, _ = get_calendar_service()
    if svc is None:
        return []
    try:
        now = datetime.datetime.utcnow().isoformat() + "Z"
        result = svc.events().list(
            calendarId=get_calendar_id(),
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        events = []
        for item in result.get("items", []):
            start = item.get("start", {})
            end   = item.get("end", {})
            events.append({
                "id":          item.get("id", ""),
                "title":       item.get("summary", "(tanpa judul)"),
                "start":       start.get("dateTime", start.get("date", "")),
                "end":         end.get("dateTime",   end.get("date",   "")),
                "description": item.get("description", ""),
                "location":    item.get("location", ""),
                "link":        item.get("htmlLink", ""),
            })
        return events
    except Exception:
        return []


def delete_calendar_event(event_id: str) -> tuple[bool, str]:
    svc, err = get_calendar_service()
    if svc is None:
        return False, f"{err}"
    try:
        svc.events().delete(calendarId=get_calendar_id(), eventId=event_id).execute()
        return True, "Event dihapus"
    except Exception as e:
        return False, f"Gagal hapus: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — SESSION STATE INIT
# ══════════════════════════════════════════════════════════════════════════════

def init_state():
    defaults = {
        "total_tokens":       0,
        "budget_exceeded":    False,
        "finance_entries":    [],
        "chat_messages":      [],
        "sheet_loaded":       False,
        "show_analytics":     False,
        "delete_confirm_idx": None,
        "todo_messages":      [],
        "todo_events_cache":  [],
        "todo_cache_loaded":  False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════

if not st.session_state["sheet_loaded"]:
    with st.spinner("🌿 Memuat data keuangan dari Google Sheets…"):
        loaded = load_finance_from_sheet()
    if loaded:
        st.session_state["finance_entries"] = loaded
    st.session_state["sheet_loaded"] = True

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — UI
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style='text-align:center;padding:1.5rem 0 1rem;'>
  <div style='font-family:"Playfair Display",serif;font-size:2.8rem;font-weight:700;
       background:linear-gradient(135deg,#a8d5b5,#7ab892,#c8a84b);
       -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
    🌿 SAMS Agent
  </div>
  <div style='color:#7ab892;font-size:.8rem;letter-spacing:3px;text-transform:uppercase;margin-top:.3rem;'>
    Google Sheets · Google Calendar · Real-time Sync
  </div>
</div>
""", unsafe_allow_html=True)

# ── STATUS STRIP ─────────────────────────────────────────────────────────────
gs_ok, gs_msg = sheet_status()
openai_key    = get_openai_api_key()
openai_ok     = bool(openai_key and openai_key.startswith("sk-"))

used_usd = tokens_to_usd(st.session_state["total_tokens"])
pct = min(100, int(used_usd / MAX_BUDGET_USD * 100))
bar_col = "#e05555" if pct > 80 else "#c8a84b" if pct > 50 else "#4a8c5c"

col_s1, col_s2, col_s3 = st.columns([1, 1, 2])
with col_s1:
    if gs_ok:
        st.markdown('<span class="pill pill-green">● Google Sheets Terhubung</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="pill pill-red">● Sheets Tidak Terhubung</span>', unsafe_allow_html=True)
with col_s2:
    if openai_ok:
        st.markdown('<span class="pill pill-green">● OpenAI Aktif</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="pill pill-amber">● OpenAI Belum Dikonfigurasi</span>', unsafe_allow_html=True)
with col_s3:
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:8px;font-size:.76rem;color:#7ab892;'>
      <span>💰 Budget Sesi</span>
      <div style='flex:1;height:5px;background:rgba(255,255,255,.08);border-radius:3px;overflow:hidden;'>
        <div style='width:{pct}%;height:100%;background:{bar_col};border-radius:3px;transition:width .4s;'></div>
      </div>
      <span style='font-weight:700;color:{"#e08888" if pct>80 else "#a8d5b5"}'>${used_usd:.4f}/${MAX_BUDGET_USD:.2f}</span>
    </div>
    """, unsafe_allow_html=True)

if not openai_ok:
    st.warning(
        "⚠️ **OPENAI_API_KEY belum dikonfigurasi atau tidak valid.**\n\n"
        "Buka **Settings → Secrets** di Streamlit Cloud dan tambahkan:\n"
        "```\nOPENAI_API_KEY = \"sk-proj-...\"\n```\n"
        "Dapatkan key baru di [platform.openai.com/api-keys](https://platform.openai.com/api-keys)"
    )

st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Konfigurasi")
    st.markdown("---")
    raw_key = get_openai_api_key()
    if raw_key:
        masked = raw_key[:7] + "..." + raw_key[-4:] if len(raw_key) > 11 else "***"
        if raw_key.startswith("sk-"):
            st.success(f"✅ API Key terdeteksi: `{masked}`")
        else:
            st.error(f"❌ Key tidak valid: `{masked}`")
    else:
        st.error("❌ OPENAI_API_KEY tidak ditemukan")
    st.markdown("---")
    st.code("""
OPENAI_API_KEY = "sk-proj-..."
GOOGLE_SHEET_ID = "..."

[google_sheets]
sheet_name = "Finance"

[google_calendar]
calendar_id = "email@gmail.com"
timezone    = "Asia/Jakarta"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
client_email = "...@....iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
""", language="toml")
    st.markdown("---")
    if st.button("🔄 Reload Data dari Sheets", use_container_width=True):
        st.session_state["sheet_loaded"] = False
        st.session_state["finance_entries"] = []
        st.rerun()
    if st.button("🔄 Reload Events Calendar", use_container_width=True, type="secondary"):
        st.session_state["todo_cache_loaded"] = False
        st.session_state["todo_events_cache"] = []
        st.rerun()
    if st.button("🧹 Reset Cache Koneksi", use_container_width=True, type="secondary"):
        get_gspread_client.clear()
        get_worksheet.clear()
        get_calendar_service.clear()
        st.session_state["sheet_loaded"] = False
        st.session_state["todo_cache_loaded"] = False
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB LAYOUT
# ══════════════════════════════════════════════════════════════════════════════

tab_todo, tab_catat, tab_riwayat, tab_chat = st.tabs(
    ["🗓️ Todo Task Agent", "➕ Catat Transaksi", "📊 Riwayat & Analitik", "💬 Chat AI Keuangan"]
)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 0 — TODO TASK AGENT
# ══════════════════════════════════════════════════════════════════════════════
with tab_todo:

    cal_svc, cal_err = get_calendar_service()
    cal_ok = cal_svc is not None

    st.markdown(f"""
    <div class='card'>
      <div class='card-title'>🗓️ SAMS Todo Task Agent
        <span style='margin-left:auto;font-size:.72rem;
              background:{"rgba(74,140,92,.18)" if cal_ok else "rgba(224,85,85,.14)"};
              color:{"#7ab892" if cal_ok else "#e08888"};
              border:1px solid {"rgba(74,140,92,.35)" if cal_ok else "rgba(224,85,85,.35)"};
              padding:3px 11px;border-radius:20px;'>
          {"● Google Calendar Terhubung" if cal_ok else "● Calendar Tidak Terhubung"}
        </span>
      </div>
      <p style='color:#7ab892;font-size:.82rem;margin:0'>
        Ceritakan kegiatan Anda — SAMS akan mendeteksi judul, tanggal, dan jam secara otomatis lalu menyimpannya ke Google Calendar.
      </p>
    </div>
    """, unsafe_allow_html=True)

    if not cal_ok:
        st.warning(f"⚠️ Google Calendar belum terhubung: {cal_err}.")

    if not st.session_state["todo_cache_loaded"]:
        with st.spinner("📅 Memuat agenda dari Google Calendar…"):
            st.session_state["todo_events_cache"] = load_upcoming_events(20)
        st.session_state["todo_cache_loaded"] = True

    events_cache = st.session_state["todo_events_cache"]
    if events_cache:
        st.markdown("<div class='card-title' style='font-size:.9rem;margin-bottom:.5rem'>📋 Agenda Mendatang</div>",
                    unsafe_allow_html=True)

        from collections import defaultdict
        grouped = defaultdict(list)
        for ev in events_cache:
            try:
                dt = datetime.datetime.fromisoformat(ev["start"].replace("Z", ""))
                day_key = dt.strftime("%A, %d %B %Y")
            except Exception:
                day_key = ev["start"][:10] if ev["start"] else "Tanggal tidak diketahui"
            grouped[day_key].append(ev)

        today_label = datetime.date.today().strftime("%A, %d %B %Y")
        tmr_label   = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%A, %d %B %Y")

        for day_key, day_evs in list(grouped.items())[:7]:
            badge = ""
            if day_key == today_label:
                badge = "<span style='background:rgba(200,168,75,.2);color:#c8a84b;border:1px solid rgba(200,168,75,.4);border-radius:8px;padding:1px 8px;font-size:.68rem;margin-left:8px;'>Hari Ini</span>"
            elif day_key == tmr_label:
                badge = "<span style='background:rgba(74,140,92,.18);color:#7ab892;border:1px solid rgba(74,140,92,.35);border-radius:8px;padding:1px 8px;font-size:.68rem;margin-left:8px;'>Besok</span>"
            st.markdown(f"<div style='color:#a8d5b5;font-size:.8rem;font-weight:700;margin:.6rem 0 .3rem;letter-spacing:.5px;'>{day_key}{badge}</div>",
                        unsafe_allow_html=True)
            for ev in day_evs:
                try:
                    start_dt = datetime.datetime.fromisoformat(ev["start"].replace("Z", ""))
                    end_dt   = datetime.datetime.fromisoformat(ev["end"].replace("Z", ""))
                    time_str = f"{start_dt.strftime('%H:%M')} – {end_dt.strftime('%H:%M')}"
                except Exception:
                    time_str = ""
                loc_html  = f"<span style='color:#7ab892;font-size:.7rem;'>📍 {ev['location']}</span>" if ev.get("location") else ""
                link_html = f"<a href='{ev['link']}' target='_blank' style='color:#7ab892;font-size:.7rem;text-decoration:none;'>🔗 Buka</a>" if ev.get("link") else ""
                st.markdown(f"""
                <div style='background:rgba(26,58,42,.4);border:1px solid rgba(74,140,92,.2);
                            border-left:3px solid #4a8c5c;border-radius:0 10px 10px 0;
                            padding:.55rem 1rem;margin-bottom:.3rem;'>
                  <div style='display:flex;align-items:center;gap:.5rem;'>
                    <span style='color:#a8d5b5;font-weight:700;font-size:.86rem;flex:1;'>{ev["title"]}</span>
                    <span style='color:#c8a84b;font-size:.75rem;font-weight:600;'>⏰ {time_str}</span>
                  </div>
                  <div style='display:flex;gap:.8rem;margin-top:3px;'>{loc_html}{link_html}</div>
                  {f"<div style='color:rgba(168,213,181,.6);font-size:.72rem;margin-top:3px;'>{ev['description'][:80]}{'…' if len(ev.get('description',''))>80 else ''}</div>" if ev.get("description") else ""}
                </div>
                """, unsafe_allow_html=True)
    else:
        if cal_ok:
            st.markdown("<div style='color:#7ab892;font-size:.84rem;padding:.5rem 0;'>📭 Belum ada agenda mendatang di kalender.</div>",
                        unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title' style='font-size:.9rem'>💬 Ceritakan Kegiatan Anda</div>",
                unsafe_allow_html=True)

    # Tampilkan riwayat chat (sembunyikan JSON dari tampilan)
    for msg in st.session_state["todo_messages"][-10:]:
        role = msg["role"]
        css  = "msg-user" if role == "user" else "msg-ai"
        label   = "Anda" if role == "user" else "🌿 SAMS"
        lbl_css = "color:#7ab892" if role == "user" else "color:#c8a84b"
        content_disp = msg["content"]
        if role == "assistant":
            # Hapus semua JSON dari tampilan chat
            content_disp = re.sub(r'\{[^{}]+\}', '', content_disp, flags=re.DOTALL).strip()
            # Tangani JSON multi-baris dengan brace matching
            while "{" in content_disp and "}" in content_disp:
                new = re.sub(r'\{[^{}]*\}', '', content_disp).strip()
                if new == content_disp:
                    break
                content_disp = new
        st.markdown(f"""
        <div class='{css}'>
          <div class='msg-lbl' style='{lbl_css}'>{label}</div>
          {content_disp}
        </div>
        """, unsafe_allow_html=True)

    ti1, ti2 = st.columns([5, 1])
    with ti1:
        todo_input = st.text_input(
            "todo_msg",
            placeholder='Contoh: "Besok rapat tim jam 09:00 sampai 11:00 di kantor Jakarta"',
            key="todo_chat_input",
            label_visibility="collapsed",
        )
    with ti2:
        send_todo = st.button("Kirim →", type="primary", use_container_width=True, key="btn_send_todo")

    tqp_cols = st.columns(3)
    todo_quick = [
        "📋 Tampilkan agenda minggu ini",
        "🏃 Meeting besok jam 10 pagi 1 jam",
        "📚 Belajar online Sabtu jam 14:00-16:00",
    ]
    todo_quick_clicked = None
    for i, qp in enumerate(todo_quick):
        with tqp_cols[i]:
            if st.button(qp, key=f"tqp_{i}", use_container_width=True):
                todo_quick_clicked = qp

    final_todo_input = todo_quick_clicked or (todo_input.strip() if send_todo and todo_input.strip() else None)

    if final_todo_input:
        st.session_state["todo_messages"].append({"role": "user", "content": final_todo_input})

        with st.spinner("🌿 SAMS memproses kegiatan…"):
            reply = call_ai_todo(st.session_state["todo_messages"][-8:])

        st.session_state["todo_messages"].append({"role": "assistant", "content": reply})

        # ── PERBAIKAN UTAMA: Gunakan extract_event_json() yang robust ─────
        event_data = extract_event_json(reply)
        if event_data:
            valid, err_msg, norm = validate_event_data(event_data)
            if valid:
                with st.spinner("📅 Menyimpan ke Google Calendar…"):
                    ok, cal_msg, link = add_google_calendar_event(
                        title=norm["title"],
                        date_str=norm["date"],
                        start_time=norm["start_time"],
                        end_time=norm["end_time"],
                        description=norm["description"],
                        location=norm["location"],
                    )
                if ok:
                    st.session_state["todo_cache_loaded"] = False
                    loc_info = f" · 📍{norm['location']}" if norm["location"] else ""
                    link_info = f"\n\n[🔗 Buka di Google Calendar]({link})" if link else ""
                    st.success(
                        f"✅ **{norm['title']}** berhasil dijadwalkan!\n\n"
                        f"📅 {norm['date']} · ⏰ {norm['start_time']}–{norm['end_time']}{loc_info}"
                        f"{link_info}"
                    )
                else:
                    st.warning(f"⚠️ {cal_msg}")
            else:
                st.warning(f"⚠️ Data event tidak lengkap: {err_msg}")
        # ──────────────────────────────────────────────────────────────────

        st.rerun()

    if st.session_state["todo_messages"]:
        if st.button("🗑️ Hapus Riwayat Chat Todo", type="secondary", key="clear_todo_chat"):
            st.session_state["todo_messages"] = []
            st.rerun()

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title' style='font-size:.9rem'>📝 Tambah Agenda Manual</div>",
                unsafe_allow_html=True)
    st.markdown("<p style='color:#7ab892;font-size:.8rem;margin-bottom:.7rem'>Isi form berikut untuk menambahkan agenda langsung tanpa AI.</p>",
                unsafe_allow_html=True)

    with st.form("form_todo_manual", clear_on_submit=True):
        fm1, fm2 = st.columns([3, 1])
        with fm1:
            fm_title = st.text_input("Judul Kegiatan *", placeholder="Contoh: Rapat Tim Marketing")
        with fm2:
            fm_date = st.date_input("Tanggal *", value=datetime.date.today())
        fm3, fm4 = st.columns(2)
        with fm3:
            fm_start = st.time_input("Jam Mulai *", value=datetime.time(9, 0))
        with fm4:
            fm_end   = st.time_input("Jam Selesai *", value=datetime.time(10, 0))
        fm5, fm6 = st.columns(2)
        with fm5:
            fm_location = st.text_input("Lokasi (opsional)", placeholder="Contoh: Kantor Jakarta, Zoom, dll.")
        with fm6:
            fm_desc = st.text_input("Deskripsi (opsional)", placeholder="Catatan tambahan…")
        fm_submitted = st.form_submit_button("📅 Simpan ke Google Calendar", type="primary", use_container_width=True)

    if fm_submitted:
        if not fm_title.strip():
            st.error("⚠️ Judul kegiatan tidak boleh kosong!")
        elif fm_start >= fm_end:
            st.error("⚠️ Jam selesai harus lebih dari jam mulai!")
        else:
            with st.spinner("📅 Menyimpan ke Google Calendar…"):
                ok, cal_msg, link = add_google_calendar_event(
                    title=fm_title.strip(),
                    date_str=str(fm_date),
                    start_time=fm_start.strftime("%H:%M"),
                    end_time=fm_end.strftime("%H:%M"),
                    description=fm_desc.strip(),
                    location=fm_location.strip(),
                )
            if ok:
                st.session_state["todo_cache_loaded"] = False
                st.success(f"✅ {cal_msg} 🎉" + (f" [Buka di Calendar]({link})" if link else ""))
                st.rerun()
            else:
                st.error(f"❌ {cal_msg}")

    if events_cache:
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        with st.expander("🗑️ Hapus Event dari Calendar", expanded=False):
            st.markdown("<p style='color:#e08888;font-size:.82rem;'>⚠️ Hapus event dari Google Calendar secara permanen.</p>",
                        unsafe_allow_html=True)
            ev_options = {f"{ev['title']} — {ev['start'][:16].replace('T', ' ')}": ev["id"]
                          for ev in events_cache if ev.get("id")}
            if ev_options:
                sel_ev = st.selectbox("Pilih event:", list(ev_options.keys()), key="del_ev_select")
                if st.button("🗑️ Hapus Event Ini", type="secondary", key="del_ev_btn"):
                    ev_id = ev_options[sel_ev]
                    ok, msg = delete_calendar_event(ev_id)
                    if ok:
                        st.session_state["todo_cache_loaded"] = False
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CATAT TRANSAKSI
# ══════════════════════════════════════════════════════════════════════════════
with tab_catat:
    entries = st.session_state["finance_entries"]
    df_all = pd.DataFrame(entries) if entries else pd.DataFrame(columns=["date","description","type","amount","ts"])

    if not df_all.empty:
        df_all["amount"] = pd.to_numeric(df_all["amount"], errors="coerce").fillna(0)
        df_all["date_dt"] = pd.to_datetime(df_all["date"], errors="coerce")
        today = pd.Timestamp.now().normalize()
        week_start  = today - pd.Timedelta(days=today.dayofweek)
        month_start = today.replace(day=1)

        def psum(df_, since, ftype):
            return df_.loc[(df_["date_dt"] >= since) & (df_["type"] == ftype), "amount"].sum()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📅 Keluar Hari Ini",   f"Rp {psum(df_all, today, 'pengeluaran'):,.0f}")
        c2.metric("📆 Keluar Minggu Ini", f"Rp {psum(df_all, week_start, 'pengeluaran'):,.0f}")
        c3.metric("🗓️ Keluar Bulan Ini",  f"Rp {psum(df_all, month_start, 'pengeluaran'):,.0f}")
        total_in  = df_all[df_all["type"] == "pemasukan"]["amount"].sum()
        total_out = df_all[df_all["type"] == "pengeluaran"]["amount"].sum()
        balance = total_in - total_out
        c4.metric("💵 Saldo Bersih", f"Rp {balance:,.0f}",
                  delta=f"{'Surplus' if balance >= 0 else 'Defisit'}",
                  delta_color="normal" if balance >= 0 else "inverse")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    st.markdown("<div class='card-title'>➕ Tambah Transaksi Baru</div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#7ab892;font-size:.82rem;margin-bottom:.8rem'>"
        "Data langsung tersimpan ke Google Sheets dan tersedia di semua sesi.</p>",
        unsafe_allow_html=True
    )

    with st.form("form_transaksi", clear_on_submit=True):
        fc1, fc2 = st.columns([3, 1])
        with fc1:
            f_desc = st.text_input("Keterangan *", placeholder="Contoh: Makan siang, Gaji bulanan, Belanja grocery…")
        with fc2:
            f_type = st.selectbox("Jenis *", ["pengeluaran", "pemasukan"])
        fc3, fc4 = st.columns([2, 1])
        with fc3:
            f_amount = st.number_input("Jumlah (Rp) *", min_value=0, step=1_000, value=0)
        with fc4:
            f_date = st.date_input("Tanggal *", value=datetime.date.today())
        submitted = st.form_submit_button("💾 Simpan ke Google Sheets", type="primary", use_container_width=True)

    if submitted:
        if not f_desc.strip():
            st.error("⚠️ Keterangan tidak boleh kosong!")
        elif f_amount <= 0:
            st.error("⚠️ Jumlah harus lebih dari 0!")
        else:
            entry = {
                "date":        str(f_date),
                "description": f_desc.strip(),
                "type":        f_type,
                "amount":      float(f_amount),
                "ts":          datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
            with st.spinner("☁️ Menyimpan ke Google Sheets…"):
                ok, msg = append_finance_to_sheet(entry)
            if ok:
                st.session_state["finance_entries"].append(entry)
                st.success(f"✅ **{f_desc}** — Rp {f_amount:,.0f} ({f_type}) ✔ {msg}")
            else:
                st.session_state["finance_entries"].append(entry)
                st.warning(f"⚠️ Tersimpan lokal (Google Sheets gagal: {msg}). Data belum permanen.")
            st.rerun()

    if entries:
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title' style='font-size:.9rem'>🕒 5 Transaksi Terbaru</div>",
                    unsafe_allow_html=True)
        for e in reversed(entries[-5:]):
            icon = "🔴" if e["type"] == "pengeluaran" else "🟢"
            st.markdown(f"""
            <div style='background:rgba(26,58,42,.4);border:1px solid rgba(74,140,92,.18);
                        border-radius:10px;padding:.6rem 1rem;margin-bottom:.35rem;
                        display:flex;align-items:center;gap:.8rem;'>
              <span style='font-size:1.1rem'>{icon}</span>
              <div style='flex:1'>
                <div style='color:#a8d5b5;font-weight:700;font-size:.86rem'>{e.get("description","")}</div>
                <div style='color:#7ab892;font-size:.74rem'>📅 {e.get("date","")} · ☁️ {e.get("ts","")}</div>
              </div>
              <div style='text-align:right'>
                <div style='color:{"#e08888" if e["type"]=="pengeluaran" else "#7ab892"};font-weight:700;font-size:.9rem'>
                  {"−" if e["type"]=="pengeluaran" else "+"} Rp {e.get("amount",0):,.0f}
                </div>
                <div style='font-size:.7rem;color:#7ab892'>{e.get("type","")}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RIWAYAT & ANALITIK
# ══════════════════════════════════════════════════════════════════════════════
with tab_riwayat:
    entries = st.session_state["finance_entries"]

    if not entries:
        st.info("📭 Belum ada data transaksi. Catat transaksi pertama Anda di tab 'Catat Transaksi'.")
    else:
        df = pd.DataFrame(entries)
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        df["date_dt"] = pd.to_datetime(df["date"], errors="coerce")

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filter_type = st.selectbox("Filter Jenis", ["Semua", "pengeluaran", "pemasukan"], key="filter_type")
        with col_f2:
            filter_keyword = st.text_input("Cari Keterangan", placeholder="ketik kata kunci…", key="filter_kw")
        with col_f3:
            max_rows = st.selectbox("Tampilkan", [20, 50, 100, "Semua"], key="max_rows")

        df_show = df.copy()
        if filter_type != "Semua":
            df_show = df_show[df_show["type"] == filter_type]
        if filter_keyword.strip():
            df_show = df_show[df_show["description"].str.contains(filter_keyword.strip(), case=False, na=False)]

        df_show = df_show.sort_values("date_dt", ascending=False)
        total_filtered = len(df_show)
        if max_rows != "Semua":
            df_show = df_show.head(int(max_rows))

        st.markdown(f"<div class='card-title' style='font-size:.9rem'>📋 Riwayat Transaksi ({total_filtered} data)</div>",
                    unsafe_allow_html=True)

        display = df_show[["date","description","type","amount","ts"]].copy()
        display["amount"] = display["amount"].apply(lambda x: f"Rp {x:,.0f}")
        display.columns = ["Tanggal","Keterangan","Jenis","Jumlah","Waktu Input"]
        st.dataframe(display.reset_index(drop=True), use_container_width=True, hide_index=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        with st.expander("🗑️ Hapus Transaksi", expanded=False):
            st.markdown("<p style='color:#e08888;font-size:.82rem'>⚠️ Hapus data dari Google Sheets secara permanen.</p>", unsafe_allow_html=True)
            del_idx = st.number_input(
                "Nomor baris data (urutan dari atas, mulai 1):",
                min_value=1, max_value=len(entries), step=1, value=1, key="del_idx"
            )
            if st.button("🗑️ Hapus Baris Ini", type="secondary", key="del_btn"):
                sheet_row = int(del_idx) + 1
                with st.spinner("🗑️ Menghapus dari Google Sheets…"):
                    ok, msg = delete_finance_row(sheet_row)
                if ok:
                    if 0 <= del_idx-1 < len(st.session_state["finance_entries"]):
                        st.session_state["finance_entries"].pop(del_idx-1)
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title' style='font-size:.9rem'>📈 Visualisasi</div>", unsafe_allow_html=True)

        try:
            import plotly.graph_objects as go
            import plotly.express as px

            df_plot = df.copy()
            df_plot["date_str"] = df_plot["date_dt"].dt.strftime("%Y-%m-%d")
            daily = df_plot.groupby(["date_str","type"])["amount"].sum().reset_index()

            fig = go.Figure()
            for ftype, color in [("pengeluaran","#e05555"),("pemasukan","#4a8c5c")]:
                sub = daily[daily["type"]==ftype]
                if not sub.empty:
                    fig.add_trace(go.Bar(x=sub["date_str"], y=sub["amount"],
                                         name=ftype.capitalize(), marker_color=color, opacity=.85))
            fig.update_layout(
                barmode="group",
                plot_bgcolor="rgba(12,28,18,.85)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#a8d5b5", family="Plus Jakarta Sans"),
                title=dict(text="Pemasukan vs Pengeluaran per Hari", font=dict(color="#a8d5b5", size=13)),
                xaxis=dict(gridcolor="rgba(74,140,92,.12)", color="#7ab892"),
                yaxis=dict(gridcolor="rgba(74,140,92,.12)", color="#7ab892",
                           tickprefix="Rp ", tickformat=",.0f"),
                legend=dict(bgcolor="rgba(26,58,42,.5)", bordercolor="rgba(74,140,92,.3)"),
                margin=dict(t=45, b=25, l=10, r=10),
            )
            st.plotly_chart(fig, use_container_width=True)

            cat = df_plot[df_plot["type"]=="pengeluaran"].groupby("description")["amount"].sum().nlargest(8)
            if not cat.empty:
                fig2 = go.Figure(go.Pie(
                    labels=cat.index, values=cat.values, hole=.5,
                    marker=dict(colors=px.colors.sequential.Greens_r[:len(cat)]),
                    textfont=dict(color="#e8f5ec"),
                ))
                fig2.update_layout(
                    title=dict(text="Distribusi Pengeluaran Terbesar", font=dict(color="#a8d5b5", size=13)),
                    paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#a8d5b5"),
                    legend=dict(bgcolor="rgba(26,58,42,.5)"),
                    margin=dict(t=45, b=10, l=10, r=10),
                )
                st.plotly_chart(fig2, use_container_width=True)
        except ImportError:
            st.info("Install plotly untuk chart: `pip install plotly`")
        except Exception as e:
            st.warning(f"Chart error: {e}")

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        csv_data = df[["date","description","type","amount","ts"]].to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download CSV",
            data=csv_data,
            file_name=f"sams_finance_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CHAT AI KEUANGAN
# ══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown("""
    <div class='card'>
      <div class='card-title'>💬 Tanya SAMS Finance Agent</div>
      <p style='color:#7ab892;font-size:.82rem;margin:0'>
        Ceritakan transaksi Anda atau minta analisis keuangan.
        SAMS akan otomatis mendeteksi dan menyimpan transaksi ke Google Sheets.
      </p>
    </div>
    """, unsafe_allow_html=True)

    if not openai_ok:
        st.warning("⚠️ OPENAI_API_KEY belum dikonfigurasi di Secrets.")
    else:
        for msg in st.session_state["chat_messages"][-10:]:
            role = msg["role"]
            css = "msg-user" if role == "user" else "msg-ai"
            label   = "Anda" if role == "user" else "🌿 SAMS"
            lbl_css = "color:#7ab892" if role == "user" else "color:#c8a84b"
            content = msg["content"]
            if role == "assistant" and "{" in content:
                content = re.sub(r'\{[^}]*\}', '', content).strip()
            st.markdown(f"""
            <div class='{css}'>
              <div class='msg-lbl' style='{lbl_css}'>{label}</div>
              {content}
            </div>
            """, unsafe_allow_html=True)

        ci1, ci2 = st.columns([5, 1])
        with ci1:
            user_input = st.text_input(
                "Pesan",
                placeholder='Contoh: "Tadi beli kopi 35rb" atau "Analisis pengeluaran bulan ini"',
                key="chat_input",
                label_visibility="collapsed",
            )
        with ci2:
            send = st.button("Kirim →", type="primary", use_container_width=True, key="btn_send")

        st.markdown("<div style='display:flex;gap:.5rem;flex-wrap:wrap;margin-top:.4rem'>", unsafe_allow_html=True)
        qp_col = st.columns(4)
        quick_prompts = [
            "📊 Analisis keuangan bulan ini",
            "💡 Tips hemat berdasarkan data saya",
            "📉 Pengeluaran terbesar saya apa?",
            "📈 Bagaimana tren keuangan saya?",
        ]
        quick_clicked = None
        for i, qp in enumerate(quick_prompts):
            with qp_col[i]:
                if st.button(qp, key=f"qp_{i}", use_container_width=True):
                    quick_clicked = qp

        final_input = quick_clicked or (user_input.strip() if send and user_input.strip() else None)

        if final_input:
            entries = st.session_state["finance_entries"]
            ctx_lines = []
            if entries:
                df_ctx = pd.DataFrame(entries)
                df_ctx["amount"] = pd.to_numeric(df_ctx["amount"], errors="coerce").fillna(0)
                total_out = df_ctx[df_ctx["type"]=="pengeluaran"]["amount"].sum()
                total_in  = df_ctx[df_ctx["type"]=="pemasukan"]["amount"].sum()
                today_str = str(datetime.date.today())
                today_out = df_ctx[(df_ctx["type"]=="pengeluaran") & (df_ctx["date"]==today_str)]["amount"].sum()
                top_cats  = df_ctx[df_ctx["type"]=="pengeluaran"].groupby("description")["amount"].sum().nlargest(3).to_dict()
                recent_5  = entries[-5:]
                ctx_lines = [
                    "[DATA KEUANGAN USER]",
                    f"Total pengeluaran: Rp {total_out:,.0f}",
                    f"Total pemasukan: Rp {total_in:,.0f}",
                    f"Pengeluaran hari ini: Rp {today_out:,.0f}",
                    f"Top pengeluaran: {top_cats}",
                    f"5 transaksi terakhir: {recent_5}",
                ]

            full_msg = final_input
            if ctx_lines:
                full_msg += "\n\n" + "\n".join(ctx_lines)

            st.session_state["chat_messages"].append({"role": "user", "content": final_input})

            with st.spinner("🌿 SAMS sedang menganalisis…"):
                msgs_for_ai = st.session_state["chat_messages"][:-1] + [{"role":"user","content":full_msg}]
                reply = call_ai(msgs_for_ai[-8:])

            st.session_state["chat_messages"].append({"role": "assistant", "content": reply})

            if '"action":"add_entry"' in reply or '"action": "add_entry"' in reply:
                m = re.search(r'\{[^}]*"action"\s*:\s*"add_entry"[^}]*\}', reply, re.DOTALL)
                if m:
                    try:
                        data = json.loads(m.group())
                        new_entry = {
                            "date":        str(datetime.date.today()),
                            "description": data["description"],
                            "type":        data["type"],
                            "amount":      float(data["amount"]),
                            "ts":          datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                        }
                        with st.spinner("☁️ Menyimpan transaksi ke Google Sheets…"):
                            ok, save_msg = append_finance_to_sheet(new_entry)
                        if ok:
                            st.session_state["finance_entries"].append(new_entry)
                            st.success(f"✅ Transaksi **{data['description']}** (Rp {data['amount']:,.0f}) tersimpan ke Sheets!")
                        else:
                            st.session_state["finance_entries"].append(new_entry)
                            st.warning(f"⚠️ Tersimpan lokal. {save_msg}")
                    except Exception as parse_err:
                        st.warning(f"Gagal parse JSON transaksi: {parse_err}")

            st.rerun()

        if st.session_state["chat_messages"]:
            if st.button("🗑️ Hapus Riwayat Chat", type="secondary", key="clear_chat"):
                st.session_state["chat_messages"] = []
                st.rerun()


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;margin-top:2rem;padding:1.2rem 0;
            border-top:1px solid rgba(74,140,92,.18);'>
  <div style='font-family:"Playfair Display",serif;
              background:linear-gradient(135deg,#a8d5b5,#7ab892);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
    🌿 SAMS Agent
  </div>
  <div style='color:rgba(122,184,146,.45);font-size:.7rem;letter-spacing:1.5px;text-transform:uppercase;margin-top:.2rem'>
    Financial Agent · Todo Task Agent · Built with Sustainable Spirit
  </div>
</div>
""", unsafe_allow_html=True)