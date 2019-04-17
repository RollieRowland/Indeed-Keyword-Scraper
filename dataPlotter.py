import plotly
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.plotly as py
import plotly.io as pio
import plotly.graph_objs as go
import os
import glob
import csv
import ntpath
import random
import numpy as np
from collections import defaultdict

skillCSV = "C:/Users/Rollie/Documents/GitHub/IndeedScraper/Salary.csv"#https://www.tiobe.com/tiobe-index/
citiesCSV = "C:/Users/Rollie/Documents/GitHub/IndeedScraper/cities.csv"
statePopulationCSV = "C:/Users/Rollie/Documents/GitHub/IndeedScraper/us-population-by-state-and-count.csv"
dataDirectory = "C:/Users/Rollie/Google Drive/School/Grad School/2019 Spring/Scholarship Seminar/Research Project (Scholarship Seminar)/Processed Data/LiveData2"

title = "Salary"
individualName = "Salary"

cityData = list(csv.reader(open(citiesCSV, encoding='utf-8'), delimiter=","))
statePopulationData = list(csv.reader(open(statePopulationCSV, encoding='utf-8'), delimiter=","))

nestedDict = lambda: defaultdict(nestedDict)

topSkills = nestedDict()
stateSkillsAll = nestedDict()
stateSkillsQueries = nestedDict()
Skills = []

minimumDisplayCount = 20

totalPopulation = 0

def getState(city):
    for row in cityData:
        if row[1].replace(" ", "") == city:
            return row[2]

    return "NOTFOUND"

def getStatePopulation(state):
    for i in range(len(statePopulationData[0])):
        if statePopulationData[0][i] in state:
            #print("State: " + state + " Population: " + statePopulationData[1][i])
            return int(statePopulationData[1][i])

def getTotalPopulation():
    sum = 0
    for i in range(len(statePopulationData[1])):
        sum = sum + int(statePopulationData[1][i])

    return sum

def getSkills():
    data = list(csv.reader(open(skillCSV, encoding='utf-8'), delimiter=","))

    for row in data[1::]:
        Skills.append(" " + row[0] + " ")

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

    for Skill in Skills:
        count = description.count(Skill)

        #print(state + " " + Skill + " " + str(count))

        stateSkillsAll[state][Skill] = stateSkillsAll.get(state, {}).get(Skill, 0) + count
        topSkills[Skill] = topSkills.get(Skill, 0) + count

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

    '''
    #population scaling
    sum = 0

    for y in range(len(yAxes)):
        scalar = totalPopulation / getStatePopulation(groupNames[y])

        print(groupNames[y] + ": " + str(scalar))

        for z in range(len(yAxes[y])):
            yAxes[y][z] = yAxes[y][z] * scalar
    '''

    statePopulations = []

    for i in groupNames:
        statePopulations.append(getStatePopulation(i))

    statePopulations, groupNames, xAxes, yAxes = (list(t) for t in zip(*sorted(zip(statePopulations, groupNames, xAxes, yAxes))))

    for i in range(len(groupNames)):
        #ci = int(255/len(groupNames)*i) # ci = "color index"

        state = []

        for k in range(len(groupNames)):
            state.append(groupNames[i])

        traces.append(go.Scatter3d(
            name=state[0],
            x=xAxes[i],
            z=yAxes[i],
            y=state,
            mode='markers',
            line=dict(
                width=1
            ),
            marker=dict(
                size=8,
                line=dict(
                    color='rgba(217, 217, 217, 0.14)',
                    width=0.5
                ),
                opacity=0.8
            )
        ))

    layout = go.Layout(
        title=name,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0
        ),
        scene = dict(
            xaxis = dict(
                title=xName),
            yaxis = dict(
                title='States'),
            zaxis = dict(
                title=yName),
        ),
    )

    fig = go.Figure(data=traces, layout=layout)

    plot(fig)

    return

def writeTopSkills():
    keys = []
    values = []

    sorted_topSkills = sorted(topSkills, key=topSkills.__getitem__, reverse=True)

    for k in sorted_topSkills:
        if topSkills[k] < minimumDisplayCount:
            sorted_topSkills.remove(k)

    for k in sorted_topSkills:
        v = topSkills[k]

        if v != 0:
            keys.append(k)
            values.append(v)

    createBarChart('Total Top ' + title, keys, values, 'Names', 'Total Counts', 'Total Top ' + title)
    createPieChart('Total Top ' + title, keys, values, 'Total Top ' + title)

def writeTopSkillsPerState():
    for k, v in stateSkillsAll.items():
        keys = []
        values = []

        sorted_topSkills = sorted(v, key=v.__getitem__, reverse=True)

        for s in sorted_topSkills:
            if topSkills[s] < minimumDisplayCount:
                sorted_topSkills.remove(s)

        for k2 in sorted_topSkills:
            v2 = v[k2]
            if v2 != 0:
                keys.append(k2)
                values.append(v2)

        createBarChart('Top ' + title + '_' + k, keys, values, 'Names', 'Total Counts', 'Top  ' + title + ' in ' + k)
        createPieChart('Top ' + title + '_' + k, keys, values, 'Top ' + title + ' in ' + k)

def writeTopSkillsPerStateOneChart():
    states = []
    Skills = []
    counts = []

    
    sorted_topSkills = sorted(topSkills, key=topSkills.__getitem__, reverse=True)

    for k in sorted_topSkills:
        if topSkills[k] < minimumDisplayCount:
            sorted_topSkills.remove(k)

    for k, v in stateSkillsAll.items():
        keys = []
        values = []

        for name in sorted_topSkills:
            v2 = v[name]

            keys.append(name)
            values.append(v2)

        states.append(k)
        Skills.append(keys)
        counts.append(values)

    createStackedChart('Top ' + title + ' Per State', Skills, counts, individualName, 'Total Counts', states, 'Top ' + title + ' Per State ')


if __name__ == '__main__':
    getSkills()

    filenames = []
    fileIndex = 0

    totalPopulation = getTotalPopulation()

    for filename in glob.glob(os.path.join(dataDirectory, '*.csv')):
        print(filename)
        filenames.append(filename)

    for filename in filenames[0::]:
        print(fileIndex)
        fileIndex += 1
        getCountsAll(filename)

    for k, v in stateSkillsAll.items():
        print(k)
        getStatePopulation(k)

        for k2, v2 in v.items():
            if v2 != 0:
                print(k2 + " " + str(v2))

    for k, v in topSkills.items():
        if v != 0:
            print(k + " " + str(v))

    if not os.path.exists('images'):
        os.mkdir('images')

    writeTopSkills()
    writeTopSkillsPerState()
    writeTopSkillsPerStateOneChart()
