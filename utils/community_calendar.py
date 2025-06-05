# Calendar functionality moved here to avoid conflicts with Python's built-in calendar module
from datetime import datetime as dt
from types import SimpleNamespace
import traceback

# Conditionally import streamlit to prevent circular imports


def get_streamlit():
    import streamlit as st
    return st


def calendar_view():
    """Nuclear-proof calendar view that cannot break the app"""
    # Get streamlit on demand to avoid circular imports
    try:
        st = get_streamlit()
    except ImportError:
        return

    # 0. Absolute minimum Streamlit check
    if not hasattr(st, '__version__'):
        return

    # 1. Safest possible session state initialization
    try:
        if not hasattr(st, 'session_state'):
            st.session_state = SimpleNamespace(calendar_date=None)
        elif not hasattr(st.session_state, 'calendar_date'):
            st.session_state.calendar_date = None
    except:
        st.session_state = SimpleNamespace(calendar_date=None)

    # 2. Get current date with ultimate fallbacks
    try:
        current_date = dt.now().date()
    except:
        try:
            current_date = dt(2023, 1, 1).date()
        except:
            current_date = None

    # 3. Safest possible sidebar access
    sidebar = None
    try:
        sidebar = st.sidebar if hasattr(st, 'sidebar') else None
    except:
        pass

    if not sidebar:
        return

    # 4. Date selection with multiple protection layers
    selected_date = current_date
    try:
        selected_date = sidebar.date_input(
            "Select Date",
            st.session_state.calendar_date or current_date
        )
        st.session_state.calendar_date = selected_date
    except:
        pass

    # 5. Database access with complete isolation
    servicemen = []
    try:
        from utils.db import users_col, schedules_col
        if 'users_col' in globals() and users_col:
            servicemen = list(users_col.find({"role": "serviceman"})) or []
    except:
        pass

    if not servicemen:
        try:
            sidebar.warning("No servicemen available")
        except:
            pass
        return

    # 6. Serviceman selection with atomic safety
    options = []
    mapping = {}
    for s in servicemen:
        try:
            name = (str(s.get("name", "")) or
                    str(s.get("username", "")) or
                    str(s.get("email", "unknown")).split("@")[0] or
                    f"Serviceman-{str(s.get('_id', 'unknown'))[:6]}")
            if name.strip():
                options.append(name)
                mapping[name] = s
        except:
            continue

    if not options:
        try:
            sidebar.warning("No valid servicemen")
        except:
            pass
        return

    try:
        selected = sidebar.selectbox("Serviceman", options)
        serviceman = mapping.get(selected)
    except:
        return

    if not serviceman:
        return

    # 7. Schedule display with ultimate protection
    schedule = {}
    try:
        if selected_date and 'schedules_col' in globals() and schedules_col:
            schedule_date = dt.combine(selected_date, dt.min.time())
            schedule = schedules_col.find_one({
                "serviceman_id": str(serviceman.get("username", "")),
                "date": schedule_date
            }) or {}
    except:
        pass

    try:
        name = (str(serviceman.get("name", "")) or
                str(serviceman.get("username", "")) or
                "Serviceman")
        sidebar.markdown(f"**{name}'s Schedule**")

        for slot in schedule.get("time_slots", []):
            try:
                start = str(slot.get("start", "?:??"))
                end = str(slot.get("end", "?:??"))
                status = "🔴 Booked" if slot.get("booked_by") else "🟢 Available"
                sidebar.text(f"{start}-{end}: {status}")
            except:
                sidebar.text("Invalid slot")
    except:
        pass
