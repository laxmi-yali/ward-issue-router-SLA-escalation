
from datetime import date, timedelta

MAX_SEMESTERS = 20
MAX_SUBJECTS = 30
MAX_HOLIDAYS = 100
MAX_EXAMS_PER_DAY = 10


# ---------------- GENERATE DATES ----------------

def generate_dates(start_date, end_date):
    dates = []
    current_date = start_date

    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    return dates


# ---------------- HOLIDAY CHECK ----------------

def is_holiday(current_date, holidays):
    return current_date in holidays


# ---------------- VALID DATE ----------------

def is_valid_date(current_date, holidays):
    # Python weekday(): Monday = 0, Sunday = 6
    if current_date.weekday() == 6:
        return False

    if is_holiday(current_date, holidays):
        return False

    return True


# ---------------- NEXT VALID DATE ----------------

def get_next_valid_date(dates, index, holidays):
    while index < len(dates):
        if is_valid_date(dates[index], holidays):
            return index

        index += 1

    return -1


# ---------------- INPUT DATE ----------------

def read_date(prompt):
    while True:
        try:
            d, m, y = map(int, input(prompt).split())
            return date(y, m, d)
        except ValueError:
            print("Invalid date. Enter a valid date as dd mm yyyy.")


# ---------------- MAIN FUNCTION ----------------

def main():
    print("=" * 80)
    print("              EXAM TIMETABLE GENERATOR SYSTEM")
    print("=" * 80)

    # ---------------- DATE INPUT ----------------

    start_date = read_date(
        "\nEnter Start Date (dd mm yyyy): "
    )

    end_date = read_date(
        "Enter End Date (dd mm yyyy): "
    )

    if start_date > end_date:
        print("ERROR: Start date must not be after end date!")
        return

    dates = generate_dates(start_date, end_date)

    # ---------------- HOLIDAYS ----------------

    while True:
        try:
            total_holidays = int(
                input("\nEnter Number of Government Holidays: ")
            )

            if 0 <= total_holidays <= MAX_HOLIDAYS:
                break

            print(f"Enter a number between 0 and {MAX_HOLIDAYS}.")

        except ValueError:
            print("Enter a valid integer.")

    holidays = set()

    print("Enter Holiday Dates (dd mm yyyy):")

    for i in range(total_holidays):
        holiday = read_date(f"Holiday {i + 1}: ")
        holidays.add(holiday)

    # ---------------- SEMESTERS ----------------

    while True:
        try:
            total_semesters = int(
                input("\nEnter Number of Semesters: ")
            )

            if 1 <= total_semesters <= MAX_SEMESTERS:
                break

            print(f"Enter a number between 1 and {MAX_SEMESTERS}.")

        except ValueError:
            print("Enter a valid integer.")

    semesters = []

    for i in range(total_semesters):
        print(f"\nSemester Entry {i + 1}")

        semester_number = int(
            input("Enter which Semester: ")
        )

        branch_name = input(
            "Enter Branch/Course Name: "
        )

        while True:
            try:
                number_of_subjects = int(
                    input("Enter Number of Subjects: ")
                )

                if 1 <= number_of_subjects <= MAX_SUBJECTS:
                    break

                print(
                    f"Enter a number between 1 and {MAX_SUBJECTS}."
                )

            except ValueError:
                print("Enter a valid integer.")

        subjects = []

        print("Enter Subject Names:")

        for j in range(number_of_subjects):
            subject = input(f"Subject {j + 1}: ")
            subjects.append(subject)

        semesters.append({
            "number": semester_number,
            "branch": branch_name,
            "subjects": subjects
        })

    # ---------------- EXAMS PER DAY ----------------

    while True:
        try:
            exams_per_day = int(
                input("\nEnter Number of Exams Per Day: ")
            )

            if 1 <= exams_per_day <= MAX_EXAMS_PER_DAY:
                break

            print(
                f"Enter a number between 1 and {MAX_EXAMS_PER_DAY}."
            )

        except ValueError:
            print("Enter a valid integer.")

    # ---------------- TIME SLOT INPUT ----------------

    time_slots = []

    print("\nEnter Time Slots:")

    for i in range(exams_per_day):
        slot = input(f"Time Slot {i + 1}: ")
        time_slots.append(slot)

    # ---------------- GAP DAYS ----------------

    while True:
        try:
            gap_days = int(
                input("\nEnter Gap Days Between Exam Dates: ")
            )

            if gap_days >= 0:
                break

            print("Gap days cannot be negative.")

        except ValueError:
            print("Enter a valid integer.")

    # ---------------- GENERATE TIMETABLES ----------------

    for semester in semesters:
        print("\n\n" + "=" * 115)

        print(
            f"EXAMINATION TIMETABLE - "
            f"SEM {semester['number']} ({semester['branch']})"
        )

        print("=" * 115)

        print(
            f"{'DATE':<15} "
            f"{'SUBJECT':<40} "
            f"{'SEM':<15} "
            f"{'TIME SLOT':<30}"
        )

        print("-" * 115)

        current_date_index = 0
        slot_index = 0

        for subject in semester["subjects"]:

            current_date_index = get_next_valid_date(
                dates, current_date_index, holidays
            )

            if current_date_index == -1:
                print("\nERROR: Not enough valid dates!")
                return

            exam_date = dates[current_date_index]

            print(
                f"{exam_date.strftime('%d/%m/%Y'):<15} "
                f"{subject:<40} "
                f"{semester['number']:<15} "
                f"{time_slots[slot_index]:<30}"
            )

            print("-" * 115)

            slot_index += 1

            # Move to the next exam date after all daily slots
            if slot_index == exams_per_day:
                slot_index = 0
                gaps = 0
                current_date_index += 1

                while (
                    gaps < gap_days
                    and current_date_index < len(dates)
                ):
                    if is_valid_date(
                        dates[current_date_index], holidays
                    ):
                        gaps += 1

                    current_date_index += 1

    # ---------------- SUCCESS ----------------

    print("\n" + "=" * 115)
    print("ALL SEMESTER TIMETABLES GENERATED SUCCESSFULLY")
    print("=" * 115)


if __name__ == "__main__":
    main()
