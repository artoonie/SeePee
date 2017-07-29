import csv
from dateutil import parser
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pytz
import sys

def readPees(filename, tzString):
    pees = []
    tz = pytz.timezone(tzString)
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        reader.next() # skip first title row

        for row in reader:
            pees.append(parser.parse(row[0]).astimezone(tz))
    return pees

def isWeekday(pee):
    return pee.weekday() < 5
def returnOnlyWeekdays(pees):
    return [p for p in pees if isWeekday(p)]

def visPeeDiffsByDay(pees, ax):
    datesAll = []
    diffsAll = []
    colorMaps = []

    lastPee = pees[0]
    for pee in pees[1:]:
        peeDiff = pee - lastPee
        peeDiffHours = peeDiff.total_seconds()/60.0/60.0
        lastPee = pee
        if peeDiffHours < 24:
            # Ignore filters on the input list to skip weekends or something
            datesAll.append(pee)
            diffsAll.append(peeDiffHours)
            colorMaps.append(cm.magma(1 - pee.hour/24.0))

    ax.set_title("# hours between pees (white=morning, black=night)")
    ax.scatter(datesAll, diffsAll, s=20, c=colorMaps)


def _visWeekdayByData(dates, data, ax):
    assert len(data) == len(dates)

    weekendX = []
    weekendY = []
    weekdayX = []
    weekdayY = []

    for i in xrange(len(dates)):
        if not isWeekday(dates[i]):
            weekendX.append(dates[i])
            weekendY.append(data[i])
        else:
            weekdayX.append(dates[i])
            weekdayY.append(data[i])

    ax.scatter(weekendX, weekendY, c='red', s=30)
    ax.scatter(weekdayX, weekdayY, c='yellow', s=30)
    ax.set_title(ax.get_title() + "\n(weekdays=yellow, weekends=red)")

def visPeeDiffAverageByDay(pees, ax):
    lastDate = None
    lastPee = None
    listOfPeesToday = []

    dates = []
    averages = []

    def addPt(listOfPeesToday):
        avg = sum(listOfPeesToday) / float(len(listOfPeesToday))
        averages.append(avg)
        dates.append(lastDate)

    for p in pees:
        currDate = p.date()

        if currDate == lastDate:
            timeBetween = p - lastPee
            listOfPeesToday.append(timeBetween.total_seconds()/(60.0*60))
        else:
            numPeesToday = len(listOfPeesToday)
            if numPeesToday >= 2:
                addPt(listOfPeesToday)
                listOfPeesToday = []

        lastPee = p
        lastDate = currDate

    # Make sure to grab the last day, too
    addPt(listOfPeesToday)

    ax.set_title("Average # hours between pees per day")
    ax.plot(dates, averages)
    _visWeekdayByData(dates, averages, ax)

def visPeeCountByDay(pees, ax):
    lastDate = None
    dates = []
    peeCount = []

    for p in pees:
        currDate = p.date()
        if currDate != lastDate:
            dates.append(currDate)
            peeCount.append(1)
            lastDate = currDate
        else:
            peeCount[-1] += 1

    ax.set_title("Number of pees per day")
    ax.plot(dates, peeCount)
    _visWeekdayByData(dates, peeCount, ax)

def visPeesByHour(pees, ax):
    dates = []
    hours = []
    for p in pees:
        dates.append(p)
        hours.append(p.hour + p.minute/60.0)

    ax.set_title("Pees by hour")
    ax.scatter(dates, hours)

try:
    filename = sys.argv[1]
except IndexError:
    print "Usage: python seepee.py <filename-of-CSV>"
    sys.exit(-1)
tzString = "US/Pacific"
pees = readPees(filename, tzString)

datemin = pees[0].date()
datemax = pees[-1].date()

nextSubplotIdx = 1
def _makeAxis(yMax):
    global nextSubplotIdx

    ax = plt.subplot(2,2,nextSubplotIdx)
    ax.set_xlim([datemin, datemax])
    ax.set_ylim([0, yMax])
    ax.grid(color='gray', linestyle='-', linewidth=0.2)

    nextSubplotIdx += 1

    return ax

plt.figure(num="Pee & See Visualization (Timezone %s)" % tzString)
visPeeDiffsByDay      (pees, _makeAxis(20))
visPeeDiffAverageByDay(pees, _makeAxis(8))
visPeesByHour         (pees, _makeAxis(24))
visPeeCountByDay      (pees, _makeAxis(25))

# Seems to have no impact:
# weekdayPees = returnOnlyWeekdays(pees)

plt.show()
