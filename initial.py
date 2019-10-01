from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time
import playsound
import speech_recognition as sr
import pyttsx3  #https://pypi.org/project/pyttsx3/ reference for modifications
import pytz
import subprocess

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
# DAYS = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
MONTHS = ["january", "february", "march", "april", "may", "june","july", "august", "september","october", "november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]

# Using pyttsx3 to recongnize sppech
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Getting audio
def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception: " + str(e))

    return said

# Authentication on google
def authenticate_google():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'clients_secrets_2.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service
    

# Getting events from user
def get_events(day, service):
	    # Call the Calendar API
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day.")

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])  # get the hour the event starts
            start_time = str(start.split("T")[1].split("-")[0])
            if int(start_time.split(":")[0]) < 12:   # if the event is in the morning
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0])-12)  # convert 24 hour time to regular
                start_time = start_time + "pm"

            speak(event["summary"] + " at " + start_time)

# Getting date from user
def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    if month < today.month and month != -1:  
        year = year+1

    
    if month == -1 and day != -1:  
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7

        return today + datetime.timedelta(dif)

    if day != -1:  
        return datetime.date(month=month, day=day, year=year)

def note(text):   #Making a note using notepad 
	date = datetime.datetime.now()
	file_name = str(date).replace(":", "-") + "-note.txt"
	with open(file_name, "w") as f:
		f.write(text)
	subprocess.Popen(["notepad.exe", file_name])

	# other options(sublime and atom)-
	# sublime = "D:\New folder\Sublime Text 3\sublime_text.exe"
	# atom = "C:\Users\Asus\AppData\Local\atom\atom.exe"
	# subprocess.Popen([sublime, file_name])
	# subprocess.Popen([atom, file_name])


# note("notepad is working")


#Main part of code
SERVICE = authenticate_google()
print("Start")
print("To ask about events use these: " + "\n\t what do i have, do i have plans, am i busy, what are my events on, events on, events i have")
print("To make notes use these: "+"\n\t make a note, remember this, remind me to, write this down, note this")
text = get_audio().lower()

#Defining various phrases to get events
CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy", "what are my events on", "events on"]
for phrase in CALENDAR_STRS:
    if phrase in text:
        date = get_date(text)
        if date:
            get_events(date, SERVICE)
        else:
            speak("Please Try Again")


#Make a note
NOTE_STRS = ["make a note", "remember this", "remind me to", "write this down", "note this"]	
for phrase in NOTE_STRS:
    if phrase in text:
        speak("What would you like me to write down? ")
        write_down = get_audio()
        note(write_down)
        speak("I've made a note of that.")


