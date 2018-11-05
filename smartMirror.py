# -*- coding: utf-8 -*-
import urllib.request, json, math, sys, datetime, calendar, icalendar, time, _thread, feedparser, random
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, pyqtSignal, QTimer, pyqtSlot, QVariantAnimation, QVariant
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
# from bson import json_util



#List of weather forecasts At first the current temp
#as second element the forecast for tomorrow at 13 o'clock and then the day after tomorrow...
weatherForecast = []

#List of information for the driving part
#first element is the normal duration to Tübingen, second is the delay
drivingInformation = []

#List of all upcoming events 
events = []

#List of greetings between 12am o'clock and 5pm o'clock
midd_day_greetings = ["Hello !", "Have a nice day :)", "Hola", "Bonjour !", "Bienvenidos :)"]

#List of greetings between 6am o'clock and 12am o'clock
morning_greetings = ["Good morning !", "I hope you slept well :)", "You look sleepy...", "Have a nice day :)"]

#List of greetings between 5pm o'clock and 6am o'clock
evenign_greetings = ["Good evening", "I hope you had a nice day:)", "Sleep well!", "Have a nice evening", "Good dreams :)"]


#False if http error occured
recieved_weather_data = True
#False if http error occured
recieved_driving_data = True
#False id http error occured
recieved_calendar_data = True





##########################################################################
#######################    WEATHER DATA      ##############################
###########################################################################
#Rottenbrug City id: 2843729
def computeWeatherData():
	#Clear old data
	del weatherForecast[:]

	#fetch new data
	with urllib.request.urlopen("http://api.openweathermap.org/data/2.5/forecast?id=2843729&units=metric&APPID=f9f8fe22830e3313a1fbc7cbcd5e97f4", timeout = 10) as url:
		weatherData = json.loads(url.read().decode())
		weatherData = weatherData['list']

		#----------------------------------------
		#fetch at least 5 days of forecast (all available data)

		#Just to find the middle temperature
		middleOfTheDay = datetime.time(13, 0 , 0) 

		#get first date in the weahter data
		firstDate = datetime.datetime.fromtimestamp(int(weatherData[0]['dt']))

		#append current weather as first item in list
		weatherForecast.append(weatherData[0])

		#append the next weatherforecasts at 13 o'clock for the following days
		for i in range(0, 39):
			currentDate = datetime.datetime.fromtimestamp(int(weatherData[i]['dt']))

			if currentDate.time() == middleOfTheDay and currentDate.date() != firstDate.date():
				weatherForecast.append(weatherData[i])
		#----------------------------------------
		print("Weather data fetched and processed")


###########################################################################
########################    DRIVING DATA     ##############################
###########################################################################
#BING MAPS REQUEST
def computeDrivingData():
	#Clear old data
	del drivingInformation[:]

	#fetch new data
	with urllib.request.urlopen("http://dev.virtualearth.net/REST/V1/Routes/Driving?wp.0=Rottenburg%20am%Neckar,%20Breitwiesenweg%206&wp.1=T%C3%BCbingen&avoid=minimizeTolls&key=AnvZ81ilKVD3h_znUyJlxWgJcrIWxqQr3nYIGtUtGiADuhoJ_OsGqLUVeWx8Nu3h", timeout = 10) as url:
		drivingData = json.loads(url.read().decode())
		distanceData = drivingData['resourceSets'][0]['resources'][0]['travelDistance']
		durationData = drivingData['resourceSets'][0]['resources'][0]['travelDuration']
		trafficDurationData = drivingData['resourceSets'][0]['resources'][0]['travelDurationTraffic']

		#first the normal time in mins to arrive
		drivingInformation.append(math.ceil(durationData/60))
		#second the delay time in mins
		drivingInformation.append(math.ceil(drivingInformation[0] - trafficDurationData/60))
		print("Driving data fetched and processed")



###########################################################################
########################    CALENDAR DATA    ##############################
###########################################################################
def computeCalendarData():
	#clear old data
	del events[:]
	#Save my main calendar as myCalendar.ical to dir
	urllib.request.urlretrieve("https://calendar.google.com/calendar/ical/guenthner.luk%40gmail.com/private-0641a5e381966e5ff241c90234fee166/basic.ics", "myCalendar.ical")
	print("Own calendar fetched")

	#Open the downloaded ical file
	file = open('myCalendar.ical', 'rb')
	#cast from ical to calendar object
	cal = icalendar.Calendar.from_ical(file.read())

	#Walk over every event
	for e in cal.walk('VEVENT'):
		get_events(e) #get events saves every future event in events[]

	file.close()


	#Now download national holidays and save as feiertage.ical
	urllib.request.urlretrieve('https://calendar.google.com/calendar/ical/de.german%23holiday%40group.v.calendar.google.com/public/basic.ics', "feiertage.ical")
	print("Feiertage fetched")


	file = open("feiertage.ical", "rb")
	cal = icalendar.Calendar.from_ical(file.read())
	for e in cal.walk('VEVENT'):
		get_events(e)
	file.close()

	#all events are fetched from the list now lets sort according to date and then time if date is the same
	events_sort()

	print("Calendar data is processed")
	#Just for debugging purposes
	# for i in range(0, len(events)-1):
	# 	print(events[i])




#gets int weekday returns german weekday string
def weekdayToGerman(int):
	if int == 0:
		return "Mo."
	elif int == 1:
		return "Di."
	elif int == 2:
		return "Mi."
	elif int == 3:
		return "Do."
	elif int == 4:
		return "Fr."
	elif int == 5:
		return "Sa."
	elif int == 6:
		return "So."

#Process the minute string (appends a 0 in front if leng=1)
def process_Minute(min):
	if len(str(min)) == 1:
		return "0" + str(min)
	else:
		return str(min)

#Process the summary if its to long add ...
def process_Summary(str):
	if len(str) > 16:
		return str[0:20] + "..."
	else:
		return str


#gets the current time and returns as nicly formatted string
def currentTime():
	now = datetime.datetime.now()

	rtr= weekdayToGerman(now.weekday())
	rtr += str(now.day) + "." + str(now.month)+ "  " + str(now.hour) + ":" + process_Minute(now.minute) + ":" + process_Minute(now.second)

	return rtr


#Function for Setting the alpha value of each pixel in a QImage
def setAlphaOfImg(img, alpha):
	out = img #Output Image
	for x in range(0, img.width()):						#iterate over each column
		for y in range(0, img.height()):				#iterate over each row
			c = img.pixel(x, y)							#get color at x, y
			colors = QtGui.QColor(c)					#cast to QColor
			colors.setAlpha(alpha)						#set alpha of current QColor
			out.setPixelColor(x, y, colors)				#set the Qcolor to x, y
	return out		#return new img


class AnimationLabel(QtWidgets.QLabel):
	def __init__(self, *args, **kwargs):
		QtWidgets.QLabel.__init__(self, *args, **kwargs)
		self.animation = QVariantAnimation()
		self.animation.valueChanged.connect(self.changeColor)

	@pyqtSlot(QVariant)
	def changeColor(self, color):
		palette = self.palette()
		palette.setColor(QtGui.QPalette.WindowText, color)
		self.setPalette(palette)

	def startFadeIn(self):
		self.animation.stop()
		self.animation.setStartValue(QtGui.QColor(0, 0, 0, 0))
		self.animation.setEndValue(QtGui.QColor(0, 0, 0, 255))
		self.animation.setDuration(2000)
		self.animation.setEasingCurve(QtCore.QEasingCurve.InBack)
		self.animation.start()

	def startFadeOut(self):
		self.animation.stop()
		self.animation.setStartValue(QtGui.QColor(0, 0, 0, 255))
		self.animation.setEndValue(QtGui.QColor(0, 0, 0, 0))
		self.animation.setDuration(2000)
		self.animation.setEasingCurve(QtCore.QEasingCurve.OutBack)
		self.animation.start()

	def startAnimation(self):
		print("starting an")
		self.startFadeOut()
		loop = QtCore.QEventLoop()
		self.animation.finished.connect(loop.quit)
		loop.exec_()
		QTimer.singleShot(2000, self.startFadeIn)



#Function to process the downloaded calender data and safe them in correct datetime form in the events list
def get_events(e):
	currentEvent = e['DTSTART'].dt

	if isinstance(currentEvent, datetime.datetime): #we have a datetime object!
		if currentEvent.date() >= datetime.date.today(): #Just get the events in the future
			currentEvent = e['DTSTART'].dt
			tempEvent = datetime.datetime.now()
			tempEvent = tempEvent.replace(currentEvent.year, currentEvent.month, currentEvent.day, currentEvent.hour, currentEvent.minute, second=0, microsecond=0)
			events.append([tempEvent, str(e['SUMMARY'])])

	#We have just have a date, add 1 as flag
	elif isinstance(currentEvent, datetime.date):
		#Just get events the future and maximal 30days later than today
		if currentEvent >= datetime.date.today() and currentEvent <= (datetime.date.today() + datetime.timedelta(days = 30)):
			currentEvent = e['DTSTART'].dt
			tempEvent = datetime.datetime.now()
			tempEvent = tempEvent.replace(currentEvent.year, currentEvent.month, currentEvent.day, hour=8, minute=0, second=0, microsecond=0)
			events.append([tempEvent, str(e['SUMMARY'])])				




#Function to sort the events list according to date and then to time
def events_sort():
	for j in range(len(events)):
		#initially swapped is false
		swapped = False
		i = 0

		while i<len(events)-1:
			#comparing the adjacent elements

			if events[i][0].date() > events[i+1][0].date():
				#swapping
				events[i], events[i+1] = events[i+1], events[i]
				#Changing the value of swapped
				swapped = True

			elif events[i][0].time() > events[i+1][0].time() and events[i][0].date() == events[i+1][0].date():
				#swapping
				events[i], events[i+1] = events[i+1], events[i]
				#Changing the value of swapped
				swapped = True

			i = i+1

		#if swapped is false then the list is sorted
		#we can stop the loop
		if swapped == False:
			break

#Function for randomly select a greeting according to the time
def greeting():
	current_time = datetime.datetime.now().hour

	if current_time >= 6 and current_time < 12:
		#Print Morning greetings
		return morning_greetings[random.randint(0, len(morning_greetings) -1)]
	elif current_time >= 12 and current_time < 17:
		#Print Midday greetings
		return midd_day_greetings[random.randint(0, len(morning_greetings) -1)]
	elif current_time >= 17 or current_time < 6:
		#Print evening greetings
		return evenign_greetings[random.randint(0, len(morning_greetings) -1)]

	


#Starts the whole program
def main():
	app = QtWidgets.QApplication(sys.argv)
	UI = Window()

	sys.exit(app.exec_())




#FUNCTION FOR STARTING THE DATA FETCH (funcion with try/except)
def fetchData():
	#Check if any http requeest throws an error
	try:
		computeWeatherData()
	except:
		print("Http execption for weather data") #Just for debugging purposes
		recieved_weather_data = False

	
	try:
		computeDrivingData()
	except:
		print("Http Eeecption for driving data") #Just for debugging purposes
		recieved_driving_data = False

	
	try:
		computeCalendarData()
	except:
		print("Http execption for calendar data")
		recieved_calendar_data = False






class Window(QtWidgets.QMainWindow):

	def __init__(self):
		super(Window, self).__init__()
		self.setWindowTitle("geheim")
		#self.setMinimumSize(1800, 450)
		

		def workerThread(foo, bar):
			fetchData()
			# self.greeting_text.startAnimation()
			self.updateInformation()

		#define timer
		self.timer = QTimer(self)
		#set intveral
		self.timer.setInterval(1000)

		self.timerCounter = 0

		#define the slot for each timer tick
		@QtCore.pyqtSlot()
		def timerTick():
			if recieved_calendar_data:
				#set the new time each second
				self.today_lbl.setText(currentTime())
				#incr the counter
				self.timerCounter += 1

				#if 108.000 seconds are gone we updatet the infromation (30min)
				if self.timerCounter == 100000:
					_thread.start_new_thread(workerThread, ("None", "None"))
					self.timerCounter = 0
					


		#connect the new slot to the timer timeout
		self.timer.timeout.connect(timerTick)
		#start the timer	
		self.timer.start()

		#Fetch data the first time
		fetchData()

		#init the UI
		self.initUI()

		self.updateInformation()

		newPalette = self.palette()
		newPalette.setColor(QtGui.QPalette.Window, Qt.black)
		self.setPalette(newPalette)

		# self.showFullScreen()
		self.show()
		


	#FUNCTOIN FOR UI INITIALIZATION
	def initUI(self):

		QtGui.QFontDatabase.addApplicationFont("HelveticaNeue-UltraLight.ttf")
		QtGui.QFontDatabase.addApplicationFont("weathericons-regular-webfont.ttf")

		#Central Widget
		self.centWid = QtWidgets.QWidget(self)
		self.setCentralWidget(self.centWid)

		#Define main Vertical Layout
		self.vBox = QtWidgets.QVBoxLayout()

		
		#Define Upper hBox row
		self.upperHbox = QtWidgets.QHBoxLayout()

		#Define central hBox row
		self.centralHbox = QHBoxLayout()

		self.bottomHbox = QHBoxLayout()

		#Upper left widget
		self.upperLeftWid = QtWidgets.QWidget(self)

		#Upper right widget
		self.upperRightWid = QtWidgets.QWidget(self)

		#Upper middle widget
		self.upperMidWid = QtWidgets.QWidget(self)

		#Central middle widget
		self.centralMidWid = QtWidgets.QWidget(self)

		#bottom middle widget
		self.bottomMidWid = QtWidgets.QWidget(self)

		#------------------------------------------------------------------------------------------------------------
		#-----------------Define Time and Calendar-------------------------------------------------------------------
		#------------------------------------------------------------------------------------------------------------

		self.cal_row_vBox = QVBoxLayout()

		self.time_hBox = QHBoxLayout()

		self.today_lbl = QtWidgets.QLabel(self)
		self.tempToday = datetime.datetime.now()
		self.today_lbl.setText(currentTime())
		self.today_lbl.setStyleSheet("font : 60px; font : bold; color : rgba(220, 220, 220, 250); font-family : HelveticaNeue-UltraLight")
		
		self.time_hBox.addWidget(self.today_lbl)


		if recieved_calendar_data:
			self.time_evnt_1_hbox = QHBoxLayout()
			self.time_evnt_1_date = QtWidgets.QLabel(self)
			self.time_evnt_1_evnt = QtWidgets.QLabel(self)

			self.time_evnt_1_date.setStyleSheet("font : 30px; color : rgba(220, 220, 220, 250); font-family : HelveticaNeue-UltraLight")			
			self.time_evnt_1_evnt.setStyleSheet("font : 25px; font : bold; color : rgba(220, 220, 220, 250); font-family : HelveticaNeue-UltraLight")

			self.time_evnt_1_hbox.addWidget(self.time_evnt_1_date)
			self.time_evnt_1_hbox.addWidget(self.time_evnt_1_evnt)

			#--------------Second Row--------------

			self.time_evnt_2_hbox = QHBoxLayout()
			self.time_evnt_2_date = QtWidgets.QLabel(self)
			self.time_evnt_2_evnt = QtWidgets.QLabel(self)

			self.time_evnt_2_date.setStyleSheet("font : 30px; color : rgba(220, 220, 220, 200); font-family : HelveticaNeue-UltraLight")
			self.time_evnt_2_evnt.setStyleSheet("font : 25px; font : bold; color : rgba(220, 220, 220, 200); font-family : HelveticaNeue-UltraLight")

			self.time_evnt_2_hbox.addWidget(self.time_evnt_2_date)
			self.time_evnt_2_hbox.addWidget(self.time_evnt_2_evnt)

			#--------------Third Row--------------

			self.time_evnt_3_hbox = QHBoxLayout()
			self.time_evnt_3_date = QtWidgets.QLabel(self)
			self.time_evnt_3_evnt = QtWidgets.QLabel(self)

			self.time_evnt_3_date.setStyleSheet("font : 30px; color : rgba(220, 220, 220, 150); font-family : HelveticaNeue-UltraLight")
			self.time_evnt_3_evnt.setStyleSheet("font : 25px; font : bold; color : rgba(220, 220, 220, 150); font-family : HelveticaNeue-UltraLight")

			self.time_evnt_3_hbox.addWidget(self.time_evnt_3_date)
			self.time_evnt_3_hbox.addWidget(self.time_evnt_3_evnt)

			#--------------Fourth Row--------------

			self.time_evnt_4_hbox = QHBoxLayout()
			self.time_evnt_4_date = QtWidgets.QLabel(self)
			self.time_evnt_4_evnt = QtWidgets.QLabel(self)

			self.time_evnt_4_date.setStyleSheet("font : 30px; color : rgba(220, 220, 220, 100); font-family : HelveticaNeue-UltraLight")
			self.time_evnt_4_evnt.setStyleSheet("font : 25px; font : bold; color : rgba(220, 220, 220, 100); font-family : HelveticaNeue-UltraLight")

			self.time_evnt_4_hbox.addWidget(self.time_evnt_4_date)
			self.time_evnt_4_hbox.addWidget(self.time_evnt_4_evnt)


			#Add all the rows and events and stuff
			self.cal_row_vBox.addLayout(self.time_hBox)
			self.cal_row_vBox.addLayout(self.time_evnt_1_hbox)
			self.cal_row_vBox.addLayout(self.time_evnt_2_hbox)
			self.cal_row_vBox.addLayout(self.time_evnt_3_hbox)
			self.cal_row_vBox.addLayout(self.time_evnt_4_hbox)
			self.cal_row_vBox.addStretch()


		else:
			self.fct_error = QtWidgets.QLabel()
			self.fct_error.setText("A http request error occured")
			self.fct_error.setStyleSheet("font : 30px; font : bold; color : rgba(250, 50, 50, 200); font-family : HelveticaNeue-UltraLight")
			self.cal_row_vBox.addWidget(self.fct_error)


		#Content margins (left, top, right, bottom)
		self.cal_row_vBox.setContentsMargins(30, 30, 0 , 0)
		self.upperLeftWid.setLayout(self.cal_row_vBox)


		#------------------------------------------------------------------------------------------------------------
		#-----------------Define Weather forecast--------------------------------------------------------------------
		#------------------------------------------------------------------------------------------------------------
		self.fct_row_vBox = QVBoxLayout()

		if recieved_weather_data:

			#FIRST ROW (Todays forecast)
			currentDay = datetime.datetime.fromtimestamp(int(weatherForecast[0]['dt']))
			self.fct_0_hBox = QHBoxLayout()

			#define text label0
			self.fct_0_text0 = QtWidgets.QLabel(self)
			self.fct_0_text0.setStyleSheet("font : 80px; color : rgba(220, 220, 220, 250); font-family : HelveticaNeue-UltraLight")
			self.fct_0_text0.setText(weekdayToGerman(currentDay.weekday()))

			#define text label0
			self.fct_0_text1 = QtWidgets.QLabel(self)
			self.fct_0_text1.setStyleSheet("font : 80px; color : rgba(220, 220, 220, 250); font-family : HelveticaNeue-UltraLight")

			#define icon label
			self.fct_0_icn = QtWidgets.QLabel(self)
			self.fct_0_icn.setPixmap(QtGui.QPixmap(str(weatherForecast[0]['weather'][0]['icon'] + ".png")))

			#add widgets to layout first icon then text
			self.fct_0_hBox.addWidget(self.fct_0_icn)
			self.fct_0_hBox.addWidget(self.fct_0_text0)
			self.fct_0_hBox.addStretch()
			self.fct_0_hBox.addWidget(self.fct_0_text1)

			#---------------------------------------------

			#Second ROW (next forecast)
			currentDay = datetime.datetime.fromtimestamp(int(weatherForecast[1]['dt']))
			self.fct_1_hBox = QHBoxLayout()

			#define text label
			self.fct_1_text0 = QtWidgets.QLabel(self)
			self.fct_1_text0.setStyleSheet("font : 70px; color : rgba(220, 220, 220, 200); font-family : HelveticaNeue-UltraLight")
			self.fct_1_text0.setText(weekdayToGerman(currentDay.weekday()))

			#define text label
			self.fct_1_text1 = QtWidgets.QLabel(self)
			self.fct_1_text1.setStyleSheet("font : 70px; color : rgba(220, 220, 220, 200); font-family : HelveticaNeue-UltraLight")

			#define icon label
			self.fct_1_icn = QtWidgets.QLabel(self)
			self.fct_1_img = QtGui.QPixmap(str(weatherForecast[1]['weather'][0]['icon'] + ".png")).toImage()
			self.fct_1_img = setAlphaOfImg(self.fct_1_img, 200)
			self.fct_1_icn.setPixmap(QtGui.QPixmap.fromImage(self.fct_1_img))

			#add widgets to layout first icon then text
			self.fct_1_spacer = QtWidgets.QSpacerItem(60, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding) 
			self.fct_1_hBox.addItem(self.fct_1_spacer)
			self.fct_1_hBox.addWidget(self.fct_1_icn)
			self.fct_1_hBox.addWidget(self.fct_1_text0)
			self.fct_1_hBox.addStretch()
			self.fct_1_hBox.addWidget(self.fct_1_text1)
			#---------------------------------------------

			#Third ROW (next forecast)
			currentDay = datetime.datetime.fromtimestamp(int(weatherForecast[2]['dt']))
			self.fct_2_hBox = QHBoxLayout()

			#define text label
			self.fct_2_text0 = QtWidgets.QLabel(self)
			self.fct_2_text0.setStyleSheet("font : 70px; color : rgba(220, 220, 220, 150); font-family : HelveticaNeue-UltraLight")
			self.fct_2_text0.setText(weekdayToGerman(currentDay.weekday()))

			#define text label
			self.fct_2_text1 = QtWidgets.QLabel(self)
			self.fct_2_text1.setStyleSheet("font : 70px; color : rgba(220, 220, 220, 150); font-family : HelveticaNeue-UltraLight")

			#define icon label
			self.fct_2_icn = QtWidgets.QLabel(self)
			self.fct_2_img = QtGui.QPixmap(str(weatherForecast[3]['weather'][0]['icon'] + ".png")).toImage()
			self.fct_2_img = setAlphaOfImg(self.fct_2_img, 150)
			self.fct_2_icn.setPixmap(QtGui.QPixmap.fromImage(self.fct_2_img))

			#add widgets to layout first icon then text
			self.fct_2_hBox.addItem(self.fct_1_spacer)
			self.fct_2_hBox.addWidget(self.fct_2_icn)
			self.fct_2_hBox.addWidget(self.fct_2_text0)
			self.fct_2_hBox.addStretch()
			self.fct_2_hBox.addWidget(self.fct_2_text1)

			#---------------------------------------------

			#Fourth ROW (next forecast)
			currentDay = datetime.datetime.fromtimestamp(int(weatherForecast[3]['dt']))
			self.fct_3_hBox = QHBoxLayout()

			#define text label
			self.fct_3_text0 = QtWidgets.QLabel(self)
			self.fct_3_text0.setStyleSheet("font : 70px; color : rgba(220, 220, 220, 100); font-family : HelveticaNeue-UltraLight")
			self.fct_3_text0.setText(weekdayToGerman(currentDay.weekday()))

			#define text label
			self.fct_3_text1 = QtWidgets.QLabel(self)
			self.fct_3_text1.setStyleSheet("font : 70px; color : rgba(220, 220, 220, 100); font-family : HelveticaNeue-UltraLight")

			#define icon label
			self.fct_3_icn = QtWidgets.QLabel(self)
			self.fct_3_img = QtGui.QPixmap(str(weatherForecast[3]['weather'][0]['icon'] + ".png")).toImage()
			self.fct_3_img = setAlphaOfImg(self.fct_3_img, 100)
			self.fct_3_icn.setPixmap(QtGui.QPixmap.fromImage(self.fct_3_img))


			#add widgets to layout first icon then text
			self.fct_3_hBox.addItem(self.fct_1_spacer)
			self.fct_3_hBox.addWidget(self.fct_3_icn)
			self.fct_3_hBox.addWidget(self.fct_3_text0)
			self.fct_3_hBox.addStretch()
			self.fct_3_hBox.addWidget(self.fct_3_text1)




			self.fct_row_vBox.addLayout(self.fct_0_hBox)
			self.fct_row_vBox.addLayout(self.fct_1_hBox)
			self.fct_row_vBox.addLayout(self.fct_2_hBox)
			self.fct_row_vBox.addLayout(self.fct_3_hBox)

		#Http error occured show error
		else:
			self.fct_error = QtWidgets.QLabel(self)
			self.fct_error.setText("A http request error occured")
			self.fct_error.setStyleSheet("font : 30px; font : bold; color : rgba(250, 50, 50, 200); font-family : HelveticaNeue-UltraLight")
			self.fct_row_vBox.addWidget(self.fct_error)
		

		#Content margins(left, top, right, bottom)
		self.fct_row_vBox.setContentsMargins(0, 30, 30, 0)
		self.upperRightWid.setLayout(self.fct_row_vBox)

		#------------------------------------------------------------------------------------------------------------
		#-----------------End weather forecast definition------------------------------------------------------------
		#------------------------------------------------------------------------------------------------------------



		#------------------------------------------------------------------------------------------------------------
		#-----------------Define driving time components-------------------------------------------------------------
		#------------------------------------------------------------------------------------------------------------

		#Rows layout manager
		self.trvl_vBox = QVBoxLayout()

		self.trvl_time_hBox = QHBoxLayout()
		self.trvl_inf_hBox = QHBoxLayout()

		self.trvl_time_text0 = QtWidgets.QLabel(self)
		self.trvl_time_text0.setStyleSheet("font : 30px; font : bold; color : rgba(220, 220, 220, 255); font-family : HelveticaNeue-UltraLight")

		#Check if http error occured
		if recieved_driving_data:

			self.trvl_time_text1 = QtWidgets.QLabel(self)
			self.trvl_time_text1.setStyleSheet("font : 30px; color : rgba(220, 220, 220, 255); font-family : HelveticaNeue-UltraLight")

			#Displays Minutes (2nd row)
			self.trvl_time_hBox.addStretch()
			self.trvl_time_hBox.addWidget(self.trvl_time_text1)
			self.trvl_time_hBox.addStretch()

		#error occured show error text
		else:
			self.trvl_error = QtWidgets.QLabel(self)
			self.trvl_error.setText("A http error occured")
			self.trvl_error.setStyleSheet("font : 30px; font : bold; color : rgba(250, 50, 50, 200); font-family : HelveticaNeue-UltraLight")
			self.trvl_time_hBox.addStretch()
			self.trvl_time_hBox.addWidget(self.trvl_error)
			self.trvl_time_hBox.addStretch()

		#Display text (1st row)
		self.trvl_inf_hBox.addStretch()
		self.trvl_inf_hBox.addWidget(self.trvl_time_text0)
		self.trvl_inf_hBox.addStretch()


		#Combines rows togehter
		self.trvl_vBox.addLayout(self.trvl_inf_hBox)
		self.trvl_vBox.addLayout(self.trvl_time_hBox)
		self.trvl_vBox.addStretch()

		#Content margins (left, top, right, bottom)
		self.trvl_vBox.setContentsMargins(0, 60, 0 , 0)


		self.upperMidWid.setLayout(self.trvl_vBox)



		#------------------------------------------------------------------------------------------------------------
		#-----------------End driving time components definition-----------------------------------------------------
		#------------------------------------------------------------------------------------------------------------


		#------------------------------------------------------------------------------------------------------------
		#-----------------Start Rss feed compontents definition------------------------------------------------------
		#------------------------------------------------------------------------------------------------------------
		self.rss_vBox = QVBoxLayout()

		self.rss_text = QtWidgets.QLabel(self)
		self.rss_text.setStyleSheet("font : 30px; font : bold; color : rgba(220, 220, 220, 255); font-family : HelveticaNeue-UltraLight")

		self.rss_vBox.addWidget(self.rss_text)
		#content margins (left,top, right, bottom)
		self.rss_vBox.setContentsMargins(0, 0, 0, 60)
		self.bottomMidWid.setLayout(self.rss_vBox)

		#------------------------------------------------------------------------------------------------------------
		#-----------------End Rss feed compontents definition------------------------------------------------------
		#------------------------------------------------------------------------------------------------------------

		#------------------------------------------------------------------------------------------------------------
		#-----------------Start greeting compontents definition------------------------------------------------------
		#------------------------------------------------------------------------------------------------------------
		self.greeting_vBox = QVBoxLayout()

		
		self.greeting_text = AnimationLabel(greeting())
		self.greeting_text.setStyleSheet("font : 45px; font : bold; color : rgba(220, 220, 220, 255); font-family : HelveticaNeue-UltraLight")
		

		self.greeting_vBox.addWidget(self.greeting_text)

		self.centralMidWid.setLayout(self.greeting_vBox)





		#Add left upper Corner
		self.upperHbox.addWidget(self.upperLeftWid)

		# #Stretch to middle and add middle
		self.upperHbox.addStretch()
		self.upperHbox.addWidget(self.upperMidWid)

		#Stretch to right corner and add Right corner
		self.upperHbox.addStretch()
		self.upperHbox.addWidget(self.upperRightWid)

		self.centralHbox.addStretch()
		self.centralHbox.addWidget(self.centralMidWid)
		self.centralHbox.addStretch()

		self.bottomHbox.addStretch()
		self.bottomHbox.addWidget(self.bottomMidWid)
		self.bottomHbox.addStretch()

		#Add Rows and Stretch
		self.vBox.addLayout(self.upperHbox)
		self.vBox.addStretch()
		self.vBox.addLayout(self.centralHbox)
		self.vBox.addStretch()
		self.vBox.addLayout(self.bottomHbox)


		#Set Layout of the central Widget and show that shit
		self.centWid.setLayout(self.vBox)
						


	#FUNCTION FOR UPDATING UI
	def updateInformation(self):
		#Travel information
		self.trvl_time_text0.setText("Fahrtzeit von Ergenzingen nach Tübingen")
		self.trvl_time_text1.setText(str(drivingInformation[0]) + " Minuten mit " + str(drivingInformation[1]) + " Minuten Verzögerung")

		#Weather information
		self.fct_3_text1.setText(str(weatherForecast[3]['main']['temp']) + "°C")
		self.fct_2_text1.setText(str(weatherForecast[2]['main']['temp']) + "°C")
		self.fct_1_text1.setText(str(weatherForecast[1]['main']['temp']) + "°C")
		self.fct_0_text1.setText(str(weatherForecast[0]['main']['temp']) + "°C")

		#Calendar Infromation
		if len(events) > 3:
			current_event = events[3]
			self.time_evnt_4_evnt.setText(process_Summary(current_event[1]))
			self.time_evnt_4_date.setText(weekdayToGerman(current_event[0].weekday()) + " " + str(current_event[0].day)+ "." +
					str(current_event[0].month) + "." + str(current_event[0].year)[2:4] +", " + str(current_event[0].hour) + ":" +
					process_Minute(current_event[0].minute) + " Uhr ")

		if len(events) > 2:
			current_event = events[2]
			self.time_evnt_3_evnt.setText(process_Summary(current_event[1]))
			self.time_evnt_3_date.setText(weekdayToGerman(current_event[0].weekday()) + " " + str(current_event[0].day)+ "." +
				str(current_event[0].month) + "." + str(current_event[0].year)[2:4] +", " + str(current_event[0].hour) + ":" +
				process_Minute(current_event[0].minute) + " Uhr ")

		if len(events) > 1:
			current_event = events[1]
			self.time_evnt_2_evnt.setText(process_Summary(current_event[1]))
			self.time_evnt_2_date.setText(weekdayToGerman(current_event[0].weekday()) + " " + str(current_event[0].day)+ "." +
				str(current_event[0].month) + "." + str(current_event[0].year)[2:4] +", " + str(current_event[0].hour) + ":" +
				process_Minute(current_event[0].minute) + " Uhr ")

		if len(events):
			current_event = events[0]
			self.time_evnt_1_evnt.setText(process_Summary(current_event[1]))
			self.time_evnt_1_date.setText(weekdayToGerman(current_event[0].weekday()) + " " + str(current_event[0].day)+ "." +
				str(current_event[0].month) + "." + str(current_event[0].year)[2:4] +", " + str(current_event[0].hour) + ":" +
				process_Minute(current_event[0].minute) + " Uhr ")

		#News feed
		self.rss_text.setText(feedparser.parse("https://www.theguardian.com/world/rss")["entries"][0]["title"])

		#Greeting
		

		
		print("Information on GUI is Updatet")
		print("")









#Anything is fetched and ready to be shown so lets do that
main()












