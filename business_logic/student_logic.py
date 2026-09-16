from langchain_core.tools import tool
from typing import Optional, Literal
import requests

# RENDER STUDENT MANAGEMENT API

BASE_URL = "https://student-management-d2uq.onrender.com"

#LIST STUDENTS

@tool
def list_students() -> str:
    """
    Get all students from the student management API.
    Returns:
        Student records returned by the API, or an error message if
        the request fails.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/students",
            timeout=60
        )
        response.raise_for_status()
        return response.text

    except requests.exceptions.RequestException as e:
        return f"Unable to retrieve students: {e}"

    
#register a student
@tool
def register_student(
    id: int,
    name: str,
    email: str,
    department: str,
    year: int
) -> str:
    """
    Register a new student using the student ID, name, email,
    department and year.
    """

    student_data = {
        "id": id,
        "name": name,
        "email": email,
        "department": department,
        "year": year
    }

    try:
        print("Request:", student_data)

        response = requests.post(
            f"{BASE_URL}/",
            json=student_data,
            timeout=60
        )

        print("Status:", response.status_code)
        print("Response:", response.text)

        response.raise_for_status()

        return response.text

    except requests.exceptions.RequestException as e:
        return f"Unable to register student: {e}"
        
@tool
#get a student
def get_student(student_id: int)-> str:
        """
        get the student details by using the student ID
        args:
        student_id : student ID required by the API
        returns:
        details of the stduents
        """
        try:
            response = requests.get(
                f"{BASE_URL}/students/{student_id}",
                        timeout=60
                    )
            if response.status_code ==200:
                return response.text
            return f"student not found. status code : {response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"can't able to register student: {e}"



#UPDATE STUDENT
@tool
def update_student(
    student_id: int,
    name: str,
    email: str,
    year: int,
    department: str
) -> str:
    """
    Update an existing student's details.

    Args:
        student_id: Student ID.
        name: Student name.
        email: Student email.
        year: Year of passing.
        department: Student department.
    """

    student_data = {
        "id": student_id,
        "name": name,
        "email": email,
        "year": year,
        "department": department
    }

    try:
        response = requests.put(
            f"{BASE_URL}/students/{student_id}",
            params={"student_id": student_id},
            json=student_data,
            timeout=60
        )

        if not response.ok:
            return f"ERROR {response.status_code}: {response.text}"

        return response.text

    except requests.exceptions.RequestException as e:
        return f"Error updating student: {e}"
          

# delete student

@tool
def delete_student(student_id: int) -> str:
    """
    Delete an existing student.

    Args:
        student_id: The ID of the student to delete.

    Returns:
        The result of the delete operation.
    """

    if student_id is None:
        return "Error: student_id is required."

    try:
        response = requests.delete(
            f"{BASE_URL}/students/{student_id}",
            timeout=60
        )

        if not response.ok:
            return f"ERROR {response.status_code}: {response.text}"

        return response.text

    except requests.exceptions.RequestException as e:
        return f"Error deleting student: {e}"

    

#Get the courses
@tool
def list_courses() -> str:
    """
    Get the list of all available courses.

    Returns:
        The list of courses.
    """

    try:
        response = requests.get(
            f"{BASE_URL}/courses",
            timeout=60
        )
        if not response.ok:
            return f"ERROR {response.status_code}: {response.text}"

        return response.text
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching courses: {e}"
    
#create a course
@tool
def create_course(
    code: str,
    name: str,
    max_seats: int,
    subject_name: str
) -> str:
    """
    Create a new course.

    Args:
        code: Course code.
        name: Course name.
        max_seats: Maximum number of students allowed.
        subject_name: Subject name.
    """

    course_data = {
        "code": code,
        "name": name,
        "max_seats": max_seats,
        "subject_name": subject_name
    }

    try:
        response = requests.post(
            f"{BASE_URL}/courses",
            json=course_data,
            timeout=60
        )

        if not response.ok:
            return f"ERROR {response.status_code}: {response.text}"

        return response.text

    except requests.exceptions.RequestException as e:
        return f"Error creating course: {e}"

#ENROLL A STUDENT
  
@tool
def enroll_student(student_id: int, course_id: int):
    """
    Enroll a student into a course.

    Use this tool when the user wants to enroll/register a student
    for a course.

    Examples:
    - "Enroll student 5 in course 2"
    - "Register student 10 for course 3"
    """
    try:
        response = requests.post(
            f"{BASE_URL}/students/{student_id}/enroll/{course_id}",
            timeout=60
        )

        if response.status_code == 200:
            return response.json()

        return f"Enrollment failed. Status code: {response.status_code}. Response: {response.text}"

    except requests.exceptions.RequestException as e:
        return f"Error connecting to Student API: {str(e)}"

  #Add marks for the student  
    
@tool
def add_marks(student_id: int, subject_name: str, marks: float):
    """
    Add marks for a student.

    Args:
        student_id: ID of the student.
        subject_name: Name of the subject or course.
        marks: Marks obtained by the student.
    """

    marks_data = {
        "subject_name": subject_name,
        "marks": marks
    }

    try:
        response = requests.post(
            f"{BASE_URL}/students/{student_id}/marks",
            json=marks_data,
            timeout=60
        )

        if response.status_code in [200, 201]:
            return response.json()

        return {
            "success": False,
            "status_code": response.status_code,
            "message": response.text
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"Student API connection error: {str(e)}"
        }
  
  #get the result for the student 
@tool
def get_result(student_id: int):
    """
    Get the academic result of a student.

    Args:
        student_id: ID of the student whose result is required.

    Examples:
        "Get the result of student 5"
        "Show student 10's result"
        "What are the marks and result of student 3?"
    """

    try:
        response = requests.get(
            f"{BASE_URL}/students/{student_id}/result",
            timeout=60
        )

        if response.status_code == 200:
            return response.json()

        return {
            "success": False,
            "status_code": response.status_code,
            "message": response.text
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"Student API connection error: {str(e)}"
        }

