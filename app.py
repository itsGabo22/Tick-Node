"""
Tick Node — Analog Clock Application.

Entry point for the Streamlit frontend.
Configures session state, renders the Plotly clock face,
and provides controls for timezone travel, brand selection,
and the Time Machine.

Run with:
    streamlit run app.py
"""

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from src.use_cases.clock_manager import ClockManager
from src.use_cases.history import HistoryStack
from src.use_cases.strategies import ForwardStrategy, BackwardStrategy
from src.infrastructure.static_data import WATCH_BRANDS, TIME_ZONES, ALL_TIME_ZONES
from src.infrastructure.time_service import TimeCalculator
from src.ui.watch_faces import WatchFaceFactory


# ═══════════════════════════════════════════════════════════════════════════
# Page Configuration
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Tick Node — Reloj Analógico",
    page_icon="🕐",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ═══════════════════════════════════════════════════════════════════════════
# Session State Initialization (runs only once per session)
# ═══════════════════════════════════════════════════════════════════════════

if "clock" not in st.session_state:
    st.session_state.clock = ClockManager()

if "history" not in st.session_state:
    st.session_state.history = HistoryStack()

if "brand_key" not in st.session_state:
    st.session_state.brand_key = "rolex"

if "current_zone" not in st.session_state:
    calc = TimeCalculator()
    st.session_state.current_zone = calc.get_local_zone_name()

if "time_machine_on" not in st.session_state:
    st.session_state.time_machine_on = False

if "auto_tick" not in st.session_state:
    st.session_state.auto_tick = False


# ═══════════════════════════════════════════════════════════════════════════
# Aliases for readability
# ═══════════════════════════════════════════════════════════════════════════

clock: ClockManager = st.session_state.clock
history: HistoryStack = st.session_state.history
calc = TimeCalculator()


# ═══════════════════════════════════════════════════════════════════════════
# Auto-refresh tick (if enabled)
# ═══════════════════════════════════════════════════════════════════════════

if st.session_state.auto_tick:
    st_autorefresh(interval=1000, limit=None, key="auto_tick_refresh")
    clock.tick()


# ═══════════════════════════════════════════════════════════════════════════
# Sidebar — Controls
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 🎛️ Panel de Control")
    st.markdown("---")

    # ── Brand Selector ──────────────────────────────────────────────── #
    st.markdown("### 🏷️ Marca de Lujo")
    brand_options = {v["display_name"]: k for k, v in WATCH_BRANDS.items()}
    selected_display = st.selectbox(
        "Elegir marca",
        options=list(brand_options.keys()),
        index=list(brand_options.values()).index(st.session_state.brand_key),
        label_visibility="collapsed",
    )
    st.session_state.brand_key = brand_options[selected_display]

    st.markdown("---")

    # ── Timezone Selector ───────────────────────────────────────────── #
    st.markdown("### 🌍 Zona Horaria")

    # Build a flat list with continent headers
    tz_flat_options = []
    for continent, zones in TIME_ZONES.items():
        for tz in zones:
            tz_flat_options.append(tz)

    current_idx = (
        tz_flat_options.index(st.session_state.current_zone)
        if st.session_state.current_zone in tz_flat_options
        else 0
    )

    selected_zone = st.selectbox(
        "Elegir zona",
        options=tz_flat_options,
        index=current_idx,
        label_visibility="collapsed",
    )

    if selected_zone != st.session_state.current_zone:
        diff = calc.hour_difference(
            destination=selected_zone,
            origin=st.session_state.current_zone,
        )
        # Push to history before shifting
        history.push({
            "from": st.session_state.current_zone,
            "to": selected_zone,
            "diff": diff,
        })
        clock.shift_time_zone(diff)
        st.session_state.current_zone = selected_zone
        st.rerun()

    # ── Undo Travel Button ──────────────────────────────────────────── #
    st.markdown("---")
    st.markdown("### ✈️ Historial de Viajes")

    if not history.is_empty():
        last = history.peek()
        st.caption(
            f"Último viaje: {last['from']} → {last['to']} "
            f"({'+' if last['diff'] >= 0 else ''}{last['diff']}h)"
        )
    else:
        st.caption("Sin viajes registrados.")

    undo_disabled = history.is_empty()
    if st.button(
        "⏪ Deshacer Viaje",
        disabled=undo_disabled,
        use_container_width=True,
    ):
        record = history.pop()
        clock.shift_time_zone(-record["diff"])
        st.session_state.current_zone = record["from"]
        st.rerun()

    st.markdown(f"📚 Pila: **{len(history)}** viaje(s)")

    st.markdown("---")

    # ── Time Machine Toggle ─────────────────────────────────────────── #
    st.markdown("### ⏳ Máquina del Tiempo")

    time_machine = st.toggle(
        "Invertir tiempo",
        value=st.session_state.time_machine_on,
    )

    if time_machine != st.session_state.time_machine_on:
        st.session_state.time_machine_on = time_machine
        clock.toggle_time_machine()
        st.rerun()

    direction = clock.get_state()["direction"]
    dir_icon = "⏩ Adelante" if direction == "Forward" else "⏪ Atrás"
    st.caption(f"Dirección: **{dir_icon}**")

    st.markdown("---")

    # ── Tick Controls ───────────────────────────────────────────────── #
    st.markdown("### ⚡ Motor del Reloj")

    auto = st.toggle(
        "Tick automático (1s)",
        value=st.session_state.auto_tick,
    )
    if auto != st.session_state.auto_tick:
        st.session_state.auto_tick = auto
        st.rerun()

    col_tick1, col_tick2 = st.columns(2)
    with col_tick1:
        if st.button("⏱️ Tick ×1", use_container_width=True):
            clock.tick()
            st.rerun()
    with col_tick2:
        if st.button("⏱️ Tick ×60", use_container_width=True):
            for _ in range(60):
                clock.tick()
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# Main Area — Clock Face
# ═══════════════════════════════════════════════════════════════════════════

# Header
st.markdown(
    "<h1 style='text-align:center; margin-bottom:0;'>"
    "🕐 Tick Node"
    "</h1>"
    "<p style='text-align:center; color:gray; margin-top:0;'>"
    "Reloj Analógico con Listas Circulares Dobles"
    "</p>",
    unsafe_allow_html=True,
)

# Get current state and brand config
state = clock.get_state()
brand_cfg = WATCH_BRANDS[st.session_state.brand_key]

# Build the Plotly figure via Factory
fig = WatchFaceFactory.create_watch_face(state=state, brand_config=brand_cfg)

# Render
st.plotly_chart(fig, use_container_width=False, config={"displayModeBar": False})

# Digital readout below the clock
h, m, s = state["hours"], state["minutes"], state["seconds"]
st.markdown(
    f"<div style='text-align:center; font-size:2rem; font-family:monospace; "
    f"letter-spacing:4px; color:{brand_cfg['accent']};'>"
    f"{h:02d} : {m:02d} : {s:02d}"
    f"</div>",
    unsafe_allow_html=True,
)

# Zone info
st.markdown(
    f"<p style='text-align:center; color:gray; font-size:0.9rem;'>"
    f"🌐 {st.session_state.current_zone}"
    f"</p>",
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════
# Footer
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray; font-size:0.75rem;'>"
    "Tick Node · Clean Architecture · Listas Circulares Dobles · "
    "Patrones GoF (Strategy, Factory, Observer) · Pila LIFO"
    "</p>",
    unsafe_allow_html=True,
)
