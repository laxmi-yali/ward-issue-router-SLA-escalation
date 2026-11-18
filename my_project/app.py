
from datetime import date, timedelta
from flask import Flask, render_template, request

app = Flask(__name__)

MAX_SEMESTERS = 20
MAX_SUBJECTS = 30
MAX_HOLIDAYS = 100
MAX_EXAMS_PER_DAY = 10


def generate_dates(start_date, end_date):
    dates = []
    current = start_date

    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)

    return dates


def is_valid_date(current_date, holidays):
    # Monday = 0, Sunday = 6
    return (
        current_date.weekday() != 6
        and current_date not in holidays
    )


def generate_timetable(
    start_date,
    end_date,
    holidays,
    semesters,
    exams_per_day,
    time_slots,
    gap_days
):
    dates = generate_dates(start_date, end_date)
    all_timetables = []

    for semester in semesters:
        timetable = []
        date_index = 0

        for subject_index, subject in enumerate(
            semester["subjects"]
        ):
            # Find the next valid exam date
            while (
                date_index < len(dates)
                and not is_valid_date(
                    dates[date_index], holidays
                )
            ):
                date_index += 1

            if date_index >= len(dates):
                raise ValueError(
                    f"Not enough valid dates for Semester "
                    f"{semester['number']} ({semester['branch']})."
                )

            exam_date = dates[date_index]
            slot_index = subject_index % exams_per_day

            timetable.append({
                "date": exam_date.strftime("%d/%m/%Y"),
                "subject": subject,
                "semester": semester["number"],
                "branch": semester["branch"],
                "time_slot": time_slots[slot_index],
                "sort_date": exam_date
            })

            # After all daily slots are filled,
            # move past the requested number of valid gap days.
            if (subject_index + 1) % exams_per_day == 0:
                date_index += 1
                gaps = 0

                while gaps < gap_days and date_index < len(dates):
                    if is_valid_date(dates[date_index], holidays):
                        gaps += 1

                    date_index += 1

        all_timetables.append({
            "number": semester["number"],
            "branch": semester["branch"],
            "exams": timetable
        })

    return all_timetables


@app.route("/", methods=["GET", "POST"])
def index():
    timetables = None
    error = None

    if request.method == "POST":
        try:
            start_date = date.fromisoformat(
                request.form["start_date"]
            )
            end_date = date.fromisoformat(
                request.form["end_date"]
            )

            if start_date > end_date:
                raise ValueError(
                    "Start date must not be after end date."
                )

            holiday_text = request.form.get(
                "holidays", ""
            ).strip()

            holiday_lines = [
                line.strip()
                for line in holiday_text.splitlines()
                if line.strip()
            ]

            if len(holiday_lines) > MAX_HOLIDAYS:
                raise ValueError(
                    f"Maximum {MAX_HOLIDAYS} holidays allowed."
                )

            holidays = set()

            for line in holiday_lines:
                try:
                    holidays.add(date.fromisoformat(line))
                except ValueError:
                    raise ValueError(
                        f"Invalid holiday date: {line}. "
                        "Use YYYY-MM-DD."
                    )

            total_semesters = int(
                request.form["total_semesters"]
            )

            if not 1 <= total_semesters <= MAX_SEMESTERS:
                raise ValueError(
                    f"Semesters must be between 1 and "
                    f"{MAX_SEMESTERS}."
                )

            semester_numbers = []
            semesters = []

            for i in range(1, total_semesters + 1):
                number = int(request.form[f"sem_number_{i}"])
                branch = request.form[
                    f"branch_{i}"
                ].strip()

                if not branch:
                    raise ValueError(
                        f"Enter a branch name for entry {i}."
                    )

                if number < 1:
                    raise ValueError(
                        "Semester numbers must be positive."
                    )

                if number in semester_numbers:
                    raise ValueError(
                        f"Semester number {number} is duplicated."
                    )

                semester_numbers.append(number)

                subjects = [
                    subject.strip()
                    for subject in request.form[
                        f"subjects_{i}"
                    ].splitlines()
                    if subject.strip()
                ]

                if not 1 <= len(subjects) <= MAX_SUBJECTS:
                    raise ValueError(
                        f"Entry {i} must have between 1 and "
                        f"{MAX_SUBJECTS} subjects."
                    )

                semesters.append({
                    "number": number,
                    "branch": branch,
                    "subjects": subjects
                })

            exams_per_day = int(
                request.form["exams_per_day"]
            )

            if not 1 <= exams_per_day <= MAX_EXAMS_PER_DAY:
                raise ValueError(
                    f"Exams per day must be between 1 and "
                    f"{MAX_EXAMS_PER_DAY}."
                )

            time_slots = [
                slot.strip()
                for slot in request.form[
                    "time_slots"
                ].splitlines()
                if slot.strip()
            ]

            if len(time_slots) != exams_per_day:
                raise ValueError(
                    "Enter exactly one time slot for each "
                    "exam allowed per day."
                )

            gap_days = int(request.form["gap_days"])

            if gap_days < 0:
                raise ValueError(
                    "Gap days cannot be negative."
                )

            timetables = generate_timetable(
                start_date,
                end_date,
                holidays,
                semesters,
                exams_per_day,
                time_slots,
                gap_days
            )

        except (ValueError, KeyError, TypeError) as exc:
            error = str(exc) or "Please check your input."

    return render_template(
        "index.html",
        timetables=timetables,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)
