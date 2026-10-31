import json                                          # built-in: read and write JSON files
import sys                                           # built-in: lets us read words typed after "python main.py" (like "test")
from pathlib import Path                             # built-in: a cleaner way to work with file paths

from fetchers import SOURCES, fetch_ical_events      # from our own fetchers.py: the source list and the feed reader
from notify import send_message                      # from our own notify.py: sends a Telegram message

SEEN_FILE = Path("seen_events.json")                 # the bot's memory: IDs of events it already told you about


def load_seen():                                     # reads the memory file into a set
    if SEEN_FILE.exists():                           # on the very first run the file doesn't exist yet
        return set(json.loads(SEEN_FILE.read_text()))  # read text -> JSON list -> Python set (a set is fast for "is X in here?" checks)
    return set()                                     # no file = nothing seen yet


def save_seen(seen):                                 # writes the memory back to disk
    SEEN_FILE.write_text(json.dumps(sorted(seen), indent=2))  # sets can't go into JSON, so convert to a sorted list; indent=2 keeps it readable


def format_event(event):                             # turns one event dict into the text you'll see on Telegram
    return (
        f"🆕 {event['title']}\n"                     # \n = new line
        f"🗓 {event['start']}\n"                      # start date/time
        f"📍 {event['source']}\n"                     # which group posted it
        f"🔗 {event['link']}"                         # link to register
    )


def get_all_events():                                # collects events from every source
    if len(sys.argv) > 1 and sys.argv[1] == "test":  # sys.argv is the list of words typed: "python main.py test" -> ["main.py", "test"]
        return [{                                    # test mode: return one fake event so we can try the pipeline end to end
            "id": "test-1",
            "title": "TEST: Kolkata Tech Meetup",
            "start": "2026-11-20 18:00",
            "link": "https://example.com",
            "source": "Test source",
        }]

    all_events = []                                  # real mode: collect everything here
    for name, url in SOURCES.items():                # loop over every source in fetchers.py
        try:                                         # try/except: if one source fails, we keep going instead of crashing everything
            all_events.extend(fetch_ical_events(name, url))  # extend adds all of that source's events to the big list
        except Exception as error:                   # catches any error: 404, timeout, blocked, etc.
            print(f"Skipping {name}: {error}")       # log it and move on to the next source
    return all_events


def main():                                          # the whole bot in 8 lines
    seen = load_seen()                               # 1. load memory
    new_events = [e for e in get_all_events() if e["id"] not in seen]  # 2. list comprehension: keep only events whose ID we haven't seen
    print(f"Found {len(new_events)} new event(s)")   # 3. tell us what happened (visible in logs later)
    for event in new_events:                         # 4. handle each new event
        send_message(format_event(event))            # 5. send it to Telegram
        seen.add(event["id"])                        # 6. remember it
        save_seen(seen)                              # 7. save after EACH send, so a crash halfway can't cause duplicate alerts next time


if __name__ == "__main__":                           # only runs when you execute this file directly
    main()