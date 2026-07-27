import streamlit as st
import pandas as pd
from student_management import StudentManagementSystem
from charts import DashboardAnalytics

# 1. Streamlit Page Configuration
st.set_page_config(
    page_title="Student Management System V2",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .student-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)


# 2. Initialize System Instance in Session State
@st.cache_resource
def get_system_instance():
    system = StudentManagementSystem("students_data.json")
    system.load_data()
    return system


sms = get_system_instance()
analytics = DashboardAnalytics(sms)


# 3. Sidebar Navigation
st.sidebar.title("📌 Menu")
page = st.sidebar.radio(
    "Go to:",
    ["📊 Dashboard & Analytics", "👨‍🎓 Students Management", "📚 Courses Management", "📝 Enrollments"]
)

st.sidebar.markdown("---")
if st.sidebar.button("💾 Force Save Data"):
    sms.save_data()
    st.sidebar.success("Data Saved Successfully!")

# ==================================================
# PAGE 1: Dashboard & Analytics
# ==================================================
if page == "📊 Dashboard & Analytics":
    st.title("🎓 Student Management System - Dashboard V2")
    st.markdown("---")

    # Top Metrics Bar
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric("Total Students 👨‍🎓", sms.total_students())
    with m_col2:
        st.metric("Total Courses 📚", sms.total_courses())
    with m_col3:
        st.metric("Total Enrollments 📝", sms.total_enrollments())

    st.markdown("---")

    # Secondary Metrics (Advanced Analytics)
    metrics = analytics.get_summary_metrics()
    sub_col1, sub_col2, sub_col3 = st.columns(3)
    with sub_col1:
        st.metric("🔥 Most Popular Course", metrics["most_popular"])
    with sub_col2:
        st.metric("🧊 Least Popular Course", metrics["least_popular"])
    with sub_col3:
        st.metric("📊 Avg Courses / Student", metrics["avg_courses_per_student"])

    st.markdown("---")

    # Interactive Charts Area
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(analytics.create_pie_chart(), use_container_width=True)
    with chart_col2:
        st.plotly_chart(analytics.create_bar_chart(), use_container_width=True)

    st.plotly_chart(analytics.create_line_chart(), use_container_width=True)

    st.markdown("---")

    # Quick Student Inspector / Search Statistics
    st.subheader("🔍 Quick Student Inspector & Details")
    search_query = st.text_input("Enter Student ID or Name (e.g., ST001 or Mostafa):", "")

    if search_query:
        details = sms.get_student_details(search_query)
        if details:
            st.success("Student Found!")
            st.markdown(f"""
            <div class="student-card">
                <h3>🆔 Student Details: {details['name']}</h3>
                <p><b>Student ID:</b> {details['student_id']}</p>
                <p><b>Email:</b> {details['email'] if details['email'] else 'N/A'}</p>
                <p><b>Phone:</b> {details['phone'] if details['phone'] else 'N/A'}</p>
                <p><b>Total Registered Courses:</b> {details['total_courses']}</p>
            </div>
            """, unsafe_allow_html=True)

            if details["courses"]:
                st.write("**Registered Courses List:**")
                for c_name in details["courses"]:
                    st.markdown(f"✔ **{c_name}**")
            else:
                st.info("This student is not registered in any courses yet.")
        else:
            st.warning("No student found matching your query.")

    st.markdown("---")

    # Data Tables Summary
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        st.subheader("👨‍🎓 All Students")
        st.dataframe(pd.DataFrame(sms.student_table()), use_container_width=True)
    with t_col2:
        st.subheader("📚 All Courses")
        st.dataframe(pd.DataFrame(sms.course_table()), use_container_width=True)


# ==================================================
# PAGE 2: Students Management
# ==================================================
elif page == "👨‍🎓 Students Management":
    st.title("👨‍🎓 Students Management")

    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search & List", "➕ Add Student", "✏️ Update Student", "❌ Delete Student"])

    # Tab 1: Search & Details
    with tab1:
        st.subheader("Search Students")
        q = st.text_input("Filter by ID or Name:", "")
        filtered_students = sms.search_students(q)
        if filtered_students:
            df = pd.DataFrame([s.to_dict() for s in filtered_students])
            st.dataframe(df, use_container_width=True)

            selected_id = st.selectbox("Select a Student to View Full Details:", [s.student_id for s in filtered_students])
            if selected_id:
                details = sms.get_student_details(selected_id)
                if details:
                    st.info(f"**ID:** {details['student_id']} | **Name:** {details['name']} | **Email:** {details['email']} | **Phone:** {details['phone']}")
                    st.write(f"**Enrollment Count:** {details['total_courses']}")
                    st.write("**Enrolled Courses:**", ", ".join(details["courses"]) if details["courses"] else "None")
        else:
            st.warning("No students found.")

    # Tab 2: Add Student
    with tab2:
        st.subheader("Add New Student")
        with st.form("add_student_form", clear_on_submit=True):
            sid = st.text_input("Student ID (e.g. ST001):")
            name = st.text_input("Full Name:")
            email = st.text_input("Email (Optional):")
            phone = st.text_input("Phone (Optional):")
            submitted = st.form_submit_button("Add Student")

            if submitted:
                if sid and name:
                    if sms.add_student(student_id=sid, name=name, email=email, phone=phone):
                        st.success(f"Student '{name}' ({sid}) added successfully!")
                        st.rerun()
                    else:
                        st.error(f"Student ID '{sid}' already exists.")
                else:
                    st.error("Please fill in required fields (Student ID & Name).")

    # Tab 3: Update Student
    with tab3:
        st.subheader("Update Student Info")
        all_students = sms.students
        if all_students:
            student_to_update = st.selectbox("Select Student to Edit:", [f"{s.student_id} - {s.name}" for s in all_students])
            selected_id = student_to_update.split(" - ")[0]
            current_s = sms.find_student(selected_id)

            if current_s:
                new_name = st.text_input("New Name:", value=current_s.name)
                new_email = st.text_input("New Email:", value=current_s.email)
                new_phone = st.text_input("New Phone:", value=current_s.phone)

                if st.button("Update Student Details"):
                    if sms.update_student(selected_id, new_name, new_email, new_phone):
                        st.success("Student details updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update student.")
        else:
            st.info("No students available to update.")

    # Tab 4: Delete Student
    with tab4:
        st.subheader("Delete Student")
        all_students = sms.students
        if all_students:
            student_to_delete = st.selectbox("Select Student to Delete:", [f"{s.student_id} - {s.name}" for s in all_students], key="del_s")
            selected_id = student_to_delete.split(" - ")[0]

            if st.button("⚠️ Confirm Delete Student", type="primary"):
                if sms.delete_student(selected_id):
                    st.success("Student and associated enrollments deleted successfully!")
                    st.rerun()
                else:
                    st.error("Delete failed.")
        else:
            st.info("No students available to delete.")


# ==================================================
# PAGE 3: Courses Management
# ==================================================
elif page == "📚 Courses Management":
    st.title("📚 Courses Management")

    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search & List", "➕ Add Course", "✏️ Update Course", "❌ Delete Course"])

    # Tab 1: Search Courses
    with tab1:
        st.subheader("Search Courses")
        q = st.text_input("Filter by Course ID or Name:", "")
        filtered_courses = sms.search_courses(q)
        if filtered_courses:
            df = pd.DataFrame([c.to_dict() for c in filtered_courses])
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No courses found.")

    # Tab 2: Add Course
    with tab2:
        st.subheader("Add New Course")
        with st.form("add_course_form", clear_on_submit=True):
            cid = st.text_input("Course ID (e.g. AI001, CS101):")
            cname = st.text_input("Course Name:")
            desc = st.text_area("Description (Optional):")
            submitted = st.form_submit_button("Add Course")

            if submitted:
                if cid and cname:
                    if sms.add_course(course_id=cid, course_name=cname, description=desc):
                        st.success(f"Course '{cname}' ({cid}) added successfully!")
                        st.rerun()
                    else:
                        st.error(f"Course ID '{cid}' already exists.")
                else:
                    st.error("Please fill in required fields (Course ID & Name).")

    # Tab 3: Update Course
    with tab3:
        st.subheader("Update Course Info")
        all_courses = sms.courses
        if all_courses:
            course_to_update = st.selectbox("Select Course to Edit:", [f"{c.course_id} - {c.course_name}" for c in all_courses])
            selected_id = course_to_update.split(" - ")[0]
            current_c = sms.find_course(selected_id)

            if current_c:
                new_cname = st.text_input("New Course Name:", value=current_c.course_name)
                new_desc = st.text_area("New Description:", value=current_c.description)

                if st.button("Update Course Details"):
                    if sms.update_course(selected_id, new_cname, new_desc):
                        st.success("Course details updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update course.")
        else:
            st.info("No courses available to update.")

    # Tab 4: Delete Course
    with tab4:
        st.subheader("Delete Course")
        all_courses = sms.courses
        if all_courses:
            course_to_delete = st.selectbox("Select Course to Delete:", [f"{c.course_id} - {c.course_name}" for c in all_courses], key="del_c")
            selected_id = course_to_delete.split(" - ")[0]

            if st.button("⚠️ Confirm Delete Course", type="primary"):
                if sms.delete_course(selected_id):
                    st.success("Course and associated enrollments deleted successfully!")
                    st.rerun()
                else:
                    st.error("Delete failed.")
        else:
            st.info("No courses available to delete.")


# ==================================================
# PAGE 4: Enrollments
# ==================================================
elif page == "📝 Enrollments":
    st.title("📝 Student Enrollments")

    tab1, tab2, tab3 = st.tabs(["📋 All Enrollments", "➕ Register Student", "❌ Remove Enrollment"])

    # Tab 1: List Enrollments
    with tab1:
        st.subheader("Current Enrollments Record")
        e_data = sms.enrollment_table()
        if e_data:
            st.dataframe(pd.DataFrame(e_data), use_container_width=True)
        else:
            st.info("No enrollments recorded yet.")

    # Tab 2: Register Student in Course
    with tab2:
        st.subheader("Register Student to Course")
        if sms.students and sms.courses:
            selected_student_str = st.selectbox(
                "Select Student:",
                [f"{s.student_id} - {s.name}" for s in sms.students]
            )
            selected_course_str = st.selectbox(
                "Select Course:",
                [f"{c.course_id} - {c.course_name}" for c in sms.courses]
            )

            student_id = selected_student_str.split(" - ")[0]
            course_id = selected_course_str.split(" - ")[0]

            if st.button("Register Student"):
                if sms.enroll_student(student_id, course_id):
                    st.success(f"Successfully enrolled Student ({student_id}) into Course ({course_id})!")
                    st.rerun()
                else:
                    st.warning("Enrollment failed. Either student is already enrolled in this course or invalid data.")
        else:
            st.warning("You need at least one student and one course to make an enrollment.")

    # Tab 3: Remove Enrollment
    with tab3:
        st.subheader("Remove Student Enrollment")
        e_data = sms.enrollments
        if e_data:
            enrollment_options = [f"{e.student.student_id} ({e.student.name}) ➔ {e.course.course_id} ({e.course.course_name})" for e in e_data]
            selected_e = st.selectbox("Select Enrollment to Remove:", enrollment_options)

            if st.button("Remove Selected Enrollment"):
                # Extract Student ID and Course ID
                part_student = selected_e.split(" ➔ ")[0]
                part_course = selected_e.split(" ➔ ")[1]

                sid = part_student.split(" (")[0]
                cid = part_course.split(" (")[0]

                if sms.remove_enrollment(sid, cid):
                    st.success("Enrollment removed successfully!")
                    st.rerun()
                else:
                    st.error("Failed to remove enrollment.")
        else:
            st.info("No enrollments available to remove.")