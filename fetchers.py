import requests                                   # makes the web request to download the feed
from icalendar import Calendar                    # reads the .ics calendar format

SOURCES = {                                                                  # dict: {display name: feed URL}
    "AWS User Group Kolkata": "https://www.meetup.com/awsugkol/events/ical/",          # the one you tested (empty right now)
    "AWS Kolkata Group": "https://www.meetup.com/aws-kolkata-group/events/ical/",      # second AWS page found in search
    "GDG Kolkata": "https://www.meetup.com/GDG-Kolkata/events/ical/",                  # Google Developer Group Kolkata
}


def fetch_ical_events(name, url):                 # downloads one feed and returns its events as a clean list of dicts
    response = requests.get(                      # GET = download something
        url,
        timeout=15,                               # don't wait forever if the site is slow
        headers={"User-Agent": "Mozilla/5.0 (event-notifier-bot)"},  # tells the site who we are; some sites reject requests with no User-Agent
    )
    response.raise_for_status()                   # crash loudly on errors like 404 (wrong URL) or 403 (blocked)

    calendar = Calendar.from_ical(response.content)  # parse the raw .ics bytes into a Calendar object

    events = []                                   # we'll collect the cleaned events here
    for item in calendar.walk("VEVENT"):          # walk() loops over every item of type VEVENT, which is what iCal calls an event
        events.append({                           # convert each messy iCal item into a simple dict
            "id": str(item.get("UID")),           # UID = unique ID of the event. We'll use it later to remember "already notified"
            "title": str(item.get("SUMMARY")),    # event name
            "start": item.get("DTSTART").dt,      # start date/time; .dt gives a real Python date object
            "link": str(item.get("URL", "")),     # event page link; "" if the event has none
            "source": name,                       # which group it came from
        })
    return events                                 # hand the list back to whoever called this function


if __name__ == "__main__":                        # runs only with `python fetchers.py`, not when main.py imports this file
    for source_name, source_url in SOURCES.items():  # loop over every source we defined
        print(f"--- {source_name} ---")            # header so output is readable
        for event in fetch_ical_events(source_name, source_url):  # fetch and loop through events
            print(event["start"], "|", event["title"], "|", event["link"])  # print one line per event