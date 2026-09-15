import sqlite3
import tkinter as tk
import tkinter.messagebox
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# =========================
# LOAD & TRAIN MODEL
# =========================
base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

csv_path = os.path.join(base_path, 'data', 'student-mat.csv')
df = pd.read_csv(csv_path, sep=";")

X = df[['studytime', 'absences', 'G1', 'G2']]
y = df['G3']

model = LinearRegression()
model.fit(X, y)

print("Model trained successfully")

# =========================
# DATABASE SETUP
# =========================
os.makedirs(os.path.join(base_path, "data"), exist_ok=True)

db_real_path = (
    os.path.join(os.path.dirname(sys.executable), "taralytix.db")
    if getattr(sys, 'frozen', False)
    else os.path.join(base_path, "data", "taralytix.db")
)

connection = sqlite3.connect(db_real_path)
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Students (
    student_id TEXT PRIMARY KEY,
    full_name TEXT,
    email TEXT,
    password TEXT,
    course TEXT,
    year_of_study INTEGER,
    semester INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Academic_Records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    course_code TEXT,
    course_name TEXT,
    attendance_percentage REAL,
    cat_mark REAL,
    assignment_mark REAL,
    exam_mark REAL,
    total_mark REAL,
    grade TEXT,
    semester INTEGER
)
""")

connection.commit()

# =========================
# MAIN WINDOW
# =========================
root = tk.Tk()
root.title("Taralytix")
root.geometry("800x550")
root.configure(bg="#1e1e2f")

main_frame = tk.Frame(root, bg="#1e1e2f")
main_frame.pack(fill="both", expand=True)

# =========================
# UTILITIES
# =========================
def clear_main():
    for widget in main_frame.winfo_children():
        widget.destroy()

def get_selected_semester_value(semester_var):
    try:
        return int(semester_var.get())
    except ValueError:
        return None

# =========================
# DASHBOARD
# =========================
def load_dashboard(student_data):
    clear_main()

    dashboard = tk.Frame(main_frame, bg="#3b3b98")
    dashboard.pack(fill="both", expand=True)

    sidebar = tk.Frame(dashboard, bg="#111827", width=200)
    sidebar.pack(side="left", fill="y")

    content = tk.Frame(dashboard, bg="#1e1e2f")
    content.pack(side="right", fill="both", expand=True)

    def clear_content():
        for widget in content.winfo_children():
            widget.destroy()

    def semester_selector(parent, title="Select Semester"):
        tk.Label(parent, text=title, bg="#1e1e2f", fg="white",
                 font=("Arial", 11, "bold")).pack(pady=(10, 5))

        semester_var = tk.StringVar()
        current_sem = student_data[6] if student_data[6] else 1
        semester_var.set(str(current_sem))

        semester_menu = tk.OptionMenu(parent, semester_var, "1", "2", "3")
        semester_menu.config(bg="#007bff", fg="white", width=10)
        semester_menu["menu"].config(bg="white", fg="black")
        semester_menu.pack(pady=5)

        return semester_var

    # =========================
    # PAGES
    # =========================
    def show_home():
        clear_content()

        tk.Label(content, text=f"Welcome, {student_data[1]}",
                 font=("Arial", 16, "bold"),
                 bg="#1e1e2f", fg="white").pack(pady=20)

        tk.Label(content,
                 text=f"{student_data[4]} | Year {student_data[5]} | Current Semester {student_data[6]}",
                 bg="#1e1e2f", fg="white", font=("Arial", 11)).pack()

        tk.Label(content,
                 text="Use the menu on the left to enter semester records, view records, and analyze performance.",
                 bg="#1e1e2f", fg="white", wraplength=500).pack(pady=20)

    def show_records():
        clear_content()

        tk.Label(content, text="View Records",
                 font=("Arial", 16, "bold"),
                 bg="#1e1e2f", fg="white").pack(pady=10)

        semester_var = semester_selector(content)

        records_frame = tk.Frame(content, bg="#1e1e2f")
        records_frame.pack(fill="both", expand=True, pady=10)

        def load_records():
            for widget in records_frame.winfo_children():
                widget.destroy()

            selected_semester = get_selected_semester_value(semester_var)
            if selected_semester is None:
                tk.Label(records_frame, text="Invalid semester selected",
                         bg="#1e1e2f", fg="red").pack()
                return

            tk.Label(records_frame,
                     text=f"Records for Semester {selected_semester}",
                     font=("Arial", 12, "bold"),
                     bg="#1e1e2f", fg="white").pack(pady=5)

            cursor.execute("""
                SELECT course_code, course_name, attendance_percentage,
                       cat_mark, assignment_mark, exam_mark, total_mark, grade
                FROM Academic_Records
                WHERE student_id = ? AND semester = ?
                ORDER BY course_code
            """, (student_data[0], selected_semester))

            records = cursor.fetchall()

            if not records:
                tk.Label(records_frame, text="No records found for this semester",
                         bg="#1e1e2f", fg="white").pack(pady=10)
                return

            header = tk.Frame(records_frame, bg="#1e1e2f")
            header.pack(pady=5)

            headings = ["Code", "Course", "Attendance", "CAT", "Assignment", "Exam", "Total", "Grade"]
            widths = [10, 18, 12, 8, 12, 8, 8, 8]

            for h, w in zip(headings, widths):
                tk.Label(header, text=h, width=w, bg="#111827", fg="white",
                         font=("Arial", 9, "bold")).pack(side="left", padx=1)

            for r in records:
                row = tk.Frame(records_frame, bg="#1e1e2f")
                row.pack(pady=2)

                values = [
                    r[0], r[1], f"{r[2]}%", r[3], r[4], r[5], r[6], r[7]
                ]

                for val, w in zip(values, widths):
                    tk.Label(row, text=str(val), width=w, bg="#2d2d44", fg="white").pack(side="left", padx=1)

        tk.Button(content, text="Load Records",
                  bg="#007bff", fg="white",
                  command=load_records).pack(pady=10)

    def show_analytics():
        clear_content()

        tk.Label(content, text="Analytics Dashboard",
                 font=("Arial", 16, "bold"),
                 bg="#1e1e2f", fg="white").pack(pady=10)

        semester_var = semester_selector(content)

        analytics_frame = tk.Frame(content, bg="#1e1e2f")
        analytics_frame.pack(fill="both", expand=True, pady=10)

        def load_analytics():
            for widget in analytics_frame.winfo_children():
                widget.destroy()

            selected_semester = get_selected_semester_value(semester_var)
            if selected_semester is None:
                tk.Label(analytics_frame, text="Invalid semester selected",
                         bg="#1e1e2f", fg="red").pack()
                return

            cursor.execute("""
                SELECT course_name, total_mark, attendance_percentage,
                       cat_mark, assignment_mark, exam_mark
                FROM Academic_Records
                WHERE student_id = ? AND semester = ?
                ORDER BY course_name
            """, (student_data[0], selected_semester))

            data = cursor.fetchall()

            if not data:
                tk.Label(analytics_frame, text="No data available for this semester",
                         bg="#1e1e2f", fg="white").pack()
                return

            courses = [d[0] for d in data]
            marks = [d[1] for d in data]
            attendance = [d[2] for d in data]
            cat_marks = [d[3] for d in data]
            assignment_marks = [d[4] for d in data]
            exam_marks = [d[5] for d in data]

            avg = round(sum(marks) / len(marks), 2)
            highest = max(marks)
            lowest = min(marks)

            avg_attendance = round(sum(attendance) / len(attendance), 2)
            avg_cat = round(sum(cat_marks) / len(cat_marks), 2)
            avg_assignment = round(sum(assignment_marks) / len(assignment_marks), 2)
            avg_exam = round(sum(exam_marks) / len(exam_marks), 2)

            color = "red" if avg < 50 else "orange" if avg < 60 else "yellow" if avg < 70 else "green"

            tk.Label(analytics_frame, text=f"Semester {selected_semester} Analysis",
                     font=("Arial", 13, "bold"),
                     bg="#1e1e2f", fg="white").pack(pady=5)

            tk.Label(analytics_frame, text=f"Average Score: {avg}",
                     fg=color, bg="#1e1e2f",
                     font=("Arial", 13, "bold")).pack(pady=5)

            tk.Label(analytics_frame, text=f"Highest Score: {highest}",
                     bg="#1e1e2f", fg="white").pack()

            tk.Label(analytics_frame, text=f"Lowest Score: {lowest}",
                     bg="#1e1e2f", fg="white").pack()

            tk.Label(analytics_frame, text=f"Average Attendance: {avg_attendance}%",
                     bg="#1e1e2f", fg="white").pack(pady=5)

            tk.Label(analytics_frame, text="Performance Breakdown",
                     font=("Arial", 13, "bold"),
                     bg="#1e1e2f", fg="white").pack(pady=10)

            tk.Label(analytics_frame, text=f"CAT Average: {avg_cat}",
                     bg="#1e1e2f", fg="white").pack()

            tk.Label(analytics_frame, text=f"Assignment Average: {avg_assignment}",
                     bg="#1e1e2f", fg="white").pack()

            tk.Label(analytics_frame, text=f"Exam Average: {avg_exam}",
                     bg="#1e1e2f", fg="white").pack()

            tk.Label(analytics_frame, text="Insights",
                     font=("Arial", 13, "bold"),
                     bg="#1e1e2f", fg="white").pack(pady=10)

            if avg_exam < avg_cat:
                insight = "Your exam performance is lower than your CATs. Focus more on final exam preparation."
            elif avg_assignment < avg_cat:
                insight = "Assignments are pulling your grade down. Improve consistency in coursework."
            elif avg_attendance < 60:
                insight = "Low attendance is affecting your performance."
            else:
                insight = "Your performance is balanced across all areas."

            tk.Label(analytics_frame, text=insight,
                     wraplength=500,
                     bg="#1e1e2f", fg="white").pack(pady=5)

            def show_graph():
                plt.figure(figsize=(8, 5))
                plt.bar(courses, marks)
                plt.title(f"Performance Trend - Semester {selected_semester}")
                plt.xlabel("Courses")
                plt.ylabel("Marks")
                plt.xticks(rotation=30, ha="right")
                plt.tight_layout()
                plt.show()

            tk.Button(analytics_frame,
                      text="Show Performance Graph",
                      bg="#007bff", fg="white",
                      command=show_graph).pack(pady=15)

        tk.Button(content, text="Load Analytics",
                  bg="#007bff", fg="white",
                  command=load_analytics).pack(pady=10)

    def show_entry():
        clear_content()

        tk.Label(content, text="Enter Academic Record",
                 font=("Arial", 16, "bold"),
                 bg="#1e1e2f", fg="white").pack(pady=10)

        entries = {}

        text_fields = ["Course Code", "Course Name", "Attendance", "CAT", "Assignment", "Exam"]

        for f in text_fields:
            tk.Label(content, text=f, bg="#1e1e2f", fg="white").pack()
            e = tk.Entry(content)
            e.pack(pady=2)
            entries[f] = e

        tk.Label(content, text="Semester", bg="#1e1e2f", fg="white").pack()
        semester_var = tk.StringVar()
        semester_var.set(str(student_data[6] if student_data[6] else 1))
        semester_menu = tk.OptionMenu(content, semester_var, "1", "2", "3")
        semester_menu.config(bg="#007bff", fg="white", width=12)
        semester_menu["menu"].config(bg="white", fg="black")
        semester_menu.pack(pady=5)

        def save():
            try:
                course_code = entries["Course Code"].get().strip()
                course_name = entries["Course Name"].get().strip()
                attendance = float(entries["Attendance"].get())
                cat = float(entries["CAT"].get())
                assignment = float(entries["Assignment"].get())
                exam = float(entries["Exam"].get())
                semester = int(semester_var.get())

                if not course_code or not course_name:
                    tkinter.messagebox.showerror("Error", "Course Code and Course Name are required")
                    return

                total = cat + assignment + exam

                pred = model.predict([[2, 100 - attendance, cat, assignment]])
                pred = round(pred[0], 2)

                grade = (
                    "A" if total >= 70 else
                    "B" if total >= 60 else
                    "C" if total >= 50 else
                    "D" if total >= 40 else
                    "F"
                )

                cursor.execute("""
                    INSERT INTO Academic_Records
                    (student_id, course_code, course_name, attendance_percentage,
                     cat_mark, assignment_mark, exam_mark, total_mark, grade, semester)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    student_data[0],
                    course_code,
                    course_name,
                    attendance,
                    cat,
                    assignment,
                    exam,
                    total,
                    grade,
                    semester
                ))

                # update current semester in Students table
                cursor.execute("""
                    UPDATE Students
                    SET semester = ?
                    WHERE student_id = ?
                """, (semester, student_data[0]))

                connection.commit()

                tkinter.messagebox.showinfo(
                    "Saved",
                    f"Record saved under Semester {semester}\nPredicted Score: {pred}\nGrade: {grade}"
                )

                # reload latest student data so dashboard shows updated semester
                cursor.execute("SELECT * FROM Students WHERE student_id = ?", (student_data[0],))
                updated_student = cursor.fetchone()
                load_dashboard(updated_student)

            except ValueError:
                tkinter.messagebox.showerror("Error", "Please enter valid numbers")
            except Exception as e:
                print("REAL ERROR:", e)
                tkinter.messagebox.showerror("Error", str(e))

        tk.Button(content, text="Save",
                  bg="#28a745", fg="white",
                  command=save).pack(pady=12)

    def show_report():
        clear_content()

        tk.Label(content, text="System Report",
                 font=("Arial", 16, "bold"),
                 bg="#1e1e2f", fg="white").pack(pady=10)

        semester_var = semester_selector(content)

        report_frame = tk.Frame(content, bg="#1e1e2f")
        report_frame.pack(fill="both", expand=True, pady=10)

        def load_report():
            for widget in report_frame.winfo_children():
                widget.destroy()

            selected_semester = get_selected_semester_value(semester_var)
            if selected_semester is None:
                tk.Label(report_frame, text="Invalid semester selected",
                         bg="#1e1e2f", fg="red").pack()
                return

            cursor.execute("""
                SELECT course_name, total_mark
                FROM Academic_Records
                WHERE student_id = ? AND semester = ?
                ORDER BY course_name
            """, (student_data[0], selected_semester))

            data = cursor.fetchall()

            if not data:
                tk.Label(report_frame, text="No data available for this semester",
                         bg="#1e1e2f", fg="white").pack()
                return

            courses = [d[0] for d in data]
            marks = [d[1] for d in data]

            avg = round(sum(marks) / len(marks), 2)

            if avg < 50:
                rec = "Needs serious improvement"
                color = "red"
                level = "Poor Performance"
            elif avg < 60:
                rec = "Below average"
                color = "orange"
                level = "Below Average"
            elif avg < 70:
                rec = "Fair performance"
                color = "yellow"
                level = "Average"
            else:
                rec = "Excellent"
                color = "green"
                level = "Excellent"

            tk.Label(report_frame, text=f"Semester {selected_semester} Performance Report",
                     font=("Arial", 14, "bold"),
                     bg="#1e1e2f", fg="white").pack(pady=10)

            tk.Label(report_frame, text=f"Average: {avg}",
                     fg=color, bg="#1e1e2f",
                     font=("Arial", 12, "bold")).pack()

            tk.Label(report_frame,
                     text="Performance Level:",
                     font=("Arial", 12, "bold"),
                     bg="#1e1e2f",
                     fg="white").pack(pady=5)

            tk.Label(report_frame,
                     text=level,
                     fg=color,
                     bg="#1e1e2f",
                     font=("Arial", 12)).pack()

            tk.Label(report_frame, text=rec,
                     bg="#1e1e2f", fg="white").pack(pady=10)

            tk.Label(report_frame,
                     text="System Interpretation:",
                     font=("Arial", 12, "bold"),
                     bg="#1e1e2f",
                     fg="white").pack(pady=10)

            interpretation = f"""
The system analyzed your performance across {len(marks)} course(s) in Semester {selected_semester}.
Your average score is {avg}, indicating a {level.lower()}.

Improving weaker areas will help boost your overall performance.
            """

            tk.Label(report_frame,
                     text=interpretation,
                     wraplength=500,
                     justify="left",
                     bg="#1e1e2f",
                     fg="white").pack(pady=5)

            def graph():
                plt.figure(figsize=(8, 5))
                plt.bar(courses, marks)
                plt.title(f"Performance Report Graph - Semester {selected_semester}")
                plt.xlabel("Courses")
                plt.ylabel("Marks")
                plt.xticks(rotation=30, ha="right")
                plt.tight_layout()
                plt.show()

            tk.Button(report_frame, text="Show Graph",
                      bg="#007bff", fg="white",
                      command=graph).pack(pady=10)

        tk.Button(content, text="Load Report",
                  bg="#007bff", fg="white",
                  command=load_report).pack(pady=10)

    # =========================
    # SIDEBAR
    # =========================
    def btn(txt, cmd):
        return tk.Button(sidebar, text=txt,
                         command=cmd,
                         bg="#111827", fg="white",
                         bd=0, width=20, anchor="w")

    btn("🏠 Dashboard", show_home).pack(pady=10)
    btn("📝 Enter Records", show_entry).pack(pady=10)
    btn("📊 View Records", show_records).pack(pady=10)
    btn("📈 Analytics", show_analytics).pack(pady=10)
    btn("📄 System Report", show_report).pack(pady=10)
    btn("🚪 Logout", show_home_screen).pack(pady=20)

    show_home()

# =========================
# LOGIN / REGISTER
# =========================
def open_login():
    clear_main()

    tk.Label(main_frame, text="Student ID", bg="#1e1e2f", fg="white").pack()
    id_entry = tk.Entry(main_frame)
    id_entry.pack()

    tk.Label(main_frame, text="Password", bg="#1e1e2f", fg="white").pack()
    pass_entry = tk.Entry(main_frame, show="*")
    pass_entry.pack()

    def login():
        student_id = id_entry.get().strip()
        password = pass_entry.get().strip()

        if not student_id or not password:
            tkinter.messagebox.showerror("Error", "Enter ID and password")
            return

        cursor.execute(
            "SELECT * FROM Students WHERE student_id=? AND password=?",
            (student_id, password)
        )

        user = cursor.fetchone()

        if user:
            load_dashboard(user)
        else:
            tkinter.messagebox.showerror("Error", "Invalid login")

    tk.Button(main_frame, text="Login",
              bg="#28a745", fg="white",
              command=login).pack(pady=10)

    tk.Button(main_frame,
              text="Back",
              bg="gray",
              fg="white",
              command=show_home_screen).pack(pady=5)

def open_register():
    clear_main()

    tk.Label(main_frame,
             text="Register",
             font=("Arial", 16, "bold"),
             bg="#1e1e2f",
             fg="white").pack(pady=20)

    entries = {}

    fields = ["Student ID", "Full Name", "Email", "Password", "Course", "Year", "Semester"]

    for field in fields:
        tk.Label(main_frame, text=field,
                 bg="#1e1e2f", fg="white").pack()

        entry = tk.Entry(main_frame)
        entry.pack(pady=2)

        entries[field] = entry

    def save():
        try:
            student_id = entries["Student ID"].get().strip()
            full_name = entries["Full Name"].get().strip()
            email = entries["Email"].get().strip()
            password = entries["Password"].get().strip()
            course = entries["Course"].get().strip()
            year = int(entries["Year"].get())
            semester = int(entries["Semester"].get())

            if not all([student_id, full_name, email, password, course]):
                tkinter.messagebox.showerror("Error", "All fields must be filled")
                return

            cursor.execute("""
                INSERT INTO Students VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (student_id, full_name, email, password, course, year, semester))
            connection.commit()

            tkinter.messagebox.showinfo("Success", "Registered successfully!")

            cursor.execute("SELECT * FROM Students WHERE student_id=?", (student_id,))
            student = cursor.fetchone()
            load_dashboard(student)

        except sqlite3.IntegrityError:
            tkinter.messagebox.showerror("Error", "Student ID already exists")

        except ValueError:
            tkinter.messagebox.showerror("Error", "Year and Semester must be numbers")

        except Exception as e:
            print("REAL ERROR:", e)
            tkinter.messagebox.showerror("Error", str(e))

    tk.Button(main_frame,
              text="Submit",
              bg="#007bff", fg="white",
              command=save).pack(pady=15)

    tk.Button(main_frame,
              text="Back",
              bg="gray", fg="white",
              command=show_home_screen).pack()

# =========================
# HOME SCREEN
# =========================
def show_home_screen():
    clear_main()

    tk.Label(main_frame, text="Welcome to Taralytix",
             font=("Arial", 18, "bold"),
             bg="#1e1e2f", fg="white").pack(pady=40)

    tk.Button(main_frame, text="Login",
              bg="#28a745", fg="white",
              command=open_login).pack(pady=10)

    tk.Button(main_frame, text="Register",
              bg="#007bff", fg="white",
              command=open_register).pack(pady=10)

show_home_screen()
root.mainloop()