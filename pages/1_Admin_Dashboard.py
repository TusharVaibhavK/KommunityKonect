import streamlit as st
from utils.db import requests_col, users_col
from bson import ObjectId
from datetime import datetime, time
from pages.Layout import layout
from utils.notifications import notify_assignment, notify_completion
from utils.calendar_utils import (
    get_available_slots,
    book_slot,
    add_time_slot
)

# Shared layout + logout
layout()

# Debug info - Add this to see what's in the session state
st.sidebar.subheader("Debug Info")
st.sidebar.write(f"Username: {st.session_state.get('username', 'Not set')}")
st.sidebar.write(f"Role: {st.session_state.get('role', 'Not set')}")
st.sidebar.write(f"All session state keys: {list(st.session_state.keys())}")

# Only admins allowed - Fixed check
if "username" not in st.session_state or st.session_state.get("role") != "admin":
    st.warning("You must be an admin to access this page.")
    st.stop()

st.title("🛠️ Admin Dashboard")

# Filters
status_filter = st.selectbox(
    "Filter by Status", ["All", "Pending", "In Progress", "Completed"])
urgency_filter = st.selectbox(
    "Filter by Urgency", ["All", "Low", "Medium", "High"])

# Build query
query = {}
if status_filter != "All":
    query["status"] = status_filter
if urgency_filter != "All":
    query["urgency"] = urgency_filter

# Fetch jobs
requests = list(requests_col.find(query))

if not requests:
    st.info("No matching service requests found.")
else:
    # Get all servicemen
    servicemen = [user["username"]
                  for user in users_col.find({"role": "serviceman"})]

    for req in requests:
        with st.expander(f"{req.get('category', 'Unknown')} - {req.get('name', 'Unnamed')} @ {req.get('location', 'Unknown')}"):
            st.write(f"**Description:** {req['description']}")
            st.write(f"**Urgency:** {req.get('urgency', 'Not specified')}")
            st.write(f"**Status:** `{req.get('status', 'Pending')}`")
            st.write(
                f"**Assigned To:** {req.get('assigned_to', 'Not Assigned')}")
            st.write(f"**Timestamp:** {req.get('timestamp', 'N/A')}")

            # Show scheduled time if exists
            if req.get("scheduled_time"):
                st.write(
                    f"**Scheduled For:** {req['scheduled_time']['date']} {req['scheduled_time']['start']}-{req['scheduled_time']['end']}")

            # Update Fields
            current_status = req.get("status", "Pending")
            valid_statuses = ["Pending", "In Progress", "Completed"]
            if current_status not in valid_statuses:
                current_status = "Pending"

            new_status = st.selectbox(
                "Update Status",
                valid_statuses,
                index=valid_statuses.index(current_status),
                key=f"status_{req['_id']}"
            )

            assigned_to = req.get("assigned_to", "Not Assigned")
            assigned_to_list = ["Not Assigned"] + servicemen

            # Ensure the assigned_to value exists in the list, otherwise default to "Not Assigned"
            if assigned_to not in assigned_to_list:
                assigned_to = "Not Assigned"

            assigned_to = st.selectbox(
                "Assign to Serviceman",
                assigned_to_list,
                index=assigned_to_list.index(assigned_to),
                key=f"assign_{req['_id']}"
            )

            admin_notes = st.text_area(
                "Admin Notes",
                value=req.get("admin_notes", ""),
                key=f"notes_{req['_id']}"
            )

            # Scheduling Section
            if new_status == "In Progress" and assigned_to != "Not Assigned":
                st.subheader("📅 Schedule Repair")
                schedule_date = st.date_input(
                    "Select Date",
                    datetime.now().date(),
                    key=f"date_{req['_id']}"
                )

                serviceman_schedule = get_available_slots(
                    assigned_to,
                    datetime.combine(schedule_date, datetime.min.time())
                )

                available_slots = [
                    slot for slot in serviceman_schedule.get("time_slots", [])
                    if not slot.get("booked_by")
                ]

                if available_slots:
                    slot_options = [
                        f"{slot['start']} - {slot['end']}" for slot in available_slots]
                    selected_slot = st.selectbox(
                        "Available Time Slots",
                        slot_options,
                        key=f"slot_{req['_id']}"
                    )
                else:
                    st.warning("No available time slots for this serviceman")

            if st.button("✅ Update", key=f"update_{req['_id']}"):
                # Determine what changed
                status_changed = new_status != req.get("status")
                assignment_changed = assigned_to != req.get(
                    "assigned_to", "Not Assigned")

                # Update database
                update_data = {
                    "status": new_status,
                    "assigned_to": assigned_to if assigned_to != "Not Assigned" else None,
                    "admin_notes": admin_notes,
                    "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                }

                # Handle scheduling if applicable
                if (new_status == "In Progress" and assigned_to != "Not Assigned"
                        and available_slots and selected_slot):
                    start, end = selected_slot.split(" - ")
                    update_data["scheduled_time"] = {
                        "date": schedule_date.strftime("%Y-%m-%d"),
                        "start": start,
                        "end": end
                    }
                    book_slot(
                        str(req["_id"]),
                        assigned_to,
                        datetime.combine(schedule_date, datetime.min.time()),
                        {"start": start, "end": end}
                    )

                requests_col.update_one(
                    {"_id": ObjectId(req["_id"])},
                    {"$set": update_data}
                )

                # Send notifications
                if assignment_changed and assigned_to != "Not Assigned":
                    notify_assignment(str(req["_id"]), assigned_to)

                if status_changed and new_status == "Completed":
                    notify_completion(
                        str(req["_id"]), st.session_state["username"])

                st.success("✅ Updated successfully!")

# ---------------------------
# Admin Tools Sidebar
# ---------------------------


def get_pending_jobs():
    return list(requests_col.find({"status": "Pending"}))


def get_servicemen():
    return list(users_col.find({"role": "serviceman"}))


def assign_job(job_id, serviceman_username):
    requests_col.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {
            "assigned_to": serviceman_username,
            "status": "In Progress",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }}
    )
    notify_assignment(job_id, serviceman_username)


def force_complete_job(job_id, reason):
    requests_col.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {
            "status": "Completed",
            "admin_notes": f"[OVERRIDE] {reason}",
            "completed_by": st.session_state["username"],
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }}
    )
    notify_completion(job_id, st.session_state["username"])


if st.session_state.get("role") == "admin":
    st.sidebar.header("🧰 Admin Tools")

    # Job Assignment Section
    pending_jobs = get_pending_jobs()
    servicemen_list = get_servicemen()

    if pending_jobs and servicemen_list:
        st.sidebar.subheader("Quick Assign")
        job_options = [f"{job['category']}" for job in pending_jobs]
        selected_index = st.sidebar.selectbox(
            "Select Job",
            list(range(len(job_options))),
            format_func=lambda i: job_options[i]
        )
        selected_job = pending_jobs[selected_index]

        serviceman_options = [
            f"{s.get('name', 'Unknown')} ({s.get('username', 'NoUsername')})"
            for s in servicemen_list
        ]
        selected_serviceman_index = st.sidebar.selectbox(
            "Assign To",
            list(range(len(servicemen_list))),
            format_func=lambda i: serviceman_options[i]
        )
        selected_serviceman = servicemen_list[selected_serviceman_index]

        if st.sidebar.button("✅ Assign"):
            assign_job(str(selected_job["_id"]),
                       selected_serviceman["username"])
            st.success(f"Job assigned to {selected_serviceman['name']}")
            st.experimental_rerun()

    # Calendar Management Section
    with st.sidebar.expander("📅 Manage Schedules"):
        st.subheader("Add Availability")
        serviceman = st.selectbox(
            "Serviceman",
            [s["username"] for s in servicemen_list],
            key="calendar_serviceman"
        )
        avail_date = st.date_input(
            "Date",
            datetime.now().date(),
            key="calendar_date"
        )
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input(
                "Start Time",
                time(9, 0),
                key="calendar_start"
            )
        with col2:
            end_time = st.time_input(
                "End Time",
                time(17, 0),
                key="calendar_end"
            )

        if st.button("➕ Add Time Slot"):
            add_time_slot(
                serviceman,
                datetime.combine(avail_date, datetime.min.time()),
                start_time.strftime("%H:%M"),
                end_time.strftime("%H:%M")
            )
            st.success("Time slot added!")
            st.experimental_rerun()

    # Emergency Override
    if pending_jobs:
        st.sidebar.subheader("Emergency Tools")
        if st.sidebar.checkbox("🚨 Force Complete"):
            job_options = [f"{job['category']}" for job in pending_jobs]
            selected_index = st.sidebar.selectbox(
                "Select Job to Complete",
                list(range(len(job_options))),
                format_func=lambda i: job_options[i],
                key="force_complete_job"
            )
            selected_job = pending_jobs[selected_index]
            override_reason = st.sidebar.text_area(
                "Reason for Override",
                key="override_reason"
            )
            if st.sidebar.button("⚠️ Force Completion"):
                force_complete_job(str(selected_job["_id"]), override_reason)
                st.success("Job forcefully marked as completed.")
                st.experimental_rerun()
