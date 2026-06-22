#Caleb Alston
#CIS261
#VIBE Coding

"""Student record manager with file persistence, class statistics, and ESC exit support."""

from __future__ import annotations
import csv
import os
import sys
from typing import Dict, List

DATA_FILE = "students.csv"
GRADE_BOUNDS = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (0, "F"),
]


class Student:
    def __init__(self, student_id: str, first_name: str, last_name: str, scores: List[float]) -> None:
        self.student_id = student_id.strip()
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        self.scores = scores
        self.average_score = 0.0
        self.grade = "F"
        self.recalculate()

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def recalculate(self) -> None:
        self.average_score = sum(self.scores) / len(self.scores)
        for bound, grade in GRADE_BOUNDS:
            if self.average_score >= bound:
                self.grade = grade
                break

    def summary(self) -> str:
        return (
            f"Student ID: {self.student_id}\n"
            f"Name: {self.full_name()}\n"
            f"Test 1: {self.scores[0]:.2f}\n"
            f"Test 2: {self.scores[1]:.2f}\n"
            f"Test 3: {self.scores[2]:.2f}\n"
            f"Average: {self.average_score:.2f}\n"
            f"Grade: {self.grade}"
        )


def is_exit_command(value: str) -> bool:
    return value.strip().upper() == "ESC"


def load_students(file_path: str = DATA_FILE) -> Dict[str, Student]:
    students: Dict[str, Student] = {}
    if not os.path.exists(file_path):
        print(f"No data file found. Starting with an empty student list.")
        return students

    try:
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    scores = [float(row[f"test{i}"]) for i in range(1, 4)]
                    student = Student(
                        row["student_id"],
                        row["first_name"],
                        row["last_name"],
                        scores,
                    )
                    students[student.student_id] = student
                except (KeyError, ValueError) as error:
                    print(f"Skipping invalid record in file: {error}")
        print(f"Loaded {len(students)} student record(s) from '{file_path}'.")
    except (IOError, PermissionError) as error:
        print(f"Could not read student file: {error}")
    return students


def save_students(students: Dict[str, Student], file_path: str = DATA_FILE) -> None:
    try:
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["student_id", "first_name", "last_name", "test1", "test2", "test3"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for student in students.values():
                writer.writerow(
                    {
                        "student_id": student.student_id,
                        "first_name": student.first_name,
                        "last_name": student.last_name,
                        "test1": f"{student.scores[0]:.2f}",
                        "test2": f"{student.scores[1]:.2f}",
                        "test3": f"{student.scores[2]:.2f}",
                    }
                )
        print(f"Student records saved to '{file_path}'.")
    except (IOError, PermissionError) as error:
        print(f"Error saving student file: {error}")


def prompt_input(prompt: str) -> str:
    value = input(prompt).strip()
    if is_exit_command(value):
        print("ESC detected. Exiting program.")
        sys.exit(0)
    return value


def prompt_nonempty(prompt: str) -> str:
    while True:
        value = prompt_input(prompt)
        if value:
            return value
        print("Entry cannot be empty. Please try again or press ESC to exit.")


def prompt_float(prompt: str, min_value: float = 0.0, max_value: float = 100.0) -> float:
    while True:
        raw = prompt_input(prompt)
        try:
            value = float(raw)
            if value < min_value or value > max_value:
                print(f"Please enter a number between {min_value:.2f} and {max_value:.2f}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Enter a numeric value or press ESC to exit.")


def prompt_scores() -> List[float]:
    print("Enter three test scores for the student.")
    return [prompt_float(f"  Test {i} score (0-100): ") for i in range(1, 4)]


def prompt_student_id(students: Dict[str, Student]) -> str:
    while True:
        student_id = prompt_nonempty("Enter student ID: ")
        if student_id.lower() in (key.lower() for key in students):
            print("A student with this ID already exists. Please enter a different ID.")
            continue
        return student_id


def find_student(students: Dict[str, Student], query: str) -> Student | None:
    query_lower = query.strip().lower()
    for student in students.values():
        if student.student_id.lower() == query_lower:
            return student
        if student.full_name().lower() == query_lower:
            return student
    return None


def add_student(students: Dict[str, Student]) -> None:
    print("\nAdd a new student:")
    first_name = prompt_nonempty("First name: ")
    last_name = prompt_nonempty("Last name: ")
    student_id = prompt_student_id(students)
    scores = prompt_scores()
    student = Student(student_id, first_name, last_name, scores)
    students[student.student_id] = student
    print(f"Student '{student.full_name()}' with ID '{student.student_id}' added successfully.")


def update_scores(students: Dict[str, Student]) -> None:
    if not students:
        print("No students available. Add a student first.")
        return
    query = prompt_nonempty("Enter student name or ID to update: ")
    student = find_student(students, query)
    if not student:
        print(f"Student '{query}' not found.")
        return
    print(f"Updating scores for {student.full_name()} (ID: {student.student_id}).")
    test_number = 0
    while test_number not in {1, 2, 3}:
        raw = prompt_input("Enter test number to update (1-3): ")
        if raw.isdigit() and 1 <= int(raw) <= 3:
            test_number = int(raw)
        else:
            print("Please choose a valid test number between 1 and 3 or press ESC to exit.")
    new_score = prompt_float(f"Enter new score for Test {test_number} (0-100): ")
    student.scores[test_number - 1] = new_score
    student.recalculate()
    print(f"Updated Test {test_number} score for '{student.full_name()}' to {new_score:.2f}.")


def display_all(students: Dict[str, Student]) -> None:
    if not students:
        print("No student records found.")
        return
    print("\nStudent Records")
    print("---------------")
    for student in sorted(students.values(), key=lambda s: s.student_id.lower()):
        print(student.summary())
        print("---------------")
    display_class_statistics(students)


def display_single(students: Dict[str, Student]) -> None:
    if not students:
        print("No students available.")
        return
    query = prompt_nonempty("Enter student name or ID to view: ")
    student = find_student(students, query)
    if not student:
        print(f"Student '{query}' not found.")
        return
    print(student.summary())


def remove_student(students: Dict[str, Student]) -> None:
    if not students:
        print("No students available.")
        return
    query = prompt_nonempty("Enter student name or ID to remove: ")
    student = find_student(students, query)
    if not student:
        print(f"Student '{query}' not found.")
        return
    del students[student.student_id]
    print(f"Removed student '{student.full_name()}' with ID '{student.student_id}'.")


def display_class_statistics(students: Dict[str, Student]) -> None:
    if not students:
        print("No class statistics available.")
        return
    averages = [student.average_score for student in students.values()]
    all_scores = [score for student in students.values() for score in student.scores]
    highest = max(averages)
    lowest = min(averages)
    average_of_averages = sum(averages) / len(averages)
    class_average = sum(all_scores) / len(all_scores)
    print("\nClass Statistics")
    print("---------------")
    print(f"Highest average: {highest:.2f}")
    print(f"Lowest average: {lowest:.2f}")
    print(f"Average of student averages: {average_of_averages:.2f}")
    print(f"Class average: {class_average:.2f}")


def show_menu() -> None:
    print(
        "\nStudent Record Manager"
        "\n1. Add student"
        "\n2. Update student test scores"
        "\n3. View all students"
        "\n4. View single student"
        "\n5. Remove student"
        "\n6. Save student records"
        "\n7. Save and Quit"
        "\nPress ESC at any prompt to exit immediately."
    )


def menu_choice() -> int:
    while True:
        choice = prompt_input("Choose an option (1-7) or ESC to exit: ")
        if choice.isdigit() and 1 <= int(choice) <= 7:
            return int(choice)
        print("Please enter a number between 1 and 7, or press ESC to exit.")


def main() -> None:
    students = load_students()
    print("Welcome to the Student Record Manager.")

    while True:
        show_menu()
        choice = menu_choice()

        if choice == 1:
            add_student(students)
        elif choice == 2:
            update_scores(students)
        elif choice == 3:
            display_all(students)
        elif choice == 4:
            display_single(students)
        elif choice == 5:
            remove_student(students)
        elif choice == 6:
            save_students(students)
        elif choice == 7:
            save_students(students)
            print("Goodbye!")
            break


def run() -> None:
    students = load_students()
    print("Welcome to the Student Record Manager.")
    try:
        while True:
            show_menu()
            choice = menu_choice()

            if choice == 1:
                add_student(students)
            elif choice == 2:
                update_scores(students)
            elif choice == 3:
                display_all(students)
            elif choice == 4:
                display_single(students)
            elif choice == 5:
                remove_student(students)
            elif choice == 6:
                save_students(students)
            elif choice == 7:
                save_students(students)
                print("Goodbye!")
                break
    except SystemExit:
        print("Saving before exit...")
        save_students(students)
        raise


if __name__ == "__main__":
    run()
