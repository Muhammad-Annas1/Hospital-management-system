import streamlit as st
import os
import base64
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

# Import custom database & services
from database.db import get_db_path
from database.schema import create_tables
from database.seed import seed_database
from services.auth_service import authenticate_user, create_user
from services.patient_service import (
    add_patient, get_all_patients, get_patient_by_id, update_patient, delete_patient
)
from services.doctor_service import (
    add_doctor, get_all_doctors, get_doctor_by_id, update_doctor, delete_doctor, SPECIALIZATIONS
)
from services.appointment_service import (
    book_appointment, get_all_appointments, get_available_slots_for_booking,
    update_appointment_status, delete_appointment
)
from services.billing_service import (
    calculate_totals, create_bill, update_bill, delete_bill, get_all_bills
)
from utils.disease_rules import get_specialization_for_problem, DISCLAIMER_TEXT, DEFAULT_DISEASE_MAPPINGS
from utils.helpers import format_currency, render_badge, get_status_color
from utils.validators import validate_email, validate_phone, validate_dob

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="HealthCare+ Hospital Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Load Custom CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def set_background_image():
    bg_path = os.path.join(os.path.dirname(__file__), "assets", "background.png")
    if os.path.exists(bg_path):
        with open(bg_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{b64}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            /* Slight overlay to keep content readable */
            .stApp::before {{
                content: '';
                position: fixed;
                inset: 0;
                background: rgba(240, 244, 248, 0.82);
                z-index: 0;
                pointer-events: none;
            }}
            </style>
        """, unsafe_allow_html=True)

load_css()
set_background_image()

# Auto-initialize & seed database if DB file missing
db_file = get_db_path()
if not os.path.exists(db_file):
    seed_database()
else:
    create_tables()

# Initialize Session State
if "user" not in st.session_state:
    st.session_state["user"] = None

# --- AUTHENTICATION & LOGIN PAGE ---
def render_login_page():
    st.markdown("""
        <div class="main-header">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:6px;">
                <span style="font-size:2.6rem; line-height:1;">🏥</span>
                <div>
                    <div style="font-size:0.78rem; font-weight:700; letter-spacing:0.12em; color:#93c5fd; text-transform:uppercase; margin-bottom:4px;">Hospital Management System</div>
                    <h1 style="margin:0; font-size:2.2rem; font-weight:800; color:#ffffff; letter-spacing:-0.03em;">HealthCare<span style="color:#93c5fd;">+</span></h1>
                </div>
            </div>
            <p style="margin:8px 0 0 0; color:#bfdbfe; font-size:1rem; font-weight:400;">
                Integrated Patient Care &amp; Hospital Operations Platform
            </p>
            <div style="display:flex; gap:24px; margin-top:20px; padding-top:16px; border-top:1px solid rgba(255,255,255,0.1);">
                <div style="text-align:center;">
                    <div style="font-size:1.4rem; font-weight:800; color:#ffffff;">👥 Patients</div>
                    <div style="font-size:0.75rem; color:#93c5fd; font-weight:500; margin-top:2px;">Registration &amp; Records</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.4rem; font-weight:800; color:#ffffff;">👨‍⚕️ Doctors</div>
                    <div style="font-size:0.75rem; color:#93c5fd; font-weight:500; margin-top:2px;">Specialists &amp; Scheduling</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.4rem; font-weight:800; color:#ffffff;">💳 Billing</div>
                    <div style="font-size:0.75rem; color:#93c5fd; font-weight:500; margin-top:2px;">Invoices &amp; Payments</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:1.4rem; font-weight:800; color:#ffffff;">📈 Analytics</div>
                    <div style="font-size:0.75rem; color:#93c5fd; font-weight:500; margin-top:2px;">Reports &amp; Insights</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if "reg_success_msg" in st.session_state and st.session_state["reg_success_msg"]:
            st.success(st.session_state["reg_success_msg"])
            st.info("🔑 Please click on the **Sign In** tab above and enter your Username & Password.")

        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Patient Registration"])



        with tab_login:
            st.subheader("Login to your Account")
            with st.form("login_form", clear_on_submit=False):
                username_input = st.text_input("Username", placeholder="Enter Username")
                password_input = st.text_input("Password", type="password", placeholder="Enter Password")
                submit_login = st.form_submit_button("Sign In", use_container_width=True, type="primary")

                if submit_login:
                    user, err = authenticate_user(username_input, password_input)
                    if err:
                        st.error(err)
                    else:
                        st.session_state["user"] = user
                        st.session_state["reg_success_msg"] = None
                        st.success(f"Welcome back, {user['username']}!")
                        st.rerun()

        with tab_register:
            st.subheader("New Patient Registration")
            with st.form("register_form", clear_on_submit=True):
                rf_name = st.text_input("Full Name *", placeholder="Your Full Name")
                rcol1, rcol2 = st.columns(2)
                r_gender = rcol1.selectbox("Gender *", ["Male", "Female", "Other"])
                r_dob = rcol2.date_input("Date of Birth *", max_value=date.today(), value=date(1995, 1, 1))

                rcol3, rcol4 = st.columns(2)
                r_phone = rcol3.text_input("Phone Number *", placeholder="Your Phone Number")
                r_email = rcol4.text_input("Email Address *", placeholder="Your Email Address")

                r_address = st.text_area("Address *", placeholder="123 Main St...")

                rcol5, rcol6 = st.columns(2)
                r_bg = rcol5.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                r_disease = rcol6.selectbox("Primary Medical Concern / Symptom", list(DEFAULT_DISEASE_MAPPINGS.keys()))

                r_emergency = st.text_input("Emergency Contact", placeholder="Name & Phone number")

                st.markdown("##### Set Account Credentials")
                ucol1, ucol2 = st.columns(2)
                r_uname = ucol1.text_input("Desired Username *", placeholder="Your Username")
                r_pwd = ucol2.text_input("Desired Password *", type="password", placeholder="••••••••")

                submit_reg = st.form_submit_button("Register Patient Account", use_container_width=True, type="primary")

                if submit_reg:
                    patient_data = {
                        "full_name": rf_name,
                        "gender": r_gender,
                        "date_of_birth": r_dob,
                        "phone": r_phone,
                        "email": r_email,
                        "address": r_address,
                        "blood_group": r_bg,
                        "disease_problem": r_disease,
                        "emergency_contact": r_emergency,
                        "status": "Active"
                    }
                    pid, p_err = add_patient(patient_data)
                    if p_err:
                        st.error(p_err)
                    else:
                        u_ok, u_err = create_user(r_uname, r_pwd, "patient", patient_id=pid)
                        if u_ok:
                            st.session_state["reg_success_msg"] = f"🎉 Registration successful! Account created for '{r_uname}'. Please Sign In with your Username & Password."
                            st.rerun()
                        else:
                            st.error(u_err)

                            st.error(u_err)

# --- ADMIN DASHBOARD VIEWS ---
def render_admin_dashboard():
    today_label = date.today().strftime("%A, %d %B %Y")
    st.markdown(f"""
        <div class="main-header">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:6px;">
                <span style="font-size:2.6rem; line-height:1;">📊</span>
                <div>
                    <div style="font-size:0.78rem; font-weight:700; letter-spacing:0.12em; color:#93c5fd; text-transform:uppercase; margin-bottom:4px;">Admin Dashboard</div>
                    <h1 style="margin:0; font-size:2rem; font-weight:800; color:#ffffff; letter-spacing:-0.03em;">Hospital Administration</h1>
                </div>
            </div>
            <p style="margin:6px 0 0 0; color:#bfdbfe; font-size:0.95rem;">📅 {today_label} — Live hospital operations overview</p>
        </div>
    """, unsafe_allow_html=True)

    patients = get_all_patients()
    doctors = get_all_doctors()
    appointments = get_all_appointments()
    bills = get_all_bills()

    today_str = date.today().strftime("%Y-%m-%d")
    today_appts = [a for a in appointments if a["appointment_date"] == today_str]
    pending_appts = [a for a in appointments if a["status"] == "Pending"]
    completed_appts = [a for a in appointments if a["status"] == "Completed"]

    total_revenue = sum(b["total_amount"] for b in bills if b["payment_status"] == "Paid")
    pending_revenue = sum(b["total_amount"] for b in bills if b["payment_status"] != "Paid")

    # KPI Summary Cards
    kcol1, kcol2, kcol3, kcol4, kcol5, kcol6 = st.columns(6)
    kcol1.metric("👥 Total Patients", len(patients))
    kcol2.metric("👨‍⚕️ Total Doctors", len(doctors))
    kcol3.metric("📅 Today's Appts", len(today_appts))
    kcol4.metric("⏳ Pending Appts", len(pending_appts))
    kcol5.metric("💰 Total Revenue", format_currency(total_revenue))
    kcol6.metric("🔴 Pending Revenue", format_currency(pending_revenue))

    st.divider()


    # Charts Row 1
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Appointments by Status")
        if appointments:
            df_appt = pd.DataFrame(appointments)
            status_counts = df_appt["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            fig_pie = px.pie(
                status_counts, values="Count", names="Status",
                hole=0.4,
                color="Status",
                color_discrete_map={
                    "Pending": "#f59e0b",
                    "Confirmed": "#3b82f6",
                    "Completed": "#10b981",
                    "Cancelled": "#ef4444"
                }
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No appointments data available.")

    with c2:
        st.subheader("Doctors by Specialization")
        if doctors:
            df_doc = pd.DataFrame(doctors)
            spec_counts = df_doc["specialization"].value_counts().reset_index()
            spec_counts.columns = ["Specialization", "Count"]
            fig_bar = px.bar(
                spec_counts, x="Count", y="Specialization",
                orientation="h",
                color="Specialization",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No doctors data available.")

    # Charts Row 2
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Revenue by Payment Status")
        if bills:
            df_bills = pd.DataFrame(bills)
            rev_status = df_bills.groupby("payment_status")["total_amount"].sum().reset_index()
            fig_rev = px.bar(
                rev_status, x="payment_status", y="total_amount",
                labels={"payment_status": "Payment Status", "total_amount": "Total Revenue (PKR)"},
                color="payment_status",
                color_discrete_map={"Paid": "#10b981", "Pending": "#f59e0b", "Partially Paid": "#8b5cf6"}
            )
            st.plotly_chart(fig_rev, use_container_width=True)
        else:
            st.info("No billing data available.")

    with c4:
        st.subheader("Patient Registrations Trend")
        if patients:
            df_p = pd.DataFrame(patients)
            p_reg = df_p.groupby("registration_date").size().reset_index(name="Registrations")
            fig_line = px.line(p_reg, x="registration_date", y="Registrations", markers=True)
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No registration data available.")

def render_admin_patients():
    st.title("👥 Patient Management")

    tab1, tab2 = st.tabs(["📋 View Patients", "➕ Add New Patient"])

    with tab1:
        col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
        search = col_s1.text_input("🔍 Search by Name, Phone, Email", key="p_search")
        g_filter = col_s2.selectbox("Filter Gender", ["All", "Male", "Female", "Other"], key="p_gfilter")
        st_filter = col_s3.selectbox("Filter Status", ["All", "Active", "Inactive"], key="p_stfilter")

        patients = get_all_patients(search, g_filter, st_filter)
        if patients:
            df = pd.DataFrame(patients)
            st.dataframe(
                df[["patient_id", "full_name", "gender", "age", "phone", "email", "blood_group", "disease_problem", "registration_date", "status"]],
                use_container_width=True,
                hide_index=True
            )

            st.divider()
            st.subheader("🛠️ Patient Actions (Edit / Delete / Details)")
            sel_pid = st.selectbox("Select Patient to Manage", [p["patient_id"] for p in patients], format_func=lambda x: f"ID #{x} - {next(p['full_name'] for p in patients if p['patient_id']==x)}")
            
            selected_pat = get_patient_by_id(sel_pid)
            if selected_pat:
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    st.markdown("##### 📝 Edit Patient Information")
                    with st.form(f"edit_patient_{sel_pid}"):
                        ef_name = st.text_input("Full Name", value=selected_pat["full_name"])
                        egender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(selected_pat["gender"]))
                        edob = st.date_input("DOB", value=datetime.strptime(selected_pat["date_of_birth"], "%Y-%m-%d").date())
                        ephone = st.text_input("Phone", value=selected_pat["phone"])
                        eemail = st.text_input("Email", value=selected_pat["email"])
                        eaddress = st.text_area("Address", value=selected_pat["address"])
                        ebg = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], index=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(selected_pat["blood_group"]))
                        edisease = st.text_input("Disease/Problem", value=selected_pat["disease_problem"])
                        eemerg = st.text_input("Emergency Contact", value=selected_pat["emergency_contact"])
                        estatus = st.selectbox("Status", ["Active", "Inactive"], index=0 if selected_pat["status"]=="Active" else 1)

                        btn_update = st.form_submit_button("Update Patient Details", type="primary")
                        if btn_update:
                            up_data = {
                                "full_name": ef_name, "gender": egender, "date_of_birth": edob,
                                "phone": ephone, "email": eemail, "address": eaddress,
                                "blood_group": ebg, "disease_problem": edisease,
                                "emergency_contact": eemerg, "status": estatus
                            }
                            ok, err = update_patient(sel_pid, up_data)
                            if ok:
                                st.success(err)
                                st.rerun()
                            else:
                                st.error(err)

                with col_e2:
                    st.markdown("##### 🔍 Patient File Details & Delete")
                    st.json(selected_pat)

                    st.divider()
                    st.warning("⚠️ Destructive Area")
                    with st.expander("Delete Patient Record"):
                        st.error(f"Are you sure you want to permanently delete Patient #{sel_pid} ({selected_pat['full_name']})?")
                        if st.button(f"Confirm Delete Patient #{sel_pid}", type="primary"):
                            ok, err = delete_patient(sel_pid)
                            if ok:
                                st.success(err)
                                st.rerun()
                            else:
                                st.error(err)

    with tab2:
        st.subheader("Register New Patient Record")
        with st.form("admin_add_patient"):
            nf_name = st.text_input("Full Name *")
            ncol1, ncol2 = st.columns(2)
            ngender = ncol1.selectbox("Gender *", ["Male", "Female", "Other"])
            ndob = ncol2.date_input("Date of Birth *", value=date(1990, 1, 1), max_value=date.today())

            ncol3, ncol4 = st.columns(2)
            nphone = ncol3.text_input("Phone Number *", placeholder="Your Phone Number")
            nemail = ncol4.text_input("Email Address *", placeholder="Your Email")

            naddress = st.text_area("Address *")

            ncol5, ncol6 = st.columns(2)
            nbg = ncol5.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            ndisease = ncol6.text_input("Disease/Problem Description")

            nemerg = st.text_input("Emergency Contact")

            nbtn = st.form_submit_button("Add Patient Record", use_container_width=True, type="primary")
            if nbtn:
                p_data = {
                    "full_name": nf_name, "gender": ngender, "date_of_birth": ndob,
                    "phone": nphone, "email": nemail, "address": naddress,
                    "blood_group": nbg, "disease_problem": ndisease, "emergency_contact": nemerg,
                    "status": "Active"
                }
                pid, err = add_patient(p_data)
                if err:
                    st.error(err)
                else:
                    # Auto-generate user account for admin-created patient
                    clean_name = "".join(c for c in nf_name.lower() if c.isalnum() or c == ' ').strip().replace(" ", "_")
                    default_uname = f"{clean_name}_{pid}" if clean_name else f"patient_{pid}"
                    create_user(default_uname, "pass123", "patient", patient_id=pid)
                    
                    st.success(f"Patient registered successfully with ID #{pid}! (Default Username: {default_uname})")
                    st.rerun()


def render_admin_doctors():
    st.title("👨‍⚕️ Doctor Management")

    tab1, tab2 = st.tabs(["📋 View Doctors List", "➕ Add New Doctor"])

    with tab1:
        c1, c2, c3 = st.columns([2, 1, 1])
        search = c1.text_input("🔍 Search Doctor Name/Room", key="d_search")
        spec_filter = c2.selectbox("Filter Specialization", ["All"] + SPECIALIZATIONS, key="d_spec")
        status_filter = c3.selectbox("Filter Status", ["All", "Active", "Inactive"], key="d_status")

        doctors = get_all_doctors(search, spec_filter, status_filter)
        if doctors:
            df = pd.DataFrame(doctors)
            st.dataframe(
                df[["doctor_id", "full_name", "specialization", "qualification", "experience_years", "consultation_fee", "available_days", "start_time", "end_time", "room_number", "status"]],
                use_container_width=True,
                hide_index=True
            )

            st.divider()
            st.subheader("🛠️ Edit / Manage Doctor Profile")
            sel_did = st.selectbox("Select Doctor", [d["doctor_id"] for d in doctors], format_func=lambda x: f"ID #{x} - {next(d['full_name'] for d in doctors if d['doctor_id']==x)}")
            sel_doc = get_doctor_by_id(sel_did)

            if sel_doc:
                dcol1, dcol2 = st.columns(2)
                with dcol1:
                    with st.form(f"edit_doc_{sel_did}"):
                        efname = st.text_input("Full Name", value=sel_doc["full_name"])
                        espec = st.selectbox("Specialization", SPECIALIZATIONS, index=SPECIALIZATIONS.index(sel_doc["specialization"]) if sel_doc["specialization"] in SPECIALIZATIONS else 0)
                        equal = st.text_input("Qualification", value=sel_doc["qualification"])
                        ephone = st.text_input("Phone", value=sel_doc["phone"])
                        eemail = st.text_input("Email", value=sel_doc["email"])
                        eexp = st.number_input("Experience (Years)", value=sel_doc["experience_years"], min_value=0)
                        efee = st.number_input("Consultation Fee (Rs.)", value=float(sel_doc["consultation_fee"]), min_value=0.0)

                        eavail = st.text_input("Available Days (comma-separated)", value=sel_doc["available_days"])
                        estart = st.text_input("Start Time (HH:MM)", value=sel_doc["start_time"])
                        eend = st.text_input("End Time (HH:MM)", value=sel_doc["end_time"])
                        eroom = st.text_input("Room Number", value=sel_doc["room_number"])
                        estatus = st.selectbox("Status", ["Active", "Inactive"], index=0 if sel_doc["status"]=="Active" else 1)

                        btn_doc_up = st.form_submit_button("Update Doctor Profile", type="primary")
                        if btn_doc_up:
                            up_doc_data = {
                                "full_name": efname, "specialization": espec, "qualification": equal,
                                "phone": ephone, "email": eemail, "experience_years": eexp,
                                "consultation_fee": efee, "available_days": eavail, "start_time": estart,
                                "end_time": eend, "slot_duration": 30, "room_number": eroom, "status": estatus
                            }
                            ok, err = update_doctor(sel_did, up_doc_data)
                            if ok:
                                st.success(err)
                                st.rerun()
                            else:
                                st.error(err)

                with dcol2:
                    st.markdown("##### 👨‍⚕️ Profile Summary")
                    st.info(f"""
                        **Name**: {sel_doc['full_name']}  
                        **Specialization**: {sel_doc['specialization']}  
                        **Fee**: {format_currency(sel_doc['consultation_fee'])}  
                        **Schedule**: {sel_doc['available_days']} ({sel_doc['start_time']} - {sel_doc['end_time']})  
                        **Location**: {sel_doc['room_number']}
                    """)

                    st.divider()
                    with st.expander("Delete Doctor Record"):
                        st.error(f"Are you sure you want to delete Doctor #{sel_did}?")
                        if st.button(f"Confirm Delete Doctor #{sel_did}", type="primary"):
                            ok, err = delete_doctor(sel_did)
                            if ok:
                                st.success(err)
                                st.rerun()
                            else:
                                st.error(err)

    with tab2:
        st.subheader("Add New Doctor")
        with st.form("add_doctor_form"):
            dfname = st.text_input("Full Name *", placeholder="Dr. Jane Smith")
            dspec = st.selectbox("Specialization *", SPECIALIZATIONS)
            dqual = st.text_input("Qualification *", placeholder="MD, Cardiology")

            col_d1, col_d2 = st.columns(2)
            dphone = col_d1.text_input("Phone Number *")
            demail = col_d2.text_input("Email Address *")

            col_d3, col_d4 = st.columns(2)
            dexp = col_d3.number_input("Experience (Years)", min_value=0, value=5)
            dfee = col_d4.number_input("Consultation Fee (Rs.)", min_value=0.0, value=2000.0)

            davail = st.text_input("Available Days (comma-separated) *", value="Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday")
            col_t1, col_t2, col_t3 = st.columns(3)
            dstart = col_t1.text_input("Start Time (HH:MM) *", value="09:00")
            dend = col_t2.text_input("End Time (HH:MM) *", value="21:00")
            droom = col_t3.text_input("Room Number *", value="Room 101")

            btn_add_doc = st.form_submit_button("Add Doctor", use_container_width=True, type="primary")
            if btn_add_doc:
                new_doc = {
                    "full_name": dfname, "specialization": dspec, "qualification": dqual,
                    "phone": dphone, "email": demail, "experience_years": dexp,
                    "consultation_fee": dfee, "available_days": davail, "start_time": dstart,
                    "end_time": dend, "slot_duration": 30, "room_number": droom, "status": "Active"
                }
                did, err = add_doctor(new_doc)
                if err:
                    st.error(err)
                else:
                    st.success(f"Doctor added successfully with ID #{did}!")
                    st.rerun()

def render_admin_appointments():
    st.title("📅 Appointment Management")

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    search = col1.text_input("🔍 Search Patient/Doctor", key="app_search")
    status_flt = col2.selectbox("Filter Status", ["All", "Pending", "Confirmed", "Completed", "Cancelled"], key="app_st")
    
    patients = get_all_patients()
    doctors = get_all_doctors()
    
    pat_opts = ["All"] + [f"ID #{p['patient_id']} - {p['full_name']}" for p in patients]
    doc_opts = ["All"] + [f"ID #{d['doctor_id']} - {d['full_name']}" for d in doctors]

    sel_pat_opt = col3.selectbox("Filter Patient", pat_opts)
    sel_doc_opt = col4.selectbox("Filter Doctor", doc_opts)

    pid_flt = int(sel_pat_opt.split("#")[1].split("-")[0].strip()) if sel_pat_opt != "All" else None
    did_flt = int(sel_doc_opt.split("#")[1].split("-")[0].strip()) if sel_doc_opt != "All" else None

    appts = get_all_appointments(patient_id_filter=pid_flt, doctor_id_filter=did_flt, status_filter=status_flt, search_term=search)

    if appts:
        df = pd.DataFrame(appts)
        st.dataframe(
            df[["appointment_id", "patient_name", "doctor_name", "specialization", "appointment_date", "appointment_time", "reason", "status", "room_number"]],
            use_container_width=True,
            hide_index=True
        )

        st.divider()
        st.subheader("🛠️ Update Appointment Status & Actions")
        sel_aid = st.selectbox("Select Appointment", [a["appointment_id"] for a in appts], format_func=lambda x: f"Appt #{x} - Patient: {next(a['patient_name'] for a in appts if a['appointment_id']==x)} with {next(a['doctor_name'] for a in appts if a['appointment_id']==x)} ({next(a['appointment_date'] for a in appts if a['appointment_id']==x)} {next(a['appointment_time'] for a in appts if a['appointment_id']==x)})")
        
        sel_appt = next(a for a in appts if a["appointment_id"] == sel_aid)
        st.info(f"Current Status: **{sel_appt['status']}** | Patient: **{sel_appt['patient_name']}** | Doctor: **{sel_appt['doctor_name']}** | Fee: **{format_currency(sel_appt['consultation_fee'])}**")

        stcol1, stcol2, stcol3, stcol4, stcol5 = st.columns(5)
        if stcol1.button("⏳ Mark Pending", use_container_width=True):
            ok, msg = update_appointment_status(sel_aid, "Pending")
            if ok: st.success(msg); st.rerun()
            else: st.error(msg)

        if stcol2.button("✅ Confirm Appointment", use_container_width=True):
            ok, msg = update_appointment_status(sel_aid, "Confirmed")
            if ok: st.success(msg); st.rerun()
            else: st.error(msg)

        if stcol3.button("🏥 Patient Arrived", use_container_width=True):
            ok, msg = update_appointment_status(sel_aid, "Arrived / Waiting")
            if ok: st.success(msg); st.rerun()
            else: st.error(msg)
            
        if stcol4.button("✔️ Mark Completed", use_container_width=True):
            ok, msg = update_appointment_status(sel_aid, "Completed")
            if ok: st.success(msg); st.rerun()
            else: st.error(msg)
            
        if stcol5.button("❌ Cancel", use_container_width=True):
            ok, msg = update_appointment_status(sel_aid, "Cancelled")
            if ok: st.success(msg); st.rerun()
            else: st.error(msg)

        st.divider()
        # Bill & Payment Collection on Arrival Management for Selected Appointment
        existing_bills = get_all_bills()
        has_bill = any(b["appointment_id"] == sel_aid for b in existing_bills)

        if not has_bill:
            st.warning("⚠️ No invoice generated yet for this appointment.")
            c_b1, c_b2 = st.columns(2)
            if c_b1.button("💰 Auto-Generate Pending Invoice", use_container_width=True, type="primary"):
                b_data = {
                    "patient_id": sel_appt["patient_id"],
                    "appointment_id": sel_aid,
                    "consultation_fee": sel_appt["consultation_fee"],
                    "medicine_charges": 0.0,
                    "laboratory_charges": 0.0,
                    "other_charges": 0.0,
                    "discount": 0.0,
                    "tax": 0.0,
                    "payment_status": "Pending",
                    "payment_method": "Cash (Pay at Counter)",
                    "bill_date": str(date.today())
                }
                bid, b_err = create_bill(b_data)
                if bid:
                    st.success(f"Invoice #{bid} generated successfully!")
                    st.rerun()
                else:
                    st.error(b_err)

            if c_b2.button("💵 Receive Cash/Card Payment Now (On Arrival)", use_container_width=True):
                b_data = {
                    "patient_id": sel_appt["patient_id"],
                    "appointment_id": sel_aid,
                    "consultation_fee": sel_appt["consultation_fee"],
                    "medicine_charges": 0.0,
                    "laboratory_charges": 0.0,
                    "other_charges": 0.0,
                    "discount": 0.0,
                    "tax": 0.0,
                    "payment_status": "Paid",
                    "payment_method": "Cash (Paid at Counter)",
                    "bill_date": str(date.today())
                }
                bid, b_err = create_bill(b_data)
                if bid:
                    st.success(f"Invoice #{bid} generated & marked PAID at hospital counter!")
                    st.rerun()
                else:
                    st.error(b_err)
        else:
            bill_obj = next(b for b in existing_bills if b["appointment_id"] == sel_aid)
            st.success(f"🧾 Invoice #{bill_obj['bill_id']} Active | Payment Status: **{bill_obj['payment_status']}** | Total Due: **{format_currency(bill_obj['total_amount'])}** | Method: **{bill_obj['payment_method']}**")
            if bill_obj["payment_status"] != "Paid":
                p_col1, p_col2 = st.columns(2)
                pay_method_admin = p_col1.selectbox("Collect Payment Method", ["Cash (Paid at Counter)", "Card (Paid at Counter / POS)", "Bank Transfer"], key=f"adm_pay_m_{bill_obj['bill_id']}")
                if p_col2.button("💵 Collect Payment & Mark Paid", type="primary", use_container_width=True):
                    up_b = {
                        "consultation_fee": bill_obj["consultation_fee"],
                        "medicine_charges": bill_obj["medicine_charges"],
                        "laboratory_charges": bill_obj["laboratory_charges"],
                        "other_charges": bill_obj["other_charges"],
                        "discount": bill_obj["discount"],
                        "tax": bill_obj["tax"],
                        "payment_status": "Paid",
                        "payment_method": pay_method_admin,
                        "bill_date": bill_obj["bill_date"]
                    }
                    ok, msg = update_bill(bill_obj["bill_id"], up_b)
                    if ok:
                        st.success(f"🎉 Payment collected successfully at counter via {pay_method_admin}!")
                        st.rerun()
                    else:
                        st.error(msg)


    else:
        st.info("No appointments found matching the specified filters.")

    st.divider()
    with st.expander("➕ Create New Appointment (Admin Override)"):
        st.markdown("#### Interactive Appointment Booking")
        col_ab1, col_ab2, col_ab3 = st.columns(3)
        b_pat = col_ab1.selectbox("Select Patient *", patients, format_func=lambda p: f"#{p['patient_id']} - {p['full_name']}", key="adm_b_pat")
        b_doc = col_ab2.selectbox("Select Doctor *", doctors, format_func=lambda d: f"#{d['doctor_id']} - {d['full_name']} ({d['specialization']})", key="adm_b_doc")
        b_date = col_ab3.date_input("Appointment Date *", min_value=date.today(), key="adm_b_date")
        
        # Real-time slot fetching outside form
        slots, s_err = get_available_slots_for_booking(b_doc['doctor_id'], b_date) if b_doc else ([], "")
        if s_err:
            st.warning(s_err)
        else:
            st.success(f"Available slots found: {len(slots)}")

        with st.form("admin_book_form"):
            b_slot = st.selectbox("Available Time Slot *", slots if slots else ["No slots available"])
            b_reason = st.text_input("Reason / Notes", placeholder="Consultation reason...")
            b_status = st.selectbox("Initial Status", ["Confirmed", "Pending"])

            btn_b = st.form_submit_button("Book Appointment", type="primary")
            if btn_b:
                if not slots or b_slot == "No slots available":
                    st.error("Cannot book. Please choose a date with available slots.")
                else:
                    aid, err = book_appointment(b_pat['patient_id'], b_doc['doctor_id'], str(b_date), b_slot, b_reason, b_status)
                    if err:
                        st.error(err)
                    else:
                        st.success(f"Appointment #{aid} booked successfully!")
                        st.rerun()

def render_admin_billing():
    st.title("💳 Billing & Payments Engine")

    tab1, tab2 = st.tabs(["📋 Bills Directory", "🧾 Generate New Bill"])

    with tab1:
        col1, col2 = st.columns([2, 1])
        search = col1.text_input("🔍 Search Patient/Doctor/Bill ID", key="bill_search")
        status_flt = col2.selectbox("Filter Payment Status", ["All", "Paid", "Pending", "Partially Paid"], key="bill_st")

        bills = get_all_bills(payment_status_filter=status_flt, search_term=search)
        if bills:
            df = pd.DataFrame(bills)
            st.dataframe(
                df[["bill_id", "patient_name", "doctor_name", "bill_date", "consultation_fee", "medicine_charges", "laboratory_charges", "other_charges", "discount", "tax", "total_amount", "payment_status", "payment_method"]],
                use_container_width=True,
                hide_index=True
            )

            st.divider()
            st.subheader("🛠️ Update Payment Status / Edit Bill")
            sel_bid = st.selectbox("Select Bill", [b["bill_id"] for b in bills], format_func=lambda x: f"Bill #{x} - Patient: {next(b['patient_name'] for b in bills if b['bill_id']==x)} ({format_currency(next(b['total_amount'] for b in bills if b['bill_id']==x))})")
            sel_bill = next(b for b in bills if b["bill_id"] == sel_bid)

            with st.form(f"edit_bill_{sel_bid}"):
                st.markdown(f"##### Editing Invoice #{sel_bid}")
                ec1, ec2, ec3, ec4 = st.columns(4)
                ec_fee = ec1.number_input("Consultation Fee (Rs.)", value=float(sel_bill["consultation_fee"]), min_value=0.0)
                em_fee = ec2.number_input("Medicine Charges (Rs.)", value=float(sel_bill["medicine_charges"]), min_value=0.0)
                el_fee = ec3.number_input("Lab Charges (Rs.)", value=float(sel_bill["laboratory_charges"]), min_value=0.0)
                eo_fee = ec4.number_input("Other Charges (Rs.)", value=float(sel_bill["other_charges"]), min_value=0.0)

                ec5, ec6, ec7, ec8 = st.columns(4)
                edisc = ec5.number_input("Discount (Rs.)", value=float(sel_bill["discount"]), min_value=0.0)
                etax = ec6.number_input("Tax (Rs.)", value=float(sel_bill["tax"]), min_value=0.0)
                status_opts = ["Paid", "Pending", "Partially Paid"]
                curr_st = sel_bill.get("payment_status", "Pending")
                if curr_st not in status_opts:
                    status_opts.append(curr_st)
                st_idx = status_opts.index(curr_st)

                method_opts = ["Cash", "Card", "Bank Transfer", "Cash (Pay at Counter)", "Cash (Paid at Counter)", "Card (Paid at Counter / POS)", "Online Card Payment"]
                curr_m = sel_bill.get("payment_method", "Cash")
                if curr_m not in method_opts:
                    method_opts.append(curr_m)
                m_idx = method_opts.index(curr_m)

                epay_st = ec7.selectbox("Payment Status", status_opts, index=st_idx)
                epay_m = ec8.selectbox("Payment Method", method_opts, index=m_idx)

                # Auto preview formula calculation
                calc = calculate_totals(ec_fee, em_fee, el_fee, eo_fee, edisc, etax)
                st.info(f"Subtotal: **{format_currency(calc['subtotal'])}** | Total Calculated Amount: **{format_currency(calc['total_amount'])}**")

                btn_up_bill = st.form_submit_button("Update Invoice Details", type="primary")
                if btn_up_bill:
                    up_data = {
                        "consultation_fee": ec_fee, "medicine_charges": em_fee, "laboratory_charges": el_fee,
                        "other_charges": eo_fee, "discount": edisc, "tax": etax,
                        "payment_status": epay_st, "payment_method": epay_m, "bill_date": sel_bill["bill_date"]
                    }
                    ok, err = update_bill(sel_bid, up_data)
                    if ok:
                        st.success(err)
                        st.rerun()
                    else:
                        st.error(err)

    with tab2:
        st.subheader("Generate Bill for Completed/Confirmed Appointment")
        appts = get_all_appointments()
        unbilled_appts = [a for a in appts if a["status"] in ["Confirmed", "Completed"]]

        if not unbilled_appts:
            st.info("No confirmed or completed appointments found to bill.")
        else:
            sel_appt_obj = st.selectbox("Select Appointment to Bill", unbilled_appts, format_func=lambda a: f"Appt #{a['appointment_id']} - Patient: {a['patient_name']} with Dr. {a['doctor_name']} ({a['appointment_date']})")
            
            with st.form("create_bill_form"):
                st.markdown(f"**Patient**: {sel_appt_obj['patient_name']} | **Doctor Fee**: {format_currency(sel_appt_obj['consultation_fee'])}")
                
                bc1, bc2 = st.columns(2)
                b_cfee = bc1.number_input("Consultation Fee (Rs.)", value=float(sel_appt_obj["consultation_fee"]), min_value=0.0)
                b_mfee = bc2.number_input("Medicine Charges (Rs.)", value=0.0, min_value=0.0)

                bc3, bc4 = st.columns(2)
                b_lfee = bc3.number_input("Laboratory Charges (Rs.)", value=0.0, min_value=0.0)
                b_ofee = bc4.number_input("Other Charges (Rs.)", value=0.0, min_value=0.0)

                bc5, bc6 = st.columns(2)
                b_disc = bc5.number_input("Discount (Rs.)", value=0.0, min_value=0.0)
                b_tax = bc6.number_input("Tax (Rs.)", value=0.0, min_value=0.0)

                bc7, bc8 = st.columns(2)
                b_pay_st = bc7.selectbox("Payment Status", ["Paid", "Pending", "Partially Paid"])
                b_pay_m = bc8.selectbox("Payment Method", ["Cash", "Card", "Bank Transfer"])

                calc = calculate_totals(b_cfee, b_mfee, b_lfee, b_ofee, b_disc, b_tax)
                st.write(f"### Total Calculated Amount: **{format_currency(calc['total_amount'])}**")

                btn_gen_bill = st.form_submit_button("Generate Invoice", type="primary", use_container_width=True)
                if btn_gen_bill:
                    b_data = {
                        "patient_id": sel_appt_obj["patient_id"],
                        "appointment_id": sel_appt_obj["appointment_id"],
                        "consultation_fee": b_cfee,
                        "medicine_charges": b_mfee,
                        "laboratory_charges": b_lfee,
                        "other_charges": b_ofee,
                        "discount": b_disc,
                        "tax": b_tax,
                        "payment_status": b_pay_st,
                        "payment_method": b_pay_m,
                        "bill_date": date.today().strftime("%Y-%m-%d")
                    }
                    bid, err = create_bill(b_data)
                    if err:
                        st.error(err)
                    else:
                        st.success(f"Bill generated successfully with Invoice ID #{bid}!")
                        st.rerun()

def render_admin_reports():
    st.title("📈 Reports & Analytics Export")

    col_f1, col_f2 = st.columns(2)
    start_d = col_f1.date_input("Start Date", value=date.today() - timedelta(days=90))

    end_d = col_f2.date_input("End Date", value=date.today())

    tab_r1, tab_r2, tab_r3 = st.tabs(["📋 Patient Registration Report", "📅 Appointments Report", "💰 Revenue & Financial Report"])

    with tab_r1:
        st.subheader("📋 Patient Registrations Report (Date & Time Tracker)")
        patients = get_all_patients()
        df_p = pd.DataFrame(patients)
        if not df_p.empty:
            df_p["reg_dt"] = pd.to_datetime(df_p["registration_date"]).dt.date
            filtered_p = df_p[(df_p["reg_dt"] >= start_d) & (df_p["reg_dt"] <= end_d)]
            
            if "registration_time" not in filtered_p.columns:
                filtered_p["registration_time"] = "09:00 AM"

            cols_to_show = ["patient_id", "full_name", "gender", "age", "phone", "email", "blood_group", "disease_problem", "registration_date", "registration_time", "status"]
            existing_cols = [c for c in cols_to_show if c in filtered_p.columns]

            st.markdown(f"**Showing {len(filtered_p)} Registered Patients** (From {start_d} to {end_d})")
            st.dataframe(filtered_p[existing_cols], use_container_width=True, hide_index=True)
            
            csv_p = filtered_p[existing_cols].to_csv(index=False).encode('utf-8')
            st.download_button("📥 Export Patients Report (CSV)", data=csv_p, file_name=f"patients_registered_{start_d}_to_{end_d}.csv", mime="text/csv", type="primary")
        else:
            st.info("No patient records found within the selected date range.")


    with tab_r2:
        st.subheader("Appointments Analytics Report")
        appts = get_all_appointments()
        df_a = pd.DataFrame(appts)
        if not df_a.empty:
            df_a["appt_dt"] = pd.to_datetime(df_a["appointment_date"]).dt.date
            filtered_a = df_a[(df_a["appt_dt"] >= start_d) & (df_a["appt_dt"] <= end_d)]
            st.dataframe(filtered_a[["appointment_id", "patient_name", "doctor_name", "specialization", "appointment_date", "appointment_time", "status"]], use_container_width=True)
            csv_a = filtered_a.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Export Appointments CSV", data=csv_a, file_name=f"appointments_report_{start_d}_to_{end_d}.csv", mime="text/csv")
        else:
            st.info("No records found.")

    with tab_r3:
        st.subheader("Revenue & Financial Report")
        bills = get_all_bills()
        df_b = pd.DataFrame(bills)
        if not df_b.empty:
            df_b["b_dt"] = pd.to_datetime(df_b["bill_date"]).dt.date
            filtered_b = df_b[(df_b["b_dt"] >= start_d) & (df_b["b_dt"] <= end_d)]
            st.dataframe(filtered_b[["bill_id", "patient_name", "doctor_name", "bill_date", "total_amount", "payment_status", "payment_method"]], use_container_width=True)
            csv_b = filtered_b.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Export Financial Revenue CSV", data=csv_b, file_name=f"revenue_report_{start_d}_to_{end_d}.csv", mime="text/csv")
        else:
            st.info("No records found.")

def render_admin_settings():
    st.title("⚙️ System Settings & Reset")

    st.markdown("##### 🔄 Reset / Reseed Demo Database")
    st.warning("Clicking this button will restore the hospital database to the initial realistic seed state with 10 patients, 8 doctors, appointments, and bills.")
    if st.button("Reset Database to Demo State", type="primary"):
        seed_database()
        st.success("Database successfully reset and re-seeded!")
        st.rerun()

# --- PATIENT INTERFACE VIEWS ---
def render_patient_dashboard():
    user = st.session_state["user"]
    patient = get_patient_by_id(user["patient_id"]) if user.get("patient_id") else None

    if not patient:
        st.error("Patient profile not found.")
        return

    st.title(f"👋 Welcome, {patient['full_name']}")
    st.markdown(f"**Patient ID**: #{patient['patient_id']} | **Blood Group**: {patient['blood_group']} | **Registered**: {patient['registration_date']}")

    my_appts = get_all_appointments(patient_id_filter=patient["patient_id"])
    my_bills = get_all_bills(patient_id_filter=patient["patient_id"])

    upcoming = [a for a in my_appts if a["status"] in ["Pending", "Confirmed"]]
    total_due = sum(b["total_amount"] for b in my_bills if b["payment_status"] != "Paid")

    c1, c2, c3 = st.columns(3)
    c1.metric("Upcoming Appointments", len(upcoming))
    c2.metric("Total Appointments History", len(my_appts))
    c3.metric("Outstanding Balance", format_currency(total_due))

    st.divider()
    st.subheader("📌 Next Upcoming Appointment")
    if upcoming:
        next_a = upcoming[0]
        st.success(f"""
            **Date**: {next_a['appointment_date']} at {next_a['appointment_time']}  
            **Doctor**: {next_a['doctor_name']} ({next_a['specialization']})  
            **Location**: {next_a['room_number']}  
            **Status**: {next_a['status']}
        """)
    else:
        st.info("You have no upcoming appointments scheduled.")

def render_patient_find_doctor():
    st.title("🔍 Find Doctor & Disease Matcher")

    st.markdown(DISCLAIMER_TEXT, unsafe_allow_html=True)

    st.subheader("Step 1: Select your Disease / Medical Problem")
    selected_prob = st.selectbox("Common Health Concerns", list(DEFAULT_DISEASE_MAPPINGS.keys()))
    custom_prob = st.text_input("Or describe your symptom (e.g. skin rash, toothache, back pain):")

    prob_input = custom_prob.strip() if custom_prob.strip() else selected_prob
    recommended_spec = get_specialization_for_problem(prob_input)

    st.success(f"💡 Recommended Medical Department: **{recommended_spec}**")

    st.divider()
    st.subheader(f"Step 2: Available Doctors in {recommended_spec}")

    doctors = get_all_doctors(spec_filter=recommended_spec, status_filter="Active")
    if doctors:
        for d in doctors:
            with st.container():
                st.markdown(f"""
                    ### {d['full_name']}
                    * **Qualification**: {d['qualification']}
                    * **Experience**: {d['experience_years']} Years
                    * **Consultation Fee**: {format_currency(d['consultation_fee'])}
                    * **Available Days**: {d['available_days']} ({d['start_time']} - {d['end_time']})
                    * **Room**: {d['room_number']}
                """)
                st.divider()
    else:
        st.info(f"No active doctors currently available in {recommended_spec}. Displaying all active physicians below:")
        all_docs = get_all_doctors(status_filter="Active")
        for d in all_docs:
            st.markdown(f"**{d['full_name']}** ({d['specialization']}) - {format_currency(d['consultation_fee'])}")

def render_patient_book_appointment():
    user = st.session_state["user"]
    patient_id = user.get("patient_id")

    st.title("📅 Book an Appointment")
    st.markdown(DISCLAIMER_TEXT, unsafe_allow_html=True)

    doctors = get_all_doctors(status_filter="Active")
    if not doctors:
        st.error("No active doctors available for booking.")
        return

    st.markdown("### Select Doctor & Preferred Date")
    col_pb1, col_pb2 = st.columns(2)
    
    sel_prob = col_pb1.selectbox("Disease / Reason for Visit", list(DEFAULT_DISEASE_MAPPINGS.keys()), key="p_book_prob")
    rec_spec = get_specialization_for_problem(sel_prob)
    col_pb1.caption(f"Recommended Department: **{rec_spec}**")

    sorted_docs = sorted(doctors, key=lambda d: 0 if d["specialization"]==rec_spec else 1)
    sel_doc = col_pb2.selectbox("Select Doctor *", sorted_docs, format_func=lambda d: f"{d['full_name']} ({d['specialization']}) - Fee: {format_currency(d['consultation_fee'])}", key="p_book_doc")

    b_date = st.date_input("Preferred Date *", min_value=date.today(), key="p_book_date")

    # Real-time slot checking outside form
    slots, slot_err = get_available_slots_for_booking(sel_doc["doctor_id"], b_date)
    if slot_err:
        st.warning(f"⚠️ {slot_err}")
    else:
        st.success(f"✅ Found {len(slots)} available time slots for {b_date.strftime('%A, %d %B %Y')}")

    with st.form("patient_booking_form"):
        sel_slot = st.selectbox("Select Available Time Slot *", slots if slots else ["No slots available"])
        reason_notes = st.text_area("Additional Notes / Symptoms", placeholder="Describe your symptoms...")

        btn_submit = st.form_submit_button("Confirm Booking Request", type="primary", use_container_width=True)

        if btn_submit:
            if not slots or sel_slot == "No slots available":
                st.error("Selected slot is unavailable. Please pick another date or doctor.")
            else:
                aid, err = book_appointment(patient_id, sel_doc["doctor_id"], str(b_date), sel_slot, reason_notes, "Pending")
                if err:
                    st.error(err)
                else:
                    st.success(f"Appointment booked successfully with ID #{aid}! Status is Pending approval.")
                    st.rerun()

def render_patient_my_appointments():
    user = st.session_state["user"]
    patient_id = user.get("patient_id")

    st.title("📋 My Appointments History")

    appts = get_all_appointments(patient_id_filter=patient_id)
    if appts:
        for a in appts:
            st_color = "🟢" if a['status'] in ["Confirmed", "Completed"] else ("🟡" if a['status'] == "Pending" else ("🔵" if "Arrived" in a['status'] else "🔴"))
            with st.expander(f"{st_color} Appt #{a['appointment_id']} - {a['appointment_date']} at {a['appointment_time']} | Status: {a['status']}"):
                st.markdown(f"""
                    * **Doctor**: {a['doctor_name']} ({a['specialization']})
                    * **Room**: {a['room_number']}
                    * **Appointment Status**: **{a['status']}**
                    * **Reason**: {a['reason']}
                """)
                if "Arrived" in a['status']:
                    st.info("🏥 You have arrived at the hospital counter. Please wait for your token call.")
                elif a['status'] == "Confirmed":
                    st.success("✅ Your appointment is confirmed! Upon arriving at the hospital, you can pay your fee by Cash or Card at the reception counter.")
                
                if a["status"] in ["Pending", "Confirmed"]:
                    if st.button(f"Cancel Appointment #{a['appointment_id']}", key=f"cancel_{a['appointment_id']}"):
                        ok, msg = update_appointment_status(a["appointment_id"], "Cancelled")
                        if ok: st.success(msg); st.rerun()
                        else: st.error(msg)
    else:
        st.info("No appointment history found.")

def render_patient_my_bills():
    user = st.session_state["user"]
    patient_id = user.get("patient_id")

    st.title("🧾 My Billing History")

    bills = get_all_bills(patient_id_filter=patient_id)
    if bills:
        for b in bills:
            with st.expander(f"Invoice #{b['bill_id']} - Date: {b['bill_date']} - Status: {b['payment_status']} ({format_currency(b['total_amount'])})"):
                st.markdown(f"""
                    * **Doctor**: {b['doctor_name']} ({b['specialization']})
                    * **Consultation Fee**: {format_currency(b['consultation_fee'])}
                    * **Medicine Charges**: {format_currency(b['medicine_charges'])}
                    * **Lab Charges**: {format_currency(b['laboratory_charges'])}
                    * **Other Charges**: {format_currency(b['other_charges'])}
                    * **Discount**: -{format_currency(b['discount'])}
                    * **Tax**: +{format_currency(b['tax'])}
                    * **Total Amount**: **{format_currency(b['total_amount'])}**
                    * **Payment Status**: **{b['payment_status']}**
                    * **Payment Method**: {b['payment_method']}
                """)
                if b["payment_status"] != "Paid":
                    st.divider()
                    st.markdown("##### 💳 Pay Your Bill / Appointment Fee")
                    st.info("ℹ️ You can pay online right now or pay by Cash/Card upon arriving at the hospital counter.")
                    pay_m = st.selectbox(
                        "Select Payment Method", 
                        ["Cash (Pay at Hospital Counter)", "Card (Pay at Hospital Counter / POS)", "Online Card Payment", "Bank Transfer"], 
                        key=f"pay_m_{b['bill_id']}"
                    )
                    
                    if "Hospital Counter" in pay_m:
                        btn_label = f"Confirm Payment Choice ({pay_m.split('(')[0].strip()})"
                    else:
                        btn_label = f"Pay {format_currency(b['total_amount'])} Now via {pay_m}"

                    if st.button(btn_label, key=f"pay_btn_{b['bill_id']}", type="primary"):
                        up_b = {
                            "consultation_fee": b["consultation_fee"],
                            "medicine_charges": b["medicine_charges"],
                            "laboratory_charges": b["laboratory_charges"],
                            "other_charges": b["other_charges"],
                            "discount": b["discount"],
                            "tax": b["tax"],
                            "payment_status": "Paid",
                            "payment_method": pay_m,
                            "bill_date": b["bill_date"]
                        }
                        ok, msg = update_bill(b["bill_id"], up_b)
                        if ok:
                            st.success(f"🎉 Payment recorded successfully! Selected Method: **{pay_m}**.")
                            st.rerun()
                        else:
                            st.error(msg)

    else:
        st.info("No billing invoices found.")

def render_patient_profile():
    user = st.session_state["user"]
    patient_id = user.get("patient_id")
    patient = get_patient_by_id(patient_id)

    st.title("👤 My Profile")

    if patient:
        with st.form("patient_profile_form"):
            pfname = st.text_input("Full Name", value=patient["full_name"])
            pphone = st.text_input("Phone Number", value=patient["phone"])
            pemail = st.text_input("Email Address", value=patient["email"])
            paddress = st.text_area("Address", value=patient["address"])
            pemerg = st.text_input("Emergency Contact", value=patient["emergency_contact"])

            btn_p_save = st.form_submit_button("Save Profile Changes", type="primary")
            if btn_p_save:
                up_p = {
                    "full_name": pfname, "gender": patient["gender"], "date_of_birth": patient["date_of_birth"],
                    "phone": pphone, "email": pemail, "address": paddress,
                    "blood_group": patient["blood_group"], "disease_problem": patient["disease_problem"],
                    "emergency_contact": pemerg, "status": patient["status"]
                }
                ok, err = update_patient(patient_id, up_p)
                if ok:
                    st.success("Profile updated successfully!")
                    st.rerun()
                else:
                    st.error(err)

# --- MAIN CONTROLLER & SIDEBAR ROUTING ---
def main():
    user = st.session_state.get("user")

    if not user:
        render_login_page()
        return

    # Sidebar Header & User Profile Info
    st.sidebar.markdown(f"### 🏥 HealthCare+")
    st.sidebar.caption(f"Logged in as **{user['username']}** ({user['role'].upper()})")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state["user"] = None
        st.rerun()

    st.sidebar.divider()

    # Admin Sidebar Navigation
    if user["role"] == "admin":
        nav_choice = st.sidebar.radio(
            "Admin Navigation",
            ["📊 Dashboard", "👥 Patients", "👨‍⚕️ Doctors", "📅 Appointments", "💳 Billing", "📈 Reports", "⚙️ Settings"]
        )

        if nav_choice == "📊 Dashboard":
            render_admin_dashboard()
        elif nav_choice == "👥 Patients":
            render_admin_patients()
        elif nav_choice == "👨‍⚕️ Doctors":
            render_admin_doctors()
        elif nav_choice == "📅 Appointments":
            render_admin_appointments()
        elif nav_choice == "💳 Billing":
            render_admin_billing()
        elif nav_choice == "📈 Reports":
            render_admin_reports()
        elif nav_choice == "⚙️ Settings":
            render_admin_settings()

    # Patient Sidebar Navigation
    elif user["role"] == "patient":
        nav_choice = st.sidebar.radio(
            "Patient Navigation",
            ["🏠 Dashboard", "🔍 Find Doctor", "📅 Book Appointment", "📋 My Appointments", "🧾 My Bills", "👤 Profile"]
        )

        if nav_choice == "🏠 Dashboard":
            render_patient_dashboard()
        elif nav_choice == "🔍 Find Doctor":
            render_patient_find_doctor()
        elif nav_choice == "📅 Book Appointment":
            render_patient_book_appointment()
        elif nav_choice == "📋 My Appointments":
            render_patient_my_appointments()
        elif nav_choice == "🧾 My Bills":
            render_patient_my_bills()
        elif nav_choice == "👤 Profile":
            render_patient_profile()

if __name__ == "__main__":
    main()
