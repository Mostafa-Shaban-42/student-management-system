import plotly.express as px
import pandas as pd
from student_management import StudentManagementSystem


class DashboardAnalytics:
    def __init__(self, system: StudentManagementSystem):
        self.system = system

    def _get_enrollments_df(self) -> pd.DataFrame:
        """Helper to create a DataFrame from current enrollments data."""
        enrollments_data = self.system.enrollment_table()
        if not enrollments_data:
            return pd.DataFrame(columns=["Student ID", "Student Name", "Course ID", "Course Name", "Enrollment Date"])
        return pd.DataFrame(enrollments_data)

    def get_summary_metrics(self) -> dict:
        """
        Calculates top-level analytics metrics:
        - Most Popular Course
        - Least Popular Course
        - Average Courses per Student
        """
        df = self._get_enrollments_df()

        if df.empty or self.system.total_students() == 0:
            return {
                "most_popular": "N/A",
                "least_popular": "N/A",
                "avg_courses_per_student": 0.0
            }

        # Course popularity counts
        course_counts = df["Course Name"].value_counts()
        most_popular = course_counts.index[0] if not course_counts.empty else "N/A"
        least_popular = course_counts.index[-1] if not course_counts.empty else "N/A"

        # Average courses per student
        total_students = self.system.total_students()
        avg_courses = round(len(df) / total_students, 2) if total_students > 0 else 0.0

        return {
            "most_popular": most_popular,
            "least_popular": least_popular,
            "avg_courses_per_student": avg_courses
        }

    def create_pie_chart(self):
        """Generates a Pie Chart for Enrollment Distribution across Courses."""
        df = self._get_enrollments_df()

        if df.empty:
            fig = px.pie(title="Enrollment Distribution (No Data Available)")
            return fig

        course_counts = df["Course Name"].value_counts().reset_index()
        course_counts.columns = ["Course Name", "Student Count"]

        fig = px.pie(
            course_counts,
            names="Course Name",
            values="Student Count",
            title="📊 Enrollment Distribution by Course",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(margin=dict(t=50, b=20, l=20, r=20))
        return fig

    def create_bar_chart(self):
        """Generates a Bar Chart showing Student Count Per Course."""
        df = self._get_enrollments_df()

        if df.empty:
            fig = px.bar(title="Students Per Course (No Data Available)")
            return fig

        course_counts = df["Course Name"].value_counts().reset_index()
        course_counts.columns = ["Course Name", "Student Count"]

        fig = px.bar(
            course_counts,
            x="Course Name",
            y="Student Count",
            title="📈 Students Per Course",
            color="Student Count",
            color_continuous_scale="Viridis",
            text="Student Count"
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            xaxis_title="Course Name",
            yaxis_title="Number of Students",
            margin=dict(t=50, b=20, l=20, r=20)
        )
        return fig

    def create_line_chart(self):
        """Generates a Line Chart showing Growth / Enrollment Trends Over Time."""
        df = self._get_enrollments_df()

        if df.empty or "Enrollment Date" not in df.columns or df["Enrollment Date"].isnull().all():
            fig = px.line(title="Enrollment Growth Over Time (No Data Available)")
            return fig

        # Group by date and calculate cumulative growth
        date_counts = df.groupby("Enrollment Date").size().reset_index(name="Daily Enrollments")
        date_counts = date_counts.sort_values("Enrollment Date")
        date_counts["Total Growth"] = date_counts["Daily Enrollments"].cumsum()

        fig = px.line(
            date_counts,
            x="Enrollment Date",
            y="Total Growth",
            title="📉 Cumulative Enrollment Growth",
            markers=True,
            line_shape="spline"
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Total Registrations",
            margin=dict(t=50, b=20, l=20, r=20)
        )
        return fig