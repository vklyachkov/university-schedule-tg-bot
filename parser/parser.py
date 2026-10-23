from datetime import date, datetime, time
import requests
from icalendar import Calendar
from dotenv import load_dotenv
import os

load_dotenv()

API_URL = os.getenv("API_URL")
STUDENT_ID = os.getenv("STUDENT_ID")

def get_schedule():
    response = requests.get(
        API_URL,
        params={
            "idStudent": STUDENT_ID,
            "iCal": "true",
        },
        timeout=15,
    )
    response.raise_for_status()

    calendar = Calendar.from_ical(response.content)

    lessons = []

    for event in calendar.walk("VEVENT"):
        start = event.decoded("DTSTART")
        end = event.decoded("DTEND")

        lessons.append({
            "subject": str(event.get("SUMMARY", "Без названия")),
            "start": start,
            "end": end,
            "room": str(event.get("LOCATION", "Аудитория не указана")),
        })

    lessons.sort(key=lambda lesson: lesson["start"])

    return lessons


def format_schedule(lessons):
    if not lessons:
        return "Ближайших занятий нет 🎉"

    day = lessons[0]["start"].strftime("%d.%m.%Y")

    lines = [f"📚 Расписание на {day}\n"]

    for i, lesson in enumerate(lessons, start=1):
        start = lesson["start"].strftime("%H:%M")
        end = lesson["end"].strftime("%H:%M")

        lines.append(
            f"{i}. {start}–{end}\n"
            f"   📖 {lesson['subject']}\n"
            f"   📍 {lesson['room']}"
        )

    return "\n\n".join(lines)

def get_next_day_lessons(lessons):
    now = datetime.now().astimezone()

    normalized = []

    for lesson in lessons:
        start = lesson["start"]
        end = lesson["end"]

        # Приводим время к локальному часовому поясу
        if isinstance(start, date) and not isinstance(start, datetime):
            start = datetime.combine(start, time.min)

        if isinstance(end, date) and not isinstance(end, datetime):
            end = datetime.combine(end, time.min)

        if start.tzinfo is None:
            start = start.astimezone()
        else:
            start = start.astimezone()

        if end.tzinfo is None:
            end = end.astimezone()
        else:
            end = end.astimezone()

        normalized.append({
            **lesson,
            "start": start,
            "end": end,
        })

    # Оставляем занятия, которые ещё не закончились
    upcoming = [
        lesson for lesson in normalized
        if lesson["end"] > now
    ]

    if not upcoming:
        return []

    # Если есть занятия сегодня — выводим их.
    # Иначе выбираем ближайшую дату с занятиями.
    today_lessons = [
        lesson for lesson in upcoming
        if lesson["start"].date() == now.date()
    ]

    if today_lessons:
        return sorted(today_lessons, key=lambda x: x["start"])

    next_date = min(
        lesson["start"].date()
        for lesson in upcoming
    )

    return sorted(
        [
            lesson for lesson in upcoming
            if lesson["start"].date() == next_date
        ],
        key=lambda x: x["start"],
    )

