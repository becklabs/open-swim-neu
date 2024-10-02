import os
import requests
import json
from datetime import datetime
from icalendar import Calendar, Event
from typing import List, Dict
import pytz


def fetch_open_swim_events() -> List[Dict]:
    url = "https://nuevents.neu.edu/ServerApi.aspx/CustomBrowseEvents"
    payload = json.dumps(
        {
            "date": datetime.now().strftime("%Y-%m-%d 00:00:00"),
            "data": {
                "BuildingId": -1,
                "GroupTypeId": -1,
                "GroupId": -1,
                "EventTypeId": 708,
                "RoomId": -1,
                "StatusId": -1,
                "ZeroDisplayOnWeb": 1,
                "HeaderUrl": "",
                "Title": "Open Swim",
                "Format": 1,
                "Rollup": 0,
                "PageSize": 50,
                "DropEventsInPast": False,
            },
        }
    )
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
    }

    response = requests.post(url, headers=headers, data=payload)
    data = response.json()
    events_json = json.loads(data["d"])
    return events_json["MonthlyBookingResults"]


def create_ics_file(events: List[Dict], filename: str) -> None:
    cal = Calendar()
    cal.add("prodid", "-//Northeastern Open Swim Schedule//mxm.dk//")
    cal.add("version", "2.0")

    cal.add('X-WR-CALNAME', 'Northeastern Open Swim Schedule')  
    cal.add('X-WR-TIMEZONE', 'America/New_York')  
    cal.add('X-APPLE-CALENDAR-COLOR', '#1E90FF')  # DodgerBlue color

    timezone = pytz.timezone("America/New_York")

    for event in events:
        cal_event = Event()
        cal_event.add("summary", event["EventName"])
        start = datetime.strptime(event["EventStart"], "%Y-%m-%dT%H:%M:%S")
        end = datetime.strptime(event["EventEnd"], "%Y-%m-%dT%H:%M:%S")
        cal_event.add("dtstart", timezone.localize(start))
        cal_event.add("dtend", timezone.localize(end))
        cal_event.add("location", event["Location"])
        cal_event.add("uid", str(event["Id"]) + "@nuevents.neu.edu")
        cal_event.add("description", f"Location: {event['Location']}")
        cal.add_component(cal_event)

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "wb") as f:
        f.write(cal.to_ical())


if __name__ == "__main__":
    events = fetch_open_swim_events()
    create_ics_file(events, filename="calendars/open_swim_schedule.ics")
