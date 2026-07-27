class Student:
    """
    Represents a student entity.
    Supports String IDs (e.g. 'ST001') and flexible optional attributes like email and phone.
    """
    def __init__(self, student_id: str, name: str, email: str = "", phone: str = ""):
        self.student_id = str(student_id).strip()
        self.name = str(name).strip()
        self.email = str(email).strip()
        self.phone = str(phone).strip()

    def to_dict(self) -> dict:
        """Converts the student object to a dictionary for JSON serialization."""
        return {
            "Student ID": self.student_id,
            "Student Name": self.name,
            "Email": self.email,
            "Phone": self.phone
        }

    def show_info(self):
        print(f"ID   : {self.student_id}")
        print(f"Name : {self.name}")
        if self.email:
            print(f"Email: {self.email}")
        if self.phone:
            print(f"Phone: {self.phone}")

    def __repr__(self):
        return f"Student(student_id='{self.student_id}', name='{self.name}')"


class Course:
    """
    Represents an academic course entity.
    Supports String IDs (e.g. 'CS101', 'AI001').
    """
    def __init__(self, course_id: str, course_name: str, description: str = ""):
        self.course_id = str(course_id).strip()
        self.course_name = str(course_name).strip()
        self.description = str(description).strip()

    def to_dict(self) -> dict:
        """Converts the course object to a dictionary for JSON serialization."""
        return {
            "Course ID": self.course_id,
            "Course Name": self.course_name,
            "Description": self.description
        }

    def show_info(self):
        print(f"Course ID   : {self.course_id}")
        print(f"Course Name : {self.course_name}")
        if self.description:
            print(f"Description : {self.description}")

    def __repr__(self):
        return f"Course(course_id='{self.course_id}', course_name='{self.course_name}')"


class Enrollment:
    """
    Represents the enrollment relationship between a Student and a Course.
    """
    def __init__(self, student: Student, course: Course, enrollment_date: str = ""):
        self.student = student
        self.course = course
        self.enrollment_date = enrollment_date

    def to_dict(self) -> dict:
        """Converts the enrollment record to a dictionary."""
        return {
            "Student ID": self.student.student_id,
            "Student Name": self.student.name,
            "Course ID": self.course.course_id,
            "Course Name": self.course.course_name,
            "Enrollment Date": self.enrollment_date
        }

    def show_info(self):
        print(f"Student : {self.student.name} ({self.student.student_id})")
        print(f"Course  : {self.course.course_name} ({self.course.course_id})")

    def __repr__(self):
        return f"Enrollment(Student='{self.student.student_id}', Course='{self.course.course_id}')"