"""
SAMS Financial Agent — Google Sheets Integration
=================================================
Persyaratan:
  pip install streamlit openai gspread google-auth pandas plotly

Konfigurasi Streamlit Secrets (.streamlit/secrets.toml):
  OPENAI_API_KEY = "sk-..."
  GOOGLE_SHEET_ID = "1AbCdEfGhIjKlMnOpQrStUvWxYz..."   ← ID spreadsheet Anda

  [gcp_service_account]
  type                        = "service_account"
  project_id                  = "your-project"
  private_key_id              = "abc123"
  private_key                 = "-----BEGIN RSA PRIVATE KEY-----\\nMIIE...\\n-----END RSA PRIVATE KEY-----\\n"
  client_email                = "sams-agent@your-project.iam.gserviceaccount.com"
  client_id                   = "123456789"
  token_uri                   = "https://oauth2.googleapis.com/token"
  client_x509_cert_url        = "https://www.googleapis.com/robot/v1/metadata/x509/sams-agent%40your-project.iam.gserviceaccount.com"

Langkah Setup:
  1. Buat Google Service Account di console.cloud.google.com
  2. Aktifkan Google Sheets API + Google Drive API
  3. Download JSON key → isi nilai-nilainya ke secrets.toml
  4. Share spreadsheet Anda ke email service account (client_email) dengan role Editor
  5. Salin Spreadsheet ID dari URL: docs.google.com/spreadsheets/d/[INI SHEET ID]/edit
"""

import streamlit as st
import os, json, re, datetime
import pandas as pd
from typing import Optional

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SAMS Financial Agent",
    page_icon="💰",
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

/* ─ Cards ─ */
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

/* ─ Inputs ─ */
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
[data-testid="stDateInput"] input {
    background: transparent !important;
    color: #e8f5ec !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stDateInput"] label,
[data-testid="stSelectbox"] label { color: var(--sage) !important; font-weight: 600 !important; font-size: 0.8rem !important; }

/* ─ Buttons ─ */
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

/* ─ Metrics ─ */
[data-testid="metric-container"] {
    background: rgba(26,58,42,0.5) !important;
    border: 1px solid rgba(74,140,92,0.2) !important;
    border-radius: var(--radius) !important;
    padding: 1rem !important;
}
[data-testid="metric-container"] label { color: var(--sage) !important; font-size: .75rem !important; }
[data-testid="stMetricValue"] { color: var(--mint) !important; font-weight: 700 !important; }

/* ─ Chat bubbles ─ */
.msg-user { background:rgba(45,90,61,.4);border:1px solid rgba(74,140,92,.3);
    border-radius:10px 0 10px 10px;padding:.7rem 1rem;margin:.4rem 0 .4rem 3rem;font-size:.87rem; }
.msg-ai { background:rgba(12,32,20,.65);border:1px solid rgba(122,184,146,.2);
    border-radius:0 10px 10px 10px;padding:.7rem 1rem;margin:.4rem 3rem .4rem 0;font-size:.87rem; }
.msg-lbl { font-size:.68rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:.25rem; }

.divider { border:none;border-top:1px solid rgba(74,140,92,0.18);margin:.8rem 0; }

/* status pill */
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
    """Read from Streamlit secrets first, then env."""
    try:
        val = st.secrets[key]
        return str(val) if val is not None else default
    except Exception:
        return os.getenv(key, default)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — GOOGLE SHEETS CLIENT (gspread, lebih simpel dari googleapiclient)
# ══════════════════════════════════════════════════════════════════════════════

SHEET_TAB = "Finance"
SHEET_HEADERS = ["Tanggal", "Keterangan", "Jenis", "Jumlah (Rp)", "Timestamp Input"]

@st.cache_resource(show_spinner=False)
def get_gspread_client():
    """
    Buat gspread client dari Service Account di Streamlit Secrets.
    Di-cache agar tidak reconnect setiap rerun.
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        sa = st.secrets["gcp_service_account"]
        info = {
            "type": "service_account",
            "project_id": str(sa["project_id"]),
            "private_key_id": str(sa["private_key_id"]),
            "private_key": str(sa["private_key"]).replace("\\n", "\n"),
            "client_email": str(sa["client_email"]),
            "client_id": str(sa["client_id"]),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": str(sa.get("token_uri", "https://oauth2.googleapis.com/token")),
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": str(sa.get("client_x509_cert_url", "")),
        }
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        return None


@st.cache_resource(show_spinner=False)
def get_worksheet():
    """
    Buka worksheet 'Finance'. Jika belum ada, buat + tulis header.
    Di-cache supaya tidak re-open setiap rerun.
    """
    gc = get_gspread_client()
    sheet_id = get_secret("GOOGLE_SHEET_ID")
    if not gc or not sheet_id:
        return None, "❌ Konfigurasi belum lengkap (lihat sidebar)."

    try:
        spreadsheet = gc.open_by_key(sheet_id)
    except Exception as e:
        return None, f"❌ Tidak bisa membuka spreadsheet: {e}"

    # Cek/buat tab Finance
    try:
        ws = spreadsheet.worksheet(SHEET_TAB)
    except Exception:
        ws = spreadsheet.add_worksheet(title=SHEET_TAB, rows=1000, cols=10)
        ws.append_row(SHEET_HEADERS, value_input_option="USER_ENTERED")

    # Pastikan header ada
    try:
        first_row = ws.row_values(1)
        if first_row != SHEET_HEADERS:
            ws.insert_row(SHEET_HEADERS, index=1)
    except Exception:
        pass

    return ws, "✅ Terhubung ke Google Sheets"


def sheet_status() -> tuple[bool, str]:
    ws, msg = get_worksheet()
    return (ws is not None), msg


# ── READ ALL ──────────────────────────────────────────────────────────────────

def load_finance_from_sheet() -> list[dict]:
    """
    Muat semua baris dari sheet Finance.
    Return list of dicts.
    """
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


# ── APPEND ONE ROW ────────────────────────────────────────────────────────────

def append_finance_to_sheet(entry: dict) -> tuple[bool, str]:
    """
    Tambahkan satu baris ke sheet Finance.
    Return (success, message).
    """
    ws, msg = get_worksheet()
    if ws is None:
        return False, msg
    try:
        ts_now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        row = [
            entry["date"],
            entry["description"],
            entry["type"],
            entry["amount"],
            ts_now,
        ]
        ws.append_row(row, value_input_option="USER_ENTERED")
        return True, "✅ Tersimpan ke Google Sheets"
    except Exception as e:
        return False, f"❌ Gagal menyimpan: {e}"


# ── DELETE ROW BY INDEX ───────────────────────────────────────────────────────

def delete_finance_row(sheet_row_index: int) -> tuple[bool, str]:
    """
    Hapus baris berdasarkan index baris di sheet (1-based, termasuk header).
    sheet_row_index = data_index + 2  (karena header di baris 1, data mulai baris 2)
    """
    ws, msg = get_worksheet()
    if ws is None:
        return False, msg
    try:
        ws.delete_rows(sheet_row_index)
        return True, "✅ Data dihapus dari Google Sheets"
    except Exception as e:
        return False, f"❌ Gagal menghapus: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — AI (OpenAI)
# ══════════════════════════════════════════════════════════════════════════════

MAX_BUDGET_USD = 0.05

def get_openai_client():
    from openai import OpenAI
    return OpenAI(api_key=get_secret("OPENAI_API_KEY"))

def tokens_to_usd(tokens: int) -> float:
    return tokens * 0.0000005   # gpt-4o-mini ~$0.50/1M input tokens

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
        return "⚠️ Budget sesi habis. Refresh halaman untuk memulai sesi baru."

    used_usd = tokens_to_usd(st.session_state.get("total_tokens", 0))
    remaining = MAX_BUDGET_USD - used_usd
    if remaining <= 0:
        st.session_state["budget_exceeded"] = True
        return "⚠️ Budget sesi habis."

    max_tokens = min(600, int(remaining / 0.0000006))
    if max_tokens < 40:
        st.session_state["budget_exceeded"] = True
        return "⚠️ Budget hampir habis. Refresh untuk sesi baru."

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
    except Exception as e:
        return f"❌ Error AI: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — SESSION STATE INIT
# ══════════════════════════════════════════════════════════════════════════════

def init_state():
    defaults = {
        "total_tokens":       0,
        "budget_exceeded":    False,
        "finance_entries":    [],       # list[dict] — mirror dari sheet
        "chat_messages":      [],       # list[dict] role/content
        "sheet_loaded":       False,    # sudah load dari sheet?
        "show_analytics":     False,
        "delete_confirm_idx": None,     # index baris yg mau dihapus
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — LOAD DATA (sekali per session)
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

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:1.5rem 0 1rem;'>
  <div style='font-family:"Playfair Display",serif;font-size:2.8rem;font-weight:700;
       background:linear-gradient(135deg,#a8d5b5,#7ab892,#c8a84b);
       -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
    💰 SAMS Financial Agent
  </div>
  <div style='color:#7ab892;font-size:.8rem;letter-spacing:3px;text-transform:uppercase;margin-top:.3rem;'>
    Google Sheets · Real-time Sync · Persistent Data
  </div>
</div>
""", unsafe_allow_html=True)

# ── STATUS STRIP ──────────────────────────────────────────────────────────────
gs_ok, gs_msg = sheet_status()
openai_ok = bool(get_secret("OPENAI_API_KEY"))

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

st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)

# ── KONFIGURASI SIDEBAR ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Konfigurasi")
    st.markdown("---")
    st.markdown("""
**Langkah Setup Google Sheets:**

1. Buka [Google Cloud Console](https://console.cloud.google.com)
2. Buat/pilih project → **APIs & Services**
3. Aktifkan **Google Sheets API** dan **Google Drive API**
4. Buat **Service Account** → buat JSON key
5. Share spreadsheet Anda ke `client_email` service account (role: **Editor**)
6. Isi `.streamlit/secrets.toml`:
""")
    st.code("""
OPENAI_API_KEY = "sk-..."
GOOGLE_SHEET_ID = "1AbCd..."

[gcp_service_account]
type = "service_account"
project_id = "my-project"
private_key_id = "abc123"
private_key = "-----BEGIN RSA PRIVATE KEY-----\\nMIIE...\\n-----END RSA PRIVATE KEY-----\\n"
client_email = "sams@my-project.iam.gserviceaccount.com"
client_id = "123456789"
token_uri = "https://oauth2.googleapis.com/token"
""", language="toml")
    st.markdown("---")
    st.markdown("**Sheet ID** ada di URL Spreadsheet:")
    st.markdown("`docs.google.com/spreadsheets/d/**[SHEET_ID]**/edit`")

    st.markdown("---")
    if st.button("🔄 Reload Data dari Sheets", use_container_width=True):
        st.session_state["sheet_loaded"] = False
        st.session_state["finance_entries"] = []
        st.rerun()

    if st.button("🧹 Reset Cache Koneksi", use_container_width=True, type="secondary"):
        get_gspread_client.clear()
        get_worksheet.clear()
        st.session_state["sheet_loaded"] = False
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB LAYOUT
# ══════════════════════════════════════════════════════════════════════════════

tab_catat, tab_riwayat, tab_chat = st.tabs(
    ["➕ Catat Transaksi", "📊 Riwayat & Analitik", "💬 Chat AI Keuangan"]
)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CATAT TRANSAKSI
# ══════════════════════════════════════════════════════════════════════════════
with tab_catat:
    entries = st.session_state["finance_entries"]
    df_all = pd.DataFrame(entries) if entries else pd.DataFrame(columns=["date","description","type","amount","ts"])

    # ── METRICS ──────────────────────────────────────────────────────────────
    if not df_all.empty:
        df_all["amount"] = pd.to_numeric(df_all["amount"], errors="coerce").fillna(0)
        df_all["date_dt"] = pd.to_datetime(df_all["date"], errors="coerce")
        today = pd.Timestamp.now().normalize()
        week_start  = today - pd.Timedelta(days=today.dayofweek)
        month_start = today.replace(day=1)

        def psum(df_, since, ftype):
            return df_.loc[(df_["date_dt"] >= since) & (df_["type"]==ftype), "amount"].sum()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📅 Keluar Hari Ini",   f"Rp {psum(df_all, today, 'pengeluaran'):,.0f}")
        c2.metric("📆 Keluar Minggu Ini", f"Rp {psum(df_all, week_start, 'pengeluaran'):,.0f}")
        c3.metric("🗓️ Keluar Bulan Ini",  f"Rp {psum(df_all, month_start, 'pengeluaran'):,.0f}")
        total_in  = df_all[df_all["type"]=="pemasukan"]["amount"].sum()
        total_out = df_all[df_all["type"]=="pengeluaran"]["amount"].sum()
        balance = total_in - total_out
        c4.metric("💵 Saldo Bersih", f"Rp {balance:,.0f}",
                  delta=f"{'Surplus' if balance>=0 else 'Defisit'}",
                  delta_color="normal" if balance>=0 else "inverse")

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── FORM CATAT TRANSAKSI ──────────────────────────────────────────────────
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
            # ── SIMPAN KE SHEET ────────────────────────────────────────────
            with st.spinner("☁️ Menyimpan ke Google Sheets…"):
                ok, msg = append_finance_to_sheet(entry)

            if ok:
                st.session_state["finance_entries"].append(entry)
                st.success(f"✅ **{f_desc}** — Rp {f_amount:,.0f} ({f_type}) {msg}")
            else:
                # Tetap simpan lokal supaya tidak hilang
                st.session_state["finance_entries"].append(entry)
                st.warning(f"⚠️ Tersimpan lokal (Google Sheets gagal: {msg}). Data belum permanen.")

            st.rerun()

    # ── TRANSAKSI TERBARU (preview 5) ────────────────────────────────────────
    if entries:
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title' style='font-size:.9rem'>🕒 5 Transaksi Terbaru</div>",
                    unsafe_allow_html=True)
        for e in reversed(entries[-5:]):
            icon = "🔴" if e["type"]=="pengeluaran" else "🟢"
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

        # ── FILTER ────────────────────────────────────────────────────────────
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

        # ── TABEL ─────────────────────────────────────────────────────────────
        st.markdown(f"<div class='card-title' style='font-size:.9rem'>📋 Riwayat Transaksi ({total_filtered} data)</div>",
                    unsafe_allow_html=True)

        display = df_show[["date","description","type","amount","ts"]].copy()
        display["amount"] = display["amount"].apply(lambda x: f"Rp {x:,.0f}")
        display.columns = ["Tanggal","Keterangan","Jenis","Jumlah","Waktu Input"]
        st.dataframe(display.reset_index(drop=True), use_container_width=True, hide_index=True)

        # ── HAPUS TRANSAKSI ───────────────────────────────────────────────────
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        with st.expander("🗑️ Hapus Transaksi", expanded=False):
            st.markdown("<p style='color:#e08888;font-size:.82rem'>⚠️ Hapus data dari Google Sheets secara permanen.</p>", unsafe_allow_html=True)
            del_idx = st.number_input(
                "Nomor baris data (urutan dari atas, mulai 1):",
                min_value=1, max_value=len(entries), step=1, value=1, key="del_idx"
            )
            if st.button("🗑️ Hapus Baris Ini", type="secondary", key="del_btn"):
                # sheet row = del_idx + 1 (header di baris 1, data mulai baris 2)
                sheet_row = int(del_idx) + 1
                with st.spinner("🗑️ Menghapus dari Google Sheets…"):
                    ok, msg = delete_finance_row(sheet_row)
                if ok:
                    # Hapus dari session state juga
                    if 0 <= del_idx-1 < len(st.session_state["finance_entries"]):
                        st.session_state["finance_entries"].pop(del_idx-1)
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        # ── CHART ─────────────────────────────────────────────────────────────
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title' style='font-size:.9rem'>📈 Visualisasi</div>", unsafe_allow_html=True)

        try:
            import plotly.graph_objects as go
            import plotly.express as px

            df_plot = df.copy()
            df_plot["date_str"] = df_plot["date_dt"].dt.strftime("%Y-%m-%d")
            daily = df_plot.groupby(["date_str","type"])["amount"].sum().reset_index()

            # Bar chart: pemasukan vs pengeluaran per hari
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

            # Pie: distribusi pengeluaran
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

        # ── EXPORT CSV ────────────────────────────────────────────────────────
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
        # ── CHAT HISTORY ─────────────────────────────────────────────────────
        for msg in st.session_state["chat_messages"][-10:]:
            role = msg["role"]
            css = "msg-user" if role=="user" else "msg-ai"
            label = "Anda" if role=="user" else "🌿 SAMS"
            lbl_css = "color:#7ab892" if role=="user" else "color:#c8a84b"
            # Sembunyikan JSON mentah dari tampilan
            content = msg["content"]
            if role == "assistant" and "{" in content:
                content = re.sub(r'\{[^}]*\}', '', content).strip()
            st.markdown(f"""
            <div class='{css}'>
              <div class='msg-lbl' style='{lbl_css}'>{label}</div>
              {content}
            </div>
            """, unsafe_allow_html=True)

        # ── INPUT ─────────────────────────────────────────────────────────────
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

        # ── QUICK PROMPTS ──────────────────────────────────────────────────────
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

        # ── PROSES PESAN ───────────────────────────────────────────────────────
        final_input = quick_clicked or (user_input.strip() if send and user_input.strip() else None)

        if final_input:
            # Sisipkan konteks keuangan ke pesan user
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
                    f"[DATA KEUANGAN USER]",
                    f"Total pengeluaran: Rp {total_out:,.0f}",
                    f"Total pemasukan: Rp {total_in:,.0f}",
                    f"Pengeluaran hari ini: Rp {today_out:,.0f}",
                    f"Top pengeluaran: {top_cats}",
                    f"5 transaksi terakhir: {recent_5}",
                ]

            full_msg = final_input
            if ctx_lines:
                full_msg += "\n\n" + "\n".join(ctx_lines)

            st.session_state["chat_messages"].append({"role": "user", "content": final_input})  # tampilkan tanpa konteks

            with st.spinner("🌿 SAMS sedang menganalisis…"):
                msgs_for_ai = st.session_state["chat_messages"][:-1] + [{"role":"user","content":full_msg}]
                reply = call_ai(msgs_for_ai[-8:])

            st.session_state["chat_messages"].append({"role": "assistant", "content": reply})

            # ── DETEKSI & SIMPAN TRANSAKSI DARI CHAT ─────────────────────────
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

        # ── CLEAR CHAT ────────────────────────────────────────────────────────
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
    🌿 SAMS Financial Agent
  </div>
  <div style='color:rgba(122,184,146,.45);font-size:.7rem;letter-spacing:1.5px;text-transform:uppercase;margin-top:.2rem'>
    Data Persisten · Google Sheets Sync · Built with Sustainable Spirit
  </div>
</div>
""", unsafe_allow_html=True)