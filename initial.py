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
import webbrowser
import smtplib
import ssl 
import random
import pyjokes
from getpass import getpass


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
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

    return said.lower()

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
    print("hello")
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
                start_time = str(int(start_time.split(":")[0])-12) + start_time.split(":")[1] # convert 24 hour time to regular
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




#Making a note using notepad
def note(text):    
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




#Greeting as per time
def greetme():
	current_time = int(datetime.datetime.now().hour)
	if (current_time >= 0 and current_time < 12):
		speak("Good morning")
	elif (current_time >= 12 and current_time < 18):
		speak("Good afternoon")
	elif(current_time >= 18 and current_time != 0):
		speak("good evening")




#Opening webpages 
def open_website(text):
	chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s' #Opening tabs in chrome 
	if 'open youtube' in text:
		speak("okay")
		webbrowser.get(chrome_path).open('youtube.com')
	elif 'open google' in text:
		speak("okay")
		webbrowser.get(chrome_path).open('google.com')
	elif 'open gmail' in text:
		speak("okay")
		webbrowser.get(chrome_path).open('gmail.com')
	elif 'open reddit' in text:
		speak("okay")
		webbrowser.get(chrome_path).open('reddit.com')
	elif 'open github' in text:
		speak("okay")
		webbrowser.get(chrome_path).open('github.com')



#Sending E-mail
def send_email():
	speak("Who is the sender?")
	sender_email = input("Enter your mail id : ")
	extension = "@gmail.com"
	sender_email = sender_email + extension
	speak("Enter senders password: ")
	sender_pass = getpass("Enter your password : ")
	speak("wanna check password? say yes or no")
	check = get_audio()
	if yes in check:
		print(sender_pass)
	s = smtplib.SMTP('smtp.gmail.com', 587) 
	# start TLS for security 
	s.ehlo()
	s.starttls()
	s.ehlo()
	speak("Who is the receipient?")
	receiver_email = input("Enter receivers mail id : ")
	receiver_email = receiver_email + extension
	speak("What would you like me send?")
	message = input("Content: ")
	# Authentication 
	s.login(sender_email, sender_pass)
	s.sendmail(sender_email, receiver_email, message)
	# terminating the session
	speak("mail sent")
	s.quit() 

			

			
#Play music
def music():
	music_folder = r'C:\Users\Asus\Desktop\personal\music'
	music = ['1', '2', '3', '4', '5', '6']
	random_music = music_folder + '\\' + random.choice(music) + '.mp3'
	os.system(random_music)
	speak("Here is your music")
    


#Tell random jokes        
def joke():
	speak(pyjokes.get_joke())




#Main part of code
SERVICE = authenticate_google()
greetme()
speak("hello i am flexa your digital assistant")
speak("how may i help you")
print("To wake me up say : listen")
print("To ask about events use these : " + "\n\t what do i have, do i have plans, am i busy, what are my events, events on, events i have")
print("To make notes use these : " + "\n\t make a note, remember this, remind me to, write this down, note this")
print("To end the conversation use these : " + "\n\t goodbye, bye-bye, quit, quit program, end program, close program, end convo")
print("To open webpages use these : " + "\n\t open youtube, open google, open gmail, open reddit, open github")
print("To play music use these : " + "\n\t play music, play something, i am bored")
print("To hear a joke use these : " + "\n\t tell a joke, say something funny, humour me")
print("To send a email use these : " + "\n\t send email, send message")


#Defining the wakeup part 
WAKE = "listen"
while (True):
    print("\nListening")
    text = get_audio()
    
    if text.count(WAKE) > 0:
        speak("hi sahej")
        speak("I am ready")
        text = get_audio()

        CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy", "what are my events", "events on", "events i have"]
        for phrase in CALENDAR_STRS:
            if phrase in text:
                date = get_date(text)
                if date:
                    get_events(date, SERVICE)
                else:
                    speak("I don't understand")

        NOTE_STRS = ["make a note", "remember this", "remind me to", "write this down", "note this"]
        for phrase in NOTE_STRS:
            if phrase in text:
                speak("What would you like me to write down?")
                note_text = get_audio()
                note(note_text)
                speak("I've made a note of that.")

        QUIT_STRS = ["goodbye", "bye-bye", "quit program", "quit", "end program", "close program", "end convo"]
        for phrase in QUIT_STRS:
            if phrase in text:
            	speak("goodbye")
            	exit()

        WEBPAGE_STRS = ["open youtube", "open google", "open gmail", "open reddit", "open github"]
        for phrase in WEBPAGE_STRS:
        	if phrase in text:
        		open_website(text)
        		speak("done")
        
        EMAIL_STRS = ["send email", "send message"]
        for phrase in EMAIL_STRS:
        	if phrase in text:
        		send_email()

        MUSIC_STRS = ["play music", "play something", "i am bored"]
        for phrase in MUSIC_STRS:
        	if phrase in text:
        		music()

        JOKES_STRS = ["tell a joke", "say something funny", "humour me"]
        for phrase in JOKES_STRS:
        	if phrase in text:
        		joke()