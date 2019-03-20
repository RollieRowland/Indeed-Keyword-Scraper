import plotly.plotly as py
import plotly.io as pio
import plotly.graph_objs as go
import os
import glob
import csv
import ntpath
import random
from collections import defaultdict

programmingHardSkillCSV = "C:/Users/Rollie/Documents/GitHub/IndeedScraper/hardskills.csv"#https://www.tiobe.com/tiobe-index/
citiesCSV = "C:/Users/Rollie/Documents/GitHub/IndeedScraper/cities.csv"
dataDirectory = "C:/Users/Rollie/Google Drive/School/Grad School/2019 Spring/Scholarship Seminar/Research Project (Scholarship Seminar)/Processed Data/LiveData2"

cityData = list(csv.reader(open(citiesCSV, encoding='utf-8'), delimiter=","))

nestedDict = lambda: defaultdict(nestedDict)

topHardSkills = nestedDict()
stateHardSkillsAll = nestedDict()
stateHardSkillsQueries = nestedDict()
HardSkills = []

minimumDisplayCount = 100

def getState(city):
    for row in cityData:
        if row[1].replace(" ", "") == city:
            return row[2]

    return "NOTFOUND"

def getHardSkills():
    data = list(csv.reader(open(programmingHardSkillCSV, encoding='utf-8'), delimiter=","))

    for row in data[1::]:
        HardSkills.append(" " + row[0] + " ")

def getCountsAll(filename):
    data = list(csv.reader(open(filename, encoding='utf-8'), delimiter=","))

    description = ''

    for row in data:
        description += str(row[11])

    nameSplit = ntpath.basename(filename).split('_')
    cityName = nameSplit[1]
    query    = nameSplit[2].split('.')[0]
    state = getState(cityName)

    #print(state + " " + cityName + " " + query)

    for HardSkill in HardSkills:
        count = description.count(HardSkill)

        #print(state + " " + HardSkill + " " + str(count))

        stateHardSkillsAll[state][HardSkill] = stateHardSkillsAll.get(state, {}).get(HardSkill, 0) + count
        topHardSkills[HardSkill] = topHardSkills.get(HardSkill, 0) + count

def createBarChart(filename,xAxis,yAxis,xName,yName,name):
    trace1 = go.Bar(
        text=list(yAxis),
        textposition = 'auto',
        x=list(xAxis),
        y=list(yAxis)
    )

    layout = go.Layout(
        barmode='group',
        title=name,
        xaxis=dict(
            title=xName
        ),
        yaxis=dict(
            title=yName
        )
    )

    data = [trace1]
    fig = go.Figure(data=data, layout=layout)

    img_bytes = pio.to_image(fig, format='PNG', width=1600, height=960, scale=2)

    if not os.path.exists('images/bar'):
        os.mkdir('images/bar')

    with open('images/bar/' + filename + '.PNG', 'wb') as f:
        f.write(img_bytes)
    return

def createPieChart(filename,xAxis,yAxis,name):
    trace1 = go.Pie(
        labels=list(xAxis),
        values=list(yAxis)
    )

    layout = go.Layout(
        title=name
    )

    data = [trace1]
    fig = go.Figure(data=data, layout=layout)

    img_bytes = pio.to_image(fig, format='PNG', width=1600, height=960, scale=2)

    if not os.path.exists('images/pie'):
        os.mkdir('images/pie')

    with open('images/pie/' + filename + '.PNG', 'wb') as f:
        f.write(img_bytes)
    return

def createStackedChart(filename,xAxes,yAxes,xName,yName,groupNames,name):
    traces = []

    rl = random.sample(range(256), len(xAxes))
    gl = random.sample(range(256), len(xAxes))
    bl = random.sample(range(256), len(xAxes))

    for i in range(len(xAxes)):
        r = rl[i]
        g = gl[i]
        b = bl[i]
        traces.append(go.Bar(
            x=list(xAxes[i]),
            y=list(yAxes[i]),
            name=groupNames[i],
            marker=dict(
                color='rgb(' + str(r) + ',' + str(g) + ',' + str(b) + ')',
            )
        ))

    layout = go.Layout(
        barmode='stack',
        title=name,
        xaxis=dict(
            title=xName
        ),
        yaxis=dict(
            title=yName
        )
    )

    fig = go.Figure(data=traces, layout=layout)

    img_bytes = pio.to_image(fig, format='PNG', width=1600, height=960, scale=2)

    if not os.path.exists('images/stackBar'):
        os.mkdir('images/stackBar')

    with open('images/stackBar/' + filename + '.PNG', 'wb') as f:
        f.write(img_bytes)
    return

def writeTopHardSkills():
    keys = []
    values = []

    sorted_topHardSkills = sorted(topHardSkills, key=topHardSkills.__getitem__, reverse=True)

    for k in sorted_topHardSkills:
        if topHardSkills[k] < minimumDisplayCount:
            sorted_topHardSkills.remove(k)

    for k in sorted_topHardSkills:
        v = topHardSkills[k]

        if v != 0:
            keys.append(k)
            values.append(v)

    createBarChart('TotalTopHardSkills', keys, values, 'Names', 'Total Counts', 'Total Top Hard Skills')
    createPieChart('TotalTopHardSkills', keys, values, 'Total Top Hard Skills')

def writeTopHardSkillsPerState():
    for k, v in stateHardSkillsAll.items():
        keys = []
        values = []

        sorted_topHardSkills = sorted(v, key=v.__getitem__, reverse=True)

        for s in sorted_topHardSkills:
            if topHardSkills[s] < minimumDisplayCount:
                sorted_topHardSkills.remove(s)

        for k2 in sorted_topHardSkills:
            v2 = v[k2]
            if v2 != 0:
                keys.append(k2)
                values.append(v2)

        createBarChart('TopHardSkills_' + k, keys, values, 'Names', 'Total Counts', 'Top Hard Skills in ' + k)
        createPieChart('TopHardSkills_' + k, keys, values, 'Top Hard Skills in ' + k)

def writeTopHardSkillsPerStateOneChart():
    states = []
    HardSkills = []
    counts = []

    sorted_topHardSkills = sorted(topHardSkills, key=topHardSkills.__getitem__, reverse=True)

    for k in sorted_topHardSkills:
        if topHardSkills[k] < minimumDisplayCount:
            sorted_topHardSkills.remove(k)

    for k, v in stateHardSkillsAll.items():
        keys = []
        values = []

        for name in sorted_topHardSkills:
            v2 = v[name]

            keys.append(name)
            values.append(v2)

        states.append(k)
        HardSkills.append(keys)
        counts.append(values)

    createStackedChart('TopHardSkillsPerState', HardSkills, counts, 'Names', 'Total Counts', states, 'Top Hard Skills Per State ')


if __name__ == '__main__':
    getHardSkills()

    filenames = []
    fileIndex = 0

    for filename in glob.glob(os.path.join(dataDirectory, '*.csv')):
        print(filename)
        filenames.append(filename)

    for filename in filenames[0::]:
        print(fileIndex)
        fileIndex += 1
        getCountsAll(filename)

    for k, v in stateHardSkillsAll.items():
        print(k)

        for k2, v2 in v.items():
            if v2 != 0:
                print(k2 + " " + str(v2))

    for k, v in topHardSkills.items():
        if v != 0:
            print(k + " " + str(v))

    if not os.path.exists('images'):
        os.mkdir('images')

    writeTopHardSkills()
    writeTopHardSkillsPerState()
    writeTopHardSkillsPerStateOneChart()
