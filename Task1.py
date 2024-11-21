import pandas as pd
from datetime import datetime
from google.colab import files  # Importing Google Colab's files module for uploads


def read_inputs():
    """
    Handles file uploads in Google Colab and reads them into DataFrames.
    """
    try:
        uploaded_files = files.upload()  # Allow user to upload files in Colab

        # Dynamically load files based on uploaded filenames
        ip_1 = pd.read_csv(next((file for file in uploaded_files if "ip_1" in file), None))
        ip_2 = pd.read_csv(next((file for file in uploaded_files if "ip_2" in file), None))
        ip_3 = pd.read_csv(next((file for file in uploaded_files if "ip_3" in file), None))
        ip_4 = pd.read_csv(next((file for file in uploaded_files if "ip_4" in file), None))

        return ip_1, ip_2, ip_3, ip_4
    except Exception as e:
        print(f"Error: {e}")
        return None, None, None, None

    except Exception as e:
        print(f"Error: {e}")
        return None, None, None, None

def save_seating_plan(seating_plan):
    """
    Save the seating plan in CSV and Excel formats.
    """
    seating_df = pd.DataFrame(seating_plan)

    # Save as CSV (semicolon-separated, as requested)
    seating_csv_filename = "seating_plan.csv"
    seating_df.to_csv(seating_csv_filename, sep=';', index=False)

    # Save as Excel
    seating_excel_filename = "seating_plan.xlsx"
    seating_df.to_excel(seating_excel_filename, index=False)

    print(f"Files saved:\n- {seating_csv_filename}\n- {seating_excel_filename}")

    # Offer files for download
    files.download(seating_csv_filename)
    files.download(seating_excel_filename)


def allocate_seating_with_optimization(ip_1, ip_2, ip_3, buffer_size=5, seating_type='dense'):
    # Function remains unchanged
    seating_plan = []  # List to store the seating arrangement for each room
    course_groups = ip_1.groupby('course')  # Grouping students by their course
    sorted_courses = course_groups.size().sort_values(ascending=False).index  # Sorting courses by size (largest first)
    room_groups = ip_3.groupby('block')  # Grouping rooms by their blocks (e.g., Block 9, LT)

    prioritized_blocks = ['Block 9', 'LT']  # Blocks to prioritize when assigning rooms
    room_allocation_by_date = {}  # Dictionary to track room usage for each date

    for course in sorted_courses:
        students = course_groups.get_group(course).reset_index(drop=True)  # Get all students for the current course
        num_students = len(students)  # Number of students in the current course

        # Get the exam date for the course
        exam_date = ip_2.loc[ip_2['course'] == course, 'exam_date'].values
        if len(exam_date) == 0:
            continue  # If no exam date is found, skip this course

        exam_date = datetime.strptime(exam_date[0], '%d/%m/%Y').date()  # Convert to datetime object

        # Ensure the date exists in the room allocation tracking
        if exam_date not in room_allocation_by_date:
            room_allocation_by_date[exam_date] = {room_name: 0 for room_name in ip_3['room_name']}  # Initialize room availability (empty) for this date

        # Allocate rooms for the current course based on the available rooms and the date
        for block in prioritized_blocks:
            if block not in room_groups.groups:
                continue  # Skip this block if it has no rooms

            rooms_in_block = room_groups.get_group(block).sort_values(by='capacity', ascending=False)  # Sort rooms by capacity

            for _, room in rooms_in_block.iterrows():  # Iterating over each room in the sorted block
                room_name = room['room_name']  # Room name
                room_capacity = room['capacity'] - buffer_size  # Adjust for buffer size

                # Check the current number of students allocated to this room for the current exam date
                allocated_students = room_allocation_by_date[exam_date][room_name]

                # Skip this room if it's already full for this exam date
                if allocated_students >= room_capacity:
                    continue

                # Determine how many more students this room can accommodate
                remaining_capacity = room_capacity - allocated_students

                # Determine maximum capacity for each course based on seating type
                if seating_type == 'dense':
                    max_course_capacity = min(remaining_capacity, num_students)  # Full capacity for dense seating
                elif seating_type == 'sparse':
                    max_course_capacity = min(remaining_capacity // 2, num_students)  # Half capacity for sparse seating
                else:
                    raise ValueError("Invalid seating type. Choose 'dense' or 'sparse'.")

                if max_course_capacity > 0:
                    # Assign students to the room up to the maximum allowed by the seating type
                    assigned_students = students.iloc[:max_course_capacity]  # Assign up to the max capacity
                    # Format the roll numbers as a semicolon-separated string
                    roll_list = ';'.join(assigned_students['roll_no'].astype(str))
                    seating_plan.append({
                        'Date': exam_date.strftime('%d/%m/%Y'),  # Format date as DD/MM/YYYY
                        'Day': exam_date.strftime('%A'),  # Get the day of the week
                        'course_code': course,
                        'Room': room_name,
                        'Allocated_students_count': len(assigned_students),
                        'Roll_list': roll_list
                    })

                    # Update room allocation for this exam date (mark it as filled for the day)
                    room_allocation_by_date[exam_date][room_name] += len(assigned_students)

                    students = students.iloc[max_course_capacity:]  # Remove assigned students from the list
                    num_students -= len(assigned_students)  # Update the number of remaining students

                if num_students <= 0:
                    break  # Stop if all students are assigned
            if num_students <= 0:
                break  # Stop if all students are assigned

    # Sort seating plan by Date in ascending order (from the earliest to latest)
    seating_plan_sorted = sorted(seating_plan, key=lambda x: datetime.strptime(x['Date'], '%d/%m/%Y'))
    return seating_plan_sorted  # Return the sorted seating plan

def save_seating_plan(seating_plan):
    """
    Save the seating plan in CSV and Excel formats.
    """
    seating_df = pd.DataFrame(seating_plan)

    # Save as CSV (semicolon-separated, as requested)
    seating_csv_filename = "seating_plan.csv"
    seating_df.to_csv(seating_csv_filename, sep=';', index=False)

    # Save as Excel
    seating_excel_filename = "seating_plan.xlsx"
    seating_df.to_excel(seating_excel_filename, index=False)

    print(f"Files saved:\n- {seating_csv_filename}\n- {seating_excel_filename}")

    # Offer files for download
    files.download(seating_csv_filename)
    files.download(seating_excel_filename)

# Main function
if __name__ == "__main__":
    # Step 1: Read inputs
    ip_1, ip_2, ip_3, ip_4 = read_inputs()

    # Ensure files were uploaded correctly and contain data
    if any(df is None for df in [ip_1, ip_2, ip_3, ip_4]):
        print("Error: Please ensure all required files are uploaded.")
    elif any(df.empty for df in [ip_1, ip_2, ip_3, ip_4]):
        print("Error: One or more files are empty. Please upload valid data.")
    else:
        # Step 2: Allocate seating with user choice of dense or sparse
        try:
            buffer_size = int(input("Enter buffer size (e.g., 5 for 5 students per room left unassigned): "))
            seating_type = input("Enter seating type ('dense' or 'sparse'): ").strip().lower()

            if seating_type not in ['dense', 'sparse']:
                raise ValueError("Invalid seating type. Please enter 'dense' or 'sparse'.")

            seating_plan = allocate_seating_with_optimization(
                ip_1, ip_2, ip_3, buffer_size=buffer_size, seating_type=seating_type
            )

            # Step 3: Save output in both CSV and Excel formats
            save_seating_plan(seating_plan)

        except ValueError as e:
            print(f"Input error: {e}")
