import json
import os
from datetime import datetime
from models import Student, Course, Enrollment


class StudentManagementSystem:
    def __init__(self, data_file="students_data.json"):
        self.data_file = data_file
        self.students: list[Student] = []
        self.courses: list[Course] = []
        self.enrollments: list[Enrollment] = []

    # ==================================================
    # Helper / Search Methods
    # ==================================================

    def find_student(self, student_id: str) -> Student | None:
        """Finds a student by exact Student ID (case-insensitive)."""
        sid = str(student_id).strip().lower()
        return next((s for s in self.students if s.student_id.lower() == sid), None)

    def find_course(self, course_id: str) -> Course | None:
        """Finds a course by exact Course ID (case-insensitive)."""
        cid = str(course_id).strip().lower()
        return next((c for c in self.courses if c.course_id.lower() == cid), None)

    def search_students(self, query: str) -> list[Student]:
        """Smart search for students by partial ID or partial Name."""
        q = str(query).strip().lower()
        if not q:
            return self.students
        return [
            s for s in self.students
            if q in s.student_id.lower() or q in s.name.lower()
        ]

    def search_courses(self, query: str) -> list[Course]:
        """Smart search for courses by partial ID or partial Name."""
        q = str(query).strip().lower()
        if not q:
            return self.courses
        return [
            c for c in self.courses
            if q in c.course_id.lower() or q in c.course_name.lower()
        ]

    # ==================================================
    # Student Operations
    # ==================================================

    def add_student(self, student_id: str, name: str, email: str = "", phone: str = "") -> bool:
        """Adds a new student. Returns False if ID already exists."""
        student_id = str(student_id).strip()
        if self.find_student(student_id):
            return False

        student = Student(
            student_id=student_id,
            name=name,
            email=email,
            phone=phone
        )
        self.students.append(student)
        self.save_data()
        return True

    def update_student(self, student_id: str, new_name: str, new_email: str = "", new_phone: str = "") -> bool:
        """Updates student info. Returns False if student not found."""
        student = self.find_student(student_id)
        if not student:
            return False

        if new_name.strip():
            student.name = new_name.strip()
        student.email = new_email.strip()
        student.phone = new_phone.strip()

        self.save_data()
        return True

    def delete_student(self, student_id: str) -> bool:
        """Deletes a student and all associated enrollments."""
        student = self.find_student(student_id)
        if not student:
            return False

        self.students.remove(student)
        # Cascade delete enrollments
        sid = student.student_id.lower()
        self.enrollments = [
            e for e in self.enrollments
            if e.student.student_id.lower() != sid
        ]
        self.save_data()
        return True

    # ==================================================
    # Course Operations
    # ==================================================

    def add_course(self, course_id: str, course_name: str, description: str = "") -> bool:
        """Adds a new course. Returns False if ID already exists."""
        course_id = str(course_id).strip()
        if self.find_course(course_id):
            return False

        course = Course(
            course_id=course_id,
            course_name=course_name,
            description=description
        )
        self.courses.append(course)
        self.save_data()
        return True

    def update_course(self, course_id: str, new_name: str, new_description: str = "") -> bool:
        """Updates course info. Returns False if course not found."""
        course = self.find_course(course_id)
        if not course:
            return False

        if new_name.strip():
            course.course_name = new_name.strip()
        course.description = new_description.strip()

        self.save_data()
        return True

    def delete_course(self, course_id: str) -> bool:
        """Deletes a course and all associated enrollments."""
        course = self.find_course(course_id)
        if not course:
            return False

        self.courses.remove(course)
        # Cascade delete enrollments
        cid = course.course_id.lower()
        self.enrollments = [
            e for e in self.enrollments
            if e.course.course_id.lower() != cid
        ]
        self.save_data()
        return True

    # ==================================================
    # Enrollment Operations
    # ==================================================

    def enroll_student(self, student_id: str, course_id: str) -> bool:
        """
        Enrolls a student into a course.
        Prevents duplicate enrollments.
        Returns False if student/course doesn't exist or already enrolled.
        """
        student = self.find_student(student_id)
        course = self.find_course(course_id)

        if not student or not course:
            return False

        # Check duplicate
        sid = student.student_id.lower()
        cid = course.course_id.lower()
        for e in self.enrollments:
            if e.student.student_id.lower() == sid and e.course.course_id.lower() == cid:
                return False

        today_str = datetime.now().strftime("%Y-%m-%d")
        enrollment = Enrollment(student=student, course=course, enrollment_date=today_str)
        self.enrollments.append(enrollment)
        self.save_data()
        return True

    def remove_enrollment(self, student_id: str, course_id: str) -> bool:
        """Removes a specific enrollment record."""
        sid = str(student_id).strip().lower()
        cid = str(course_id).strip().lower()

        target = next(
            (e for e in self.enrollments
             if e.student.student_id.lower() == sid and e.course.course_id.lower() == cid),
            None
        )

        if not target:
            return False

        self.enrollments.remove(target)
        self.save_data()
        return True

    def get_student_courses(self, student_id: str) -> list[Course]:
        """Gets all courses enrolled by a specific student."""
        sid = str(student_id).strip().lower()
        return [
            e.course for e in self.enrollments
            if e.student.student_id.lower() == sid
        ]

    def get_student_details(self, query: str) -> dict | None:
        """
        Fetches full details card for a student using exact or smart search.
        Includes registered courses list and total enrollment count.
        """
        # First try exact match
        student = self.find_student(query)
        # If not exact, try smart search
        if not student:
            matches = self.search_students(query)
            if matches:
                student = matches[0]

        if not student:
            return None

        courses = self.get_student_courses(student.student_id)
        return {
            "student_id": student.student_id,
            "name": student.name,
            "email": student.email,
            "phone": student.phone,
            "courses": [c.course_name for c in courses],
            "course_ids": [c.course_id for c in courses],
            "total_courses": len(courses)
        }

    # ==================================================
    # Dashboard Statistics & Tables
    # ==================================================

    def total_students(self) -> int:
        return len(self.students)

    def total_courses(self) -> int:
        return len(self.courses)

    def total_enrollments(self) -> int:
        return len(self.enrollments)

    def dashboard_info(self) -> dict:
        return {
            "students": self.total_students(),
            "courses": self.total_courses(),
            "enrollments": self.total_enrollments()
        }

    def student_table(self) -> list[dict]:
        return [s.to_dict() for s in self.students]

    def course_table(self) -> list[dict]:
        return [c.to_dict() for c in self.courses]

    def enrollment_table(self) -> list[dict]:
        return [e.to_dict() for e in self.enrollments]

    # ==================================================
    # JSON Persistence (Auto Save & Auto Load)
    # ==================================================

    def save_data(self, file_name: str = None) -> bool:
        target_file = file_name or self.data_file
        data = {
            "students": self.student_table(),
            "courses": self.course_table(),
            "enrollments": self.enrollment_table()
        }
        try:
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False

    def load_data(self, file_name: str = None) -> bool:
        target_file = file_name or self.data_file
        if not os.path.exists(target_file):
            return False

        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.students.clear()
            self.courses.clear()
            self.enrollments.clear()

            # Load Students
            for item in data.get("students", []):
                self.students.append(
                    Student(
                        student_id=item["Student ID"],
                        name=item["Student Name"],
                        email=item.get("Email", ""),
                        phone=item.get("Phone", "")
                    )
                )

            # Load Courses
            for item in data.get("courses", []):
                self.courses.append(
                    Course(
                        course_id=item["Course ID"],
                        course_name=item["Course Name"],
                        description=item.get("Description", "")
                    )
                )

            # Load Enrollments
            for item in data.get("enrollments", []):
                student = self.find_student(item["Student ID"])
                course = self.find_course(item["Course ID"])
                if student and course:
                    self.enrollments.append(
                        Enrollment(
                            student=student,
                            course=course,
                            enrollment_date=item.get("Enrollment Date", "")
                        )
                    )

            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def clear_all_data(self) -> bool:
        """Resets system memory and updates data file."""
        self.students.clear()
        self.courses.clear()
        self.enrollments.clear()
        self.save_data()
        return True