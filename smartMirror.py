# -*- coding: utf-8 -*-
import urllib.request, json, math, sys, datetime, calendar
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout

#List of weather forecasts At first the current temp
#as second element the forecast for tomorrow at 13 o'clock and then the day after tomorrow...
weatherForecast = []

#List of information for the driving part
#first element is the normal duration to Tübingen, second is the delay
drivingInformation = []

#False if http error occured
recieved_weather_data = True
#False if http error occured
recieved_driving_data = True

class Window(QtWidgets.QMainWindow):
	def __init__(self):
		super(Window, self).__init__()
		self.setWindowTitle("geheim")
		self.initUI()


		newPalette = self.palette()
		newPalette.setColor(QtGui.QPalette.Window, Qt.black)
		self.setPalette(newPalette)
		
		# self.showFullScreen()
		self.show()
		

	def initUI(self):

		QtGui.QFontDatabase.addApplicationFont("HelveticaNeue-UltraLight.ttf")
		QtGui.QFontDatabase.addApplicationFont("weathericons-regular-webfont.ttf")

		#Central Widget
		centWid = QtWidgets.QWidget(self)
		self.setCentralWidget(centWid)

		#Define main Vertical Layout
		vBox = QtWidgets.QVBoxLayout()

		#Define Upper hBox row
		upperHbox = QtWidgets.QHBoxLayout()

		#Upper left widget
		upperLeftWid = QtWidgets.QWidget(self)

		#Upper right widget
		upperRightWid = QtWidgets.QWidget(self)

		#Upper middle widget
		upperMidWid = QtWidgets.QWidget(self)



		#------------------------------------------------------------------------------------------------------------
		#-----------------Define Weather forecast--------------------------------------------------------------------
		#------------------------------------------------------------------------------------------------------------
		fct_row_vBox = QVBoxLayout()

		if recieved_weather_data:

			#FIRST ROW (Todays forecast)
			currentDay = datetime.datetime.fromtimestamp(int(weatherForecast[0]['dt']))
			fct_0_hBox = QHBoxLayout()

			#define text label
			fct_0_text = QtWidgets.QLabel()
			fct_0_text.setStyleSheet("font : 80px; color : rgba(220, 220, 220, 250); font-family : HelveticaNeue-UltraLight")
			fct_0_text.setText(weekdayToGerman(currentDay.weekday()) + " " + str(weatherForecast[0]['main']['temp']) + "°C")

			#define icon label
			fct_0_icn = QtWidgets.QLabel()
			fct_0_icn.setPixmap(QtGui.QPixmap(str(weatherForecast[0]['weather'][0]['icon'] + ".png")))

			#add widgets to layout first icon then text
			fct_0_hBox.addWidget(fct_0_icn)
			fct_0_hBox.addWidget(fct_0_text)

			#---------------------------------------------

			#Second ROW (next forecast)
			currentDay = datetime.datetime.fromtimestamp(int(weatherForecast[1]['dt']))
			fct_1_hBox = QHBoxLayout()

			#define text label
			fct_1_text = QtWidgets.QLabel()
			fct_1_text.setStyleSheet("font : 70px; color : rgba(220, 220, 220, 200); font-family : HelveticaNeue-UltraLight")
			fct_1_text.setText(weekdayToGerman(currentDay.weekday()) + " " + str(weatherForecast[1]['main']['temp']) + "°C")

			#define icon label
			fct_1_icn = QtWidgets.QLabel()
			fct_1_img = QtGui.QPixmap(str(weatherForecast[1]['weather'][0]['icon'] + ".png")).toImage()
			fct_1_img = setAlphaOfImg(fct_1_img, 200)
			fct_1_icn.setPixmap(QtGui.QPixmap.fromImage(fct_1_img))

			#add widgets to layout first icon then text
			fct_1_spacer = QtWidgets.QSpacerItem(60, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding) 
			fct_1_hBox.addItem(fct_1_spacer)
			fct_1_hBox.addWidget(fct_1_icn)
			fct_1_hBox.addStretch(1)
			fct_1_hBox.addWidget(fct_1_text)

			#---------------------------------------------

			#Third ROW (next forecast)
			currentDay = datetime.datetime.fromtimestamp(int(weatherForecast[2]['dt']))
			fct_2_hBox = QHBoxLayout()

			#define text label
			fct_2_text = QtWidgets.QLabel()
			fct_2_text.setStyleSheet("font : 65px; color : rgba(220, 220, 220, 150); font-family : HelveticaNeue-UltraLight")
			fct_2_text.setText(weekdayToGerman(currentDay.weekday()) + " " + str(weatherForecast[2]['main']['temp']) + "°C")

			#define icon label
			fct_2_icn = QtWidgets.QLabel()
			fct_2_img = QtGui.QPixmap(str(weatherForecast[3]['weather'][0]['icon'] + ".png")).toImage()
			fct_2_img = setAlphaOfImg(fct_2_img, 150)
			fct_2_icn.setPixmap(QtGui.QPixmap.fromImage(fct_2_img))

			#add widgets to layout first icon then text
			fct_2_hBox.addItem(fct_1_spacer)
			fct_2_hBox.addWidget(fct_2_icn)
			fct_2_hBox.addStretch(1)
			fct_2_hBox.addWidget(fct_2_text)

			#---------------------------------------------

			#Fourth ROW (next forecast)
			currentDay = datetime.datetime.fromtimestamp(int(weatherForecast[3]['dt']))
			fct_3_hBox = QHBoxLayout()

			#define text label
			fct_3_text = QtWidgets.QLabel()
			fct_3_text.setStyleSheet("font : 65px; color : rgba(220, 220, 220, 100); font-family : HelveticaNeue-UltraLight")
			# fct_3_text.setText(calendar.day_name[currentDay.weekday()][0:3] + ", " + str(weatherForecast[3]['main']['temp']) + "°C")
			fct_3_text.setText(weekdayToGerman(currentDay.weekday()) + " " + str(weatherForecast[3]['main']['temp']) + "°C")

			#define icon label
			fct_3_icn = QtWidgets.QLabel()
			fct_3_img = QtGui.QPixmap(str(weatherForecast[3]['weather'][0]['icon'] + ".png")).toImage()
			fct_3_img = setAlphaOfImg(fct_3_img, 100)
			fct_3_icn.setPixmap(QtGui.QPixmap.fromImage(fct_3_img))


			#add widgets to layout first icon then text
			fct_3_hBox.addItem(fct_1_spacer)
			fct_3_hBox.addWidget(fct_3_icn)
			fct_3_hBox.addStretch(1)
			fct_3_hBox.addWidget(fct_3_text)




			fct_row_vBox.addLayout(fct_0_hBox)
			fct_row_vBox.addLayout(fct_1_hBox)
			fct_row_vBox.addLayout(fct_2_hBox)
			fct_row_vBox.addLayout(fct_3_hBox)

		#Http error occured show error
		else:
			fct_error = QtWidgets.QLabel()
			fct_error.setText("A http request error occured")
			fct_error.setStyleSheet("font : 30px; font : bold; color : rgba(250, 50, 50, 200); font-family : HelveticaNeue-UltraLight")
			fct_row_vBox.addWidget(fct_error)
		

		#Content margins(left, top, right, bottom)
		fct_row_vBox.setContentsMargins(0, 30, 30, 0)
		upperRightWid.setLayout(fct_row_vBox)

		#------------------------------------------------------------------------------------------------------------
		#-----------------End weather forecast definition------------------------------------------------------------
		#------------------------------------------------------------------------------------------------------------



		#------------------------------------------------------------------------------------------------------------
		#-----------------Define driving time components-------------------------------------------------------------
		#------------------------------------------------------------------------------------------------------------

		#Rows layout manager
		trvl_vBox = QVBoxLayout()

		trvl_time_hBox = QHBoxLayout()
		trvl_inf_hBox = QHBoxLayout()

		trvl_time_text0 = QtWidgets.QLabel()
		trvl_time_text0.setText("Fahrtzeit von Ergenzingen nach Tübingen")
		trvl_time_text0.setStyleSheet("font : 30px; font : bold; color : rgba(220, 220, 220, 255); font-family : HelveticaNeue-UltraLight")

		#Check if http error occured
		if recieved_driving_data:

			trvl_time_text1 = QtWidgets.QLabel()
			trvl_time_text1.setText(str(drivingInformation[0]) + " Minuten mit " + str(drivingInformation[1]) + " Minuten Verzögerung")
			trvl_time_text1.setStyleSheet("font : 30px; color : rgba(220, 220, 220, 255); font-family : HelveticaNeue-UltraLight")

			#Displays Minutes (2nd row)
			trvl_time_hBox.addStretch()
			trvl_time_hBox.addWidget(trvl_time_text1)
			trvl_time_hBox.addStretch()

		#error occured show error text
		else:
			trvl_error = QtWidgets.QLabel()
			trvl_error.setText("A http error occured")
			trvl_error.setStyleSheet("font : 30px; font : bold; color : rgba(250, 50, 50, 200); font-family : HelveticaNeue-UltraLight")
			trvl_time_hBox.addStretch()
			trvl_time_hBox.addWidget(trvl_error)
			trvl_time_hBox.addStretch()

		#Display text (1st row)
		trvl_inf_hBox.addStretch()
		trvl_inf_hBox.addWidget(trvl_time_text0)
		trvl_inf_hBox.addStretch()


		#Combines rows togehter
		trvl_vBox.addLayout(trvl_inf_hBox)
		trvl_vBox.addLayout(trvl_time_hBox)
		trvl_vBox.addStretch()

		#Content margins (left, top, right, bottom)
		trvl_vBox.setContentsMargins(0, 40, 0 , 0)


		upperMidWid.setLayout(trvl_vBox)

		#------------------------------------------------------------------------------------------------------------
		#-----------------End driving time components definition-----------------------------------------------------
		#------------------------------------------------------------------------------------------------------------



		#Add left upper Corner
		upperHbox.addWidget(upperLeftWid)

		# #Stretch to middle and add middle
		upperHbox.addStretch(1)
		upperHbox.addWidget(upperMidWid)

		#Stretch to right corner and add Right corner
		upperHbox.addStretch(1)
		upperHbox.addWidget(upperRightWid)

		#Add Rows and Stretch
		vBox.addLayout(upperHbox)
		vBox.addStretch(1)


		#Set Layout of the central Widget and show that shit
		centWid.setLayout(vBox)
		

def main():
	app = QtWidgets.QApplication(sys.argv)
	UI = Window()
	sys.exit(app.exec_())

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








###########################################################################
#######################    WEATHER DATA      ##############################
###########################################################################
#Rottenbrug City id: 2843729
def computeWeatherData():
	with urllib.request.urlopen("http://api.openweathermap.org/data/2.5/forecast?id=2843729&units=metric&APPID=f9f8fe22830e3313a1fbc7cbcd5e97f4") as url:
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


###########################################################################
########################    DRIVING DATA     ##############################
###########################################################################
#BING MAPS REQUEST
def computeDrivingData():
	with urllib.request.urlopen("http://dev.virtualearth.net/REST/V1/Routes/Driving?wp.0=Rottenburg%20am%Neckar,%20Breitwiesenweg%206&wp.1=T%C3%BCbingen&avoid=minimizeTolls&key=AnvZ81ilKVD3h_znUyJlxWgJcrIWxqQr3nYIGtUtGiADuhoJ_OsGqLUVeWx8Nu3h") as url:
		drivingData = json.loads(url.read().decode())
		distanceData = drivingData['resourceSets'][0]['resources'][0]['travelDistance']
		durationData = drivingData['resourceSets'][0]['resources'][0]['travelDuration']
		trafficDurationData = drivingData['resourceSets'][0]['resources'][0]['travelDurationTraffic']

		#first the normal time in mins to arrive
		drivingInformation.append(math.floor(durationData/60))
		#second the delay time in mins
		drivingInformation.append(math.floor(trafficDurationData/60 - drivingInformation[0]))




#Start program here

#Check if any http requeest throws an error
#Weeather error?
try:
	computeWeatherData()
except:
	print("Http Execption for Weather data") #Just for debugging purposes
	recieved_weather_data = False


try:
	computeDrivingData()
except:
	print("Http Execption for Driving data") #Just for debugging purposes
	recieved_driving_data = False


#Anything is
main()
