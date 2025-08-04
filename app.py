from flask import Flask, render_template, request, redirect
import pandas as pd
import os
import openpyxl
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font
from flask import session, url_for, flash
import gspread

from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

app = Flask(__name__)

app.secret_key = '563596d88700bb183fbd9bc6b87c37ca'  # Needed for session management

GOOGLE_SHEET_ID = "1rPlfvW1V11Uevbe6KKpADvyI5HxFsfxISh9aQ9cxv_c"  # ⬅️ your sheet ID
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
client = gspread.authorize(creds)


FACULTY_SHEET = 'faculty'
COURSE_SHEET = 'courses'
CAPACITY_SHEET = 'ClassroomCapacity'


AREA_LIST = sorted([
    'Amonora','Aundh','Aundh And PCMC','Aundh and PCMC','Aundh and FC','Baner','Bavdhan','BT Kawade','BT Kawade road','FC','FC and Kothrud' ,'FC and Lloyds','Hadapsar','Hadapsar and Lloyds','Hinjewadi','Karve Nagar','Khadhi','Kothrud','Lloyds','Lloyds and Swargate','Magarpatta','Mundwa','NIBM road','Pashan','PCMC','PS','Shivajinagar','Sopan Baug','Vishrant Wadi,'
])
ZONE_LIST = sorted(['Aundh-PCMC-PS', 'FC-Kothrud-Katraj', 'Lloyds-Hadapsar'])
COURSE_LIST = sorted([
    'Foundation BASIC', 'Foundation ADVANCED', 'FOUNDATION ADAVANCED PLUS',
    'Foundation Accelerated', 'FOUNDATION SUMMER', 'Pre-Foundation Basic',
    'Pre - Foundation Advanced', 'PRE - FOUNDATION SUMMER'
])
DAY_LIST = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
BATCH_LIST = [
    "A26 Aundh Offline Champions (Wed 5:30 pm to 8:50 pm Sun 7:00 am to 10:20 am) [1st Floor classroom 1]",
    "A26 Aundh Offline COC (Tue 5:30 pm to 8:50 pm Fri 5:30 pm to 8:50 pm) [1st Floor classroom 2]",
    "A26 Aundh Offline Wizards (Thu 5:30 pm to 8:50 pm Sun 11:00 am to 2:20 pm) [2nd Floor Big]"
    "A26 Aundh Synergy COC + Champions (Wed 5:30 pm to 8:50 pm Sat 5:30 to 8:50 pm) [2nd Floor Big]"
    "A26 Completely Online Champions (Sat 6:00 pm to 9:20 pm Sun 6:00 pm to 9:20 pm)",
    "A26 Completely Online COC - 1 (Fri 6:00 pm to 9:20 pm Sun 6:00 pm to 9:20 pm)",
    "A26 Completely Online COC - 2 (Fri 6:00 pm to 9:20 pm Sun 6:00 pm to 9:20 pm)",
    "A26 Completely Online Wizards (Thu 6:00 pm to 9:20 pm Sun 11:00 to 2:20 pm)",
    "A26 FC Road Synergy COC + Champions (Tue 6:00 pm to 9:20 pm Fri 6:00 pm to 9:20 pm) [GC Mid]",
    "A26 FC Road Synergy Wizards (Thu 6:00 pm to 9:20 pm Sun 11:00 am to 2:20 pm) [GC Mid]",
    "A26 Hadapsar Offline Champion (Fri 5:30 pm to 8:50 pm Sun 11:00 am to 2:20 pm) [Krome Mall Classroom 4]",
    "A26 Hadapsar Offline COC (Fri 5:30 pm to 8:50 pm Sun 11:00 am to 2:20 pm) [Krome Mall Classroom 3]",
    "A26 Hadapsar Offline Wizards (Thu 5:30 pm to 8:50 pm Sun 11:00 to 2:20 pm) [New Hadapsar Classroom 2]",
    "A26 Katraj Offline COC + Champions (Wed 5:30 pm to 8:50 pm Sat 5:30 pm to 8:50 pm) [Classroom 2]",
    "A26 Kothrud Offline COC + Champions (Wed 6:00 pm to 9:20 pm Sat 6:00 pm to 9:20 pm) [Akshat Classroom]",  
    "A26 PCMC Offline COC + Champions (Thur(6 pm to 9:20 pm Sun 11:00 am to 2:20 pm) [Classroom 3]",
    "A26 Pimple Saudagar Offline Champion (Wed 5:30 pm to 8:50 pm Sun 11:00 am to 2:20 pm) [Classroom 5]",
    "A26 Pimple Saudagar Offline COC - 1 (Tue 5:30 pm to 8:50 pm Sat 5:30 pm to 8:50 pm) [Classroom 1]",
    "A26 Pimple Saudagar Offline COC - 2 (Tue 5:30 pm to 8:50 pm Sat 5:30 pm to 8:50 pm) [Classroom 2]",
    "A26 Vimannagar Offline COC + Champions (Wed 5:30 pm to 8:50 pm Sat 5:30 to 8:50 pm) [Classroom 1]",
    "B26 Aundh Offline Champions - 1 (Thu 5:30 to 8:50 pm Sun 11:00 to 2:20 pm) [1st Floor Classroom 1]",
    "B26 Aundh Offline Champions - 2 (Thu 5:30 to 8:50 pm Sun 11:00 to 2:20 pm) [1st Floor Classroom 2]",
    "B26 Aundh Offline COC - 1 (Wed 5:30 to 8:50 pm Fri 5:30 to 8:50 pm) [2nd Floor Big]",
    "B26 Aundh Offline COC - 2 (Wed 5:30 to 8:50 pm Fri 5:30 to 8:50 pm) [2nd Floor Small]",
    "B26 Aundh Offline Wizards (Thu 5:30 to 8:50 pm Sat 5:30 to 8:50 pm) [2nd Floor Small]",
    "B26 Aundh Synergy Champions (Tue 6:00 to 9:20 pm Sun 7:00 to 10:20 am) [2nd Floor Small]",
    "B26 Aundh Synergy COC (Tue 6:00 to 9:20 pm Sun 7:00 to 10:20 am) [2nd Floor Big]",
    "B26 Completely Online Champions (Fri 6:00 to 9:20 pm Sun 6:00 to 9:20 pm)",
    "B26 Completely Online Champions (Tue 6:00 to 9:20 pm Sat 6:00 to 9:20 pm)",
    "B26 Completely Online COC (Fri 6:00 to 9:20 pm Sun 6:00 to 9:20 pm)",
    "B26 Completely Online COC (Tue 6:00 to 9:20 pm Sat 6:00 to 9:20 pm)",
    "B26 Completely Online COC + Champions (Sat 6:00 to 9:20 pm Sun 7:00 to 10:20 am)",
    "B26 Completely Online Wizards (Wed 6:00 to 9:20 pm Fri 6:00 to 9:20 pm)",
    "B26 FC Road Synergy COC + Champions (Tue 6:00 to 9:20 pm Sat 6:00 to 9:20 pm) [GC Mid]",
    "B26 Hadapsar Offline Champions (Fri 5:30 to 8:50 pm Sun 11:00 to 2:20 pm) [Krome Mall Classroom 2]",
    "B26 Hadapsar Offline COC (Wed 5:30 to 8:50 pm & Sat 5:30 to 8:50 pm) [Krome Mall Classroom 3]",
    "B26 Katraj Offline COC + Champions (Fri 5:30 to 8:50 pm Sun 11:00 to 2:20 pm) [Classroom 2]",
    "B26 Kothrud Offline Champions (Thu 6:00 to 9:20 pm Sat 6:00 to 9:20 pm) [Pratik Classroom]",
    "B26 Kothrud Offline COC (Wed 6:00 to 9:20 pm Fri 6:00 to 9:20 pm) [Pratik Classroom]",
    "B26 Lloyds Synergy Wizards (Fri 6:00 to 9:20 pm & Sun 11:00 to 2:20 pm) [Block 2 508]",
    "B26 PCMC Offline Champions (Wed 6:00 to 9:20 pm Sun 11:00 to 2:20 pm) [Classroom 2]",
    "B26 PCMC Offline COC (Thu 6:00 to 9:20 pm Sat 6:00 to 9:20 pm) [Classroom 1]",
    "B26 Pimple Saudagar Offline Champions - 1 (Fri 5:30 to 8:50 pm Sun 11:00 to 2:20 pm) [Classroom 3]",
    "B26 Pimple Saudagar Offline Champions - 2 (Fri 5:30 to 8:50 pm Sun 11:00 to 2:20 pm) [Classroom 4]",
    "B26 Pimple Saudagar Offline COC - 1 (Thu 5:30 to 8:50 pm Sat 5:30 to 8:50 pm) [Classroom 3]",
    "B26 Pimple Saudagar Offline COC - 2 (Thu 5:30 to 8:50 pm Sat 5:30 to 8:50 pm) [Classroom 4]",
    "B26 Vimannagar Offline Champions (Fri 5:30 to 8:50 pm Sun 11:00 to 2:20 pm) [Classroom 1]",
    "B26 Vimannagar Offline COC (Thu 5:30 to 8:50 pm Sat 5:30 to 8:50 pm) [Classroom 3]",
    "Biology Extra Classes for ICSE Board ( Online) ( 6 to 9:20 pm)",


    "C-26  COC+Champ Tutorials-2 (12:30 to 2:30 pm) - Weekend",
    "C-26  Wizards Tutorials-1 (4 to 6 pm)",
    "C-26 Afternoon Wizards Tutorials-2 (12:30 to 2:30 pm) - Weekend",
    "C-26 WOW Tutorials (7 to 9 am) (Weekends)",
    "C-27 COC + Champ Afternoon Tutorials ( 12:30 pm to 2:30 pm) - Weekend",
    "C-27 COC Morning Tutorials-1 (3 to 5 pm)",
    "C-27 COC Morning Tutorials-2 (3 to 5 pm)",
    "C-27 COC Noon Tutorials - 1 ( 6 pm to 8 pm)",
    "C-27 COC Noon Tutorials - 2 ( 6 pm to 8 pm)",
    "C-27 Champions Morning Tutorials-1 (3 to 5 pm)",
    "C-27 Champions Noon Tutorials  ( 6 pm to 8 pm)",
    "C-27 Wizards Afternoon Tutorials ( 12:30 pm to 2:30 pm) - Weekend",
    "C-27 Wizards Noon Tutorials ( 6 pm to 8 pm)",
    "C-27 WOW Tutorials (7 to 9 am) (Weekends)",
    "F Adv Plus 10th std Bio (Online) (Friday) (6 pm to 9:20 pm)",
    "Pre FB Offline Aundh Champions (Sat 5 to 8:20 pm) - Shambhu Vihar New building (Small) - 1st floor class 1",
    "Pre FB Online COC (Sun 3 to 6:20 pm)"
]


from datetime import datetime

def format_12hr(h, m):
    return datetime.strptime(f"{h}:{m}", "%H:%M").strftime("%I:%M %p").lstrip('0')

TIME_LIST = [format_12hr(h, m) for h in range(7, 22) for m in range(0, 60, 5)]
CLASSROOM_LIST = [f'C{i}' for i in range(1, 11)]
SUBJECT_LIST = ['Physics', 'Chemistry', 'Mathematics', 'Logic', 'Coding']
MODE_LIST = ['OFFLINE', 'ONLINE', 'COMBINE']



def ensure_sheets():
    spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
    existing_sheets = [ws.title for ws in spreadsheet.worksheets()]

    # Create FACULTY sheet with headers if not exist
    if FACULTY_SHEET not in existing_sheets:
        worksheet = spreadsheet.add_worksheet(title=FACULTY_SHEET, rows="100", cols="10")
        headers = [["FacultyID","Location","Zone", "Maximum Load","Actual Load","Office Work"]]

        worksheet.update('A1:F1', headers)

    # Create COURSES sheet with headers if not exist
    if COURSE_SHEET not in existing_sheets:
        worksheet = spreadsheet.add_worksheet(title=COURSE_SHEET, rows="100", cols="10")
        headers = [["Batch Name", "Physics", "Chemistry", "Mathematics", "Logic", "Coding"," Course"]]
        worksheet.update('A1:G1', headers)

    # Create CAPACITY sheet with headers if not exist
    if CAPACITY_SHEET not in existing_sheets:
        worksheet = spreadsheet.add_worksheet(title=CAPACITY_SHEET, rows="100", cols="10")
        headers = [["Location", "Classroom", "Seating Capacity", "Alloted Students", "Ownership"]]
        worksheet.update('A1:E1', headers)


def autofit_columns(sheet):
    for col in sheet.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        sheet.column_dimensions[col_letter].width = max_length + 2

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Replace with secure authentication in real apps
        if username == 'admin' and password == 'password123':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    
    filtered = None  # ✅ Initialize this here

    # Connect to Google Sheet
    spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)

    # Load Faculty Sheet safely
    faculty_ws = spreadsheet.worksheet(FACULTY_SHEET)
    try:
        faculty_df = get_as_dataframe(faculty_ws, evaluate_formulas=True).fillna("")
        faculty_df.columns = [str(c).strip() for c in faculty_df.columns]
        if "FacultyID" not in faculty_df.columns or not faculty_df.columns.is_unique:
            raise ValueError("Invalid Faculty Sheet")
    except Exception:
        faculty_df = pd.DataFrame(columns=["FacultyID","Location","Zone","Maximum Load","Actual Load","Office Work"])

    # Load Course Sheet safely
    course_ws = spreadsheet.worksheet(COURSE_SHEET)
    try:
        course_df = get_as_dataframe(course_ws).fillna("")
        course_df.columns = [str(c).strip() for c in course_df.columns]
        if "Batch" not in course_df.columns or not course_df.columns.is_unique:
            course_df = pd.DataFrame(columns=["Batch", "Mode", "Physics", "Chemistry", "Mathematics", "Logic", "Coding", "Course"])

    except Exception:
        course_df = pd.DataFrame(columns=["Batch", "Mode", "Physics", "Chemistry", "Mathematics", "Logic", "Coding", "Course"])

    # Load/Create Capacity Sheet safely
    try:
        capacity_ws = spreadsheet.worksheet(CAPACITY_SHEET)
        capacity_df = get_as_dataframe(capacity_ws).fillna("")
        capacity_df.columns = [str(c).strip() for c in capacity_df.columns]
        if "Classroom" not in capacity_df.columns or not capacity_df.columns.is_unique:
            raise ValueError("Invalid Capacity Sheet")
    except gspread.exceptions.WorksheetNotFound:
        capacity_df = pd.DataFrame(columns=["Location", "Classroom", "Seating Capacity", "Alloted Students", "Ownership"])
    except Exception:
        capacity_df = pd.DataFrame(columns=["Location", "Classroom", "Seating Capacity", "Alloted Students", "Ownership"])

    if request.method == 'POST':
        form_type = request.form.get('form')
        action = request.form.get('action')
        
        
        if form_type == 'faculty':
            faculty_id = request.form.get('faculty_id', '').strip()
            
            if action == 'delete' and faculty_id:
                faculty_df["FacultyID"] = faculty_df["FacultyID"].astype(str)
                faculty_df = faculty_df[faculty_df["FacultyID"] != faculty_id]

                # ✅ Clear and update the Google Sheet even if empty
                faculty_ws.clear()
                headers = ["FacultyID", "Location", "Zone", "Maximum Load", "Actual Load", "Office Work"]
                faculty_ws.append_row(headers)

                if not faculty_df.empty:
                    set_with_dataframe(faculty_ws, faculty_df, include_column_header=False, resize=True)

 
            else:
                location = request.form.get('location', '').strip()
                zone = request.form.get('zone', '').strip()

                try:
                    max_load = int(request.form.get('max_load', 48) or 48)
                except:
                    max_load = 48
        
                try:
                    actual_load = int(request.form.get('actual_load', 0) or 0)
                except:
                    actual_load = 0

            # ✅ Calculate Office Work if both > 0
                office_work = max_load - actual_load

         
    # ✅ Remove existing FacultyID entry
                faculty_df["FacultyID"] = faculty_df["FacultyID"].astype(str)
                faculty_df = faculty_df[faculty_df["FacultyID"] != faculty_id]

    # ✅ Add updated/new row
                faculty_df = pd.concat([faculty_df, pd.DataFrame([{
                    "FacultyID": faculty_id,
                    "Location": location,
                    "Zone": zone,
                    "Maximum Load": max_load,
                    "Actual Load": actual_load,
                    "Office Work": office_work
                }])], ignore_index=True)
        


        elif form_type == 'course':
            course= request.form.get('course_name', '').strip()
            if action == 'create':
                mode = request.form.get('mode')
                physics = request.form.get('physics')
                chemistry = request.form.get('chemistry')
                mathematics = request.form.get('mathematics')
                logic = request.form.get('logic')
                coding = request.form.get('coding')
                option = request.form.get('batch')
                course_df = course_df[course_df["Course"] != course]
                course_df = pd.concat([course_df, pd.DataFrame([{
                    "course": course,
                    "Mode": mode,
                    "Physics": physics,
                    "Chemistry": chemistry,
                    "Mathematics": mathematics,
                    "Logic": logic,
                    "Coding": coding,
                    "Batch": option
                }])], ignore_index=True)
            elif action == 'delete' and course:
                course_df = course_df[course_df["Course"] != course]

        elif form_type == 'capacity':
            classroom = request.form.get('classroom_id', '').strip()
            location = request.form.get('location')
            seating_capacity = request.form.get('capacity')
            ownership = request.form.get('ownership')
            students = request.form.get('students')

            if action == 'create' and classroom:
                capacity_df = capacity_df[capacity_df["Classroom"] != classroom]
                capacity_df = pd.concat([capacity_df, pd.DataFrame([{
                    "Location": location,
                    "Classroom": classroom,
                    "Seating Capacity": seating_capacity,
                    "Alloted Students": students,
                    "Ownership": ownership
                }])], ignore_index=True)
            elif action == 'delete' and classroom:
                capacity_df = capacity_df[capacity_df["Classroom"] != classroom]

        # ✅ Save back to Google Sheets
        sheets_data = []

        if not faculty_df.empty and "FacultyID" in faculty_df.columns:
            safe_faculty_df = faculty_df.assign(blank1="", blank2="")[["FacultyID","Location","Zone","Maximum Load","Actual Load","Office Work"]]
            sheets_data.append((
                FACULTY_SHEET,
                safe_faculty_df,
                ["FacultyID","Location","Zone","Maximum Load","Actual Load","Office Work"]
    ))

        if not course_df.empty and "Course" in course_df.columns:
            sheets_data.append((
               COURSE_SHEET,
               course_df,
        list(course_df.columns)
    ))

        if not capacity_df.empty and "Classroom" in capacity_df.columns:
            sheets_data.append((
                CAPACITY_SHEET,
                capacity_df,
                list(capacity_df.columns)
    ))

        for sheet_name, df, headers in sheets_data:
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                spreadsheet.del_worksheet(worksheet)  # delete first if exists
            except gspread.exceptions.WorksheetNotFound:
                pass
            
            
    # ✅ Create fresh sheet safely inside the loop
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")
    
     # Fill empty rows to ensure Google Sheet shows a full grid
            while len(df) < 100:
              df = pd.concat([df, pd.DataFrame([[""] * len(df.columns)], columns=df.columns)], ignore_index=True)

            
            # 🔐 Ensure headers are assigned properly
            df.columns = headers

# ✅ Upload entire DataFrame with correct column order
            set_with_dataframe(worksheet, df, include_column_header=True, resize=True)
            worksheet.resize(rows=1000, cols=20)
    # Make unique temporary headers for uploading
            seen = set()
            safe_headers = []
            for h in headers:
                original = h or "blank"
                counter = 1
                while original in seen:
                    original = f"{h}_{counter}"
                    counter += 1
                seen.add(original)
                safe_headers.append(original)

            
            # df.columns = safe_headers  # Set safe headers temporarily
            df.columns = [str(c).strip() if c else "blank" for c in headers]

            set_with_dataframe(worksheet, df, include_column_header=True, resize=False)
            worksheet.resize(rows=1000, cols=20)  # Force Google Sheet to look full
            


    # Reset real headers on row 1
            worksheet.update('A1', [headers])
     
         # ✅ For GET request
    if "FacultyID" not in faculty_df.columns:
        faculty_df["FacultyID"] = ""

    faculty_df["FacultyID"] = faculty_df["FacultyID"].astype(str).str.strip()
    faculty_df = faculty_df.dropna(subset=["FacultyID"])
    faculty_df = faculty_df[faculty_df["FacultyID"].str.len() > 0]
    faculty_df["FacultyID_FirstChar"] = faculty_df["FacultyID"].str[0].str.upper()

    # Filter only valid uppercase alphabet characters
    valid_letters = sorted([
        c for c in set(faculty_df["FacultyID_FirstChar"])
        if isinstance(c, str) and c.isalpha() and len(c) == 1
    ])

    faculty_dict = {}

    for letter in valid_letters:
        filtered = faculty_df[faculty_df["FacultyID"].str.upper().str.startswith(letter)]
        if not filtered.empty:
            # Get the last alphabetically sorted FacultyID starting with this letter
            faculty_dict[letter] = filtered["FacultyID"].sort_values().tolist()[-1]


    all_faculty_ids = faculty_df["FacultyID"].dropna().astype(str).unique().tolist()

    return render_template("index.html",
        faculty_dict=faculty_dict,
        area_list=AREA_LIST,
        zone_list=ZONE_LIST,
        course_list=COURSE_LIST,
        day_list=DAY_LIST,
        classroom_list=CLASSROOM_LIST,
        subject_list=SUBJECT_LIST,
        mode_list=MODE_LIST,
        time_list=TIME_LIST,
        all_faculty_ids=sorted(all_faculty_ids),
        Batch_list=BATCH_LIST,
    )
    
@app.route('/submit_course', methods=['POST'])
def submit_course():
    spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
    action = request.form.get('action')

    courses = request.form.getlist('course_name[]')
    subjects = request.form.getlist('subject[]')
    modes = request.form.getlist('mode[]')
    batches = request.form.getlist('batch[]')

    # Extract all time slot arrays
    days = request.form.getlist('day[]')
    start_times = request.form.getlist('start_time[]')
    end_times = request.form.getlist('end_time[]')

    # Extract grouped faculty list
    faculties_grouped = []
    i = 0
    while True:
        key = f"faculties[{i}][]"
        if key in request.form:
            faculties_grouped.append(request.form.getlist(key))
            i += 1
        else:
            break

    try:
        worksheet = spreadsheet.worksheet(COURSE_SHEET)
        headers = worksheet.row_values(1)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=COURSE_SHEET, rows="1000", cols="20")
        headers = ["Course Name", "Subject", "Day_Time", "Mode", "Faculty", "Batch"]
        worksheet.append_row(headers)

    existing_data = worksheet.get_all_records()
    df = pd.DataFrame(existing_data)
    
    
    
    if action == 'delete':
       new_df = df.copy()

       for i in range(len(courses)):
            course = courses[i]
            subject = subjects[i]
            selected_faculties = set(faculties_grouped[i]) if i < len(faculties_grouped) else set()

        # Filter out rows that match course, subject and any matching faculty
            def row_matches(row):
                row_faculties = set(str(row["Faculty"]).split(", "))
                return (
                   row["Course Name"] == course and
                   row["Subject"] == subject and
                   not selected_faculties.isdisjoint(row_faculties)
            )

            new_df = new_df[~new_df.apply(row_matches, axis=1)]

       worksheet.batch_clear(['A2:Z1000'])

       if new_df.empty:
           return redirect("/")

       set_with_dataframe(worksheet, new_df, row=2, include_column_header=False, resize=False)
       return redirect("/")


    # ✅ For Create
    new_rows = []
    total_blocks = len(courses)
    time_index = 0

    for i in range(total_blocks):
        course = courses[i]
        subject = subjects[i]
        mode = modes[i] if i < len(modes) else ""
        batch = batches[i] if i < len(batches) else ""
        faculty = ", ".join(faculties_grouped[i]) if i < len(faculties_grouped) else ""

        # Collect all time slots for this course block
        schedule_parts = []

        # Heuristic: assume each course block has at least 1 slot, and detect when the next course block starts
        # You can customize this logic if you later add hidden slot counters
        while time_index < len(days):
            d = days[time_index]
            s = start_times[time_index]
            e = end_times[time_index]

            # Defensive check
            if not (d and s and e):
                time_index += 1
                continue

            schedule_parts.append(f"{d} - {s} to {e}")
            time_index += 1

            # If next course exists and we've passed equal number of time slots per course
            # this is a rough logic assuming time slots are evenly distributed
            if len(schedule_parts) >= 1 and (i + 1 < total_blocks) and (
                len(days) - time_index == total_blocks - (i + 1)
            ):
                break

        schedule = " and ".join(schedule_parts)

        new_rows.append({
            "Course Name": course,
            "Subject": subject,
            "Day_Time": schedule,
            "Mode": mode,
            "Faculty": faculty,
            "Batch": batch
        })

    new_df = pd.DataFrame(new_rows)
    final_df = pd.concat([df, new_df], ignore_index=True)

    worksheet.batch_clear(['A2:Z1000'])
    set_with_dataframe(worksheet, final_df, row=2, include_column_header=False, resize=False)
    worksheet.resize(rows=1000, cols=20)

    return redirect('/')
    
    
@app.route("/submit_capacity", methods=["POST"])
def submit_capacity():
    try:
        import pandas as pd

        # ── 1. Grab form data ───────────────────────────────────────────────
        action           = request.form.get("action")
        location         = request.form.get("location")
        classroom_names  = request.form.getlist("classroom_names[]")
        seating_caps     = request.form.getlist("seating_capacities[]")
        ownerships       = request.form.getlist("ownerships[]")
        students         = request.form.getlist("students[]")
        classroom_days   = request.form.getlist("classroom_days[]")
        start_times      = request.form.getlist("start_times[]")
        end_times        = request.form.getlist("end_times[]")

        if not all(len(lst) == len(classroom_names) for lst in
                   [seating_caps, ownerships, students,
                    classroom_days, start_times, end_times]):
            return "Form data is incomplete or inconsistent", 400

        # ── 2. Load or create the Google Sheet ──────────────────────────────
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        try:
            sheet = spreadsheet.worksheet(CAPACITY_SHEET)
        except gspread.exceptions.WorksheetNotFound:
            sheet = spreadsheet.add_worksheet(title=CAPACITY_SHEET, rows="100", cols="20")

        headers = ["Location", "Day_Time", "Classroom", "Seating Capacity", "Allotted Students", "Owned"]
        all_data = sheet.get_all_values()

        if not all_data or len(all_data[0]) < len(headers):
            df = pd.DataFrame(columns=headers)
        else:
            sheet_headers = [h.strip() for h in all_data[0]]
            df = pd.DataFrame(all_data[1:], columns=sheet_headers)
            df.columns = [c.strip() for c in df.columns]

        # ── 3. Action handling ───────────────────────────────────────────────
        if action == "delete":
           classroom = request.form.get("classroom_name")
           day = request.form.get("classroom_day")
           start = request.form.get("start_time")
           end = request.form.get("end_time")

           if not (location and classroom and day and start and end):
              return "Missing information for delete action", 400

           day_time = f"{day} - {start} to {end}"

           df = df[~(
                (df["Location"] == location) &
                (df["Classroom"] == classroom) &
                (df["Day_Time"] == day_time)
            )]


        

        else:
             # ── Creation / Update logic ─────────────────────────────────────
            if not all(len(lst) == len(classroom_names) for lst in
                       [seating_caps, ownerships, students, classroom_days, start_times, end_times]):
                return "Form data is incomplete or inconsistent", 400
            
            
            
            
            for i in range(len(classroom_names)):
                if classroom_names[i].strip() and classroom_days[i] and start_times[i] and end_times[i]:
                    day_time = f"{classroom_days[i]} - {start_times[i]} to {end_times[i]}"
                    
                    # Remove existing rows that match classroom + time + location
                    df = df[~(
                        (df["Classroom"] == classroom_names[i]) &
                        (df["Day_Time"] == day_time) &
                        (df["Location"] == location)
                    )]

                    new_row = {
                        "Location": location,
                        "Day_Time": day_time,
                        "Classroom": classroom_names[i],
                        "Seating Capacity": seating_caps[i],
                        "Allotted Students": students[i],
                        "Owned": ownerships[i]
                    }

                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # ── 4. Clean up padding rows before padding again ────────────────────
        df = df[df["Classroom"].str.strip().astype(bool)]

        # ── 5. Pad for nice Google Sheet view ────────────────────────────────
        while len(df) < 100:
            df = pd.concat([df, pd.DataFrame([[""] * len(headers)], columns=headers)], ignore_index=True)

        # ── 6. Write back to Google Sheet ────────────────────────────────────
        sheet.clear()
        sheet.append_row(headers)
        set_with_dataframe(sheet, df, row=2, include_column_header=False, resize=True)
        sheet.format("A1:F1", {"textFormat": {"bold": True}})
        sheet.resize(rows=1000, cols=20)

        return redirect("/")

    except Exception as e:
        return f"An error occurred: {e}", 500

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)


    
    


 
