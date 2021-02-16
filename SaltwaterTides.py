
from datetime import date, datetime, timedelta
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from re import split as resplit
from sys import argv
from urllib import request

args = argv

site = "Virginia"
station_number = "8637624"

yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d').split('-')

year = yesterday[0]
month = yesterday[1]
start_date = yesterday[2]

maximum_days = "3"

if(len(args) > 1):
	if(int(args[1]) < 30 and int(args[1]) > 0):
		maximum_days = args[1]

payload = [
	"site=" + site,
	"station_number=" + station_number,
	"month=" + month,
	"year=" + year,
	"start_date=" + start_date,
	"maximum_days=" + maximum_days
]

url = "https://www.saltwatertides.com/cgi-bin/virginia.cgi"

req =  request.Request(url, data='&'.join(payload).encode('UTF-8'))
resp = request.urlopen(req)
resp_body = resplit("<PRE>\nDay".encode('UTF-8'), resp.read())[1]
resp_body = resplit("\n\n</PRE>\n<P>\nReturn".encode('UTF-8'), resp_body)[0]
resp_body = resp_body.decode('UTF-8')

resp_lines = resp_body.split('\n')

raw_headers = resp_lines[:2]
headers_line1 = raw_headers[0].split()
headers_line2 = raw_headers[1].split() 
headers = [x + y for x,y in zip(headers_line1, headers_line2)]
headers = ["Weekday", "Day"] + headers
headers = headers[:-1] + ["MoonTime", "%MoonVisible"]

# headers: Weekday Day High/Low TideTime TideHeight SunRise/Set MoonRise/Set Moon%

raw_tides = resp_lines[3:]
tides = []

for tide in raw_tides:
	if len(tide.split()) > 1:
		tides.append(tide)

current_day = raw_tides[0].split()[0].strip()
tides = [x.replace(" AM", "AM") for x in tides]
tides = [x.replace(" PM", "PM") for x in tides]
tides = [x.split() for x in tides]

weekdays = ['M', 'Tu', 'W', 'Th', 'F', 'Sa', 'Su']

filtered_tides = []
for tide in tides:
	if tide[0] in weekdays:
		current_day = tide[0]
		filtered_tides.append(tide)
	else:
		filtered_tides.append([current_day]+tide)

tides = [x[:5] for x in filtered_tides]
tide_times = [x[1] + ":" + x[3] for x in tides]

def modifyTime(x):
	date = ""
	hours = ""
	minutes = ""
	
	if "PM" in x:
		x = x.replace("PM","")
		date = x.split(':')[0]
		hours = str(int(x.split(':')[1]) + 12)
		if hours == "24":
		    hours = "12"
		minutes = x.split(':')[2]
	else:
	    x = x.replace("AM","")
	    date = x.split(':')[0]
	    hours = x.split(':')[1]
	    if hours == "12":
	        hours = "0"
	    minutes = x.split(':')[2]
	return date + ":" + hours + ":" + minutes

tide_times = [modifyTime(x) for x in tide_times]
tide_heights = [float(x[4]) for x in tides]

right_now = datetime.today().strftime('%d:%H:%M')

fig, ax = plt.subplots(1)
plt.axvline(x=right_now, linewidth=2, color="red")
plt.plot(tide_times, tide_heights)
plt.show()
