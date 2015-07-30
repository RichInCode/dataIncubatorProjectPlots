import zipfile, urllib2, csv
import requests
import wget
import datetime
import matplotlib.pyplot as plt
import pandas
import glob

def generateDateList():
    time_list = []
    start_time = datetime.datetime(2013,7,1)
    end_time = datetime.datetime(2015,2,1)
    time_list.append(start_time)
    next_time = start_time
    while next_time < end_time:
        try:
            next_time = datetime.datetime(next_time.year, next_time.month+1,1)
        except ValueError:
            next_time = datetime.datetime(next_time.year+1, 1, 1)
        time_list.append(next_time)


    return time_list
    

def download_files():
    date_list = generateDateList()
    file_list = []
    
    for date in date_list:
        year = date.strftime('%Y')
        month = date.strftime('%m')
        
        url = 'https://s3.amazonaws.com/tripdata/'+year+month+'-citibike-tripdata.zip'

        print url

        file_name = wget.download(url)
        file_list.append(file_name)

    return file_list

def unzip_files(file_list):  
    unzipped_file_list = []
    for item in file_list:
        fh = open(item, 'rb')
        z = zipfile.ZipFile(fh)
        
        for name in z.namelist():
            z.extract(name, ".")
            unzipped_file_list.append(z)
        fh.close()
    return unzipped_file_list

def createDicts(file_list):
    dfList = []
    for item in file_list:
        result = pandas.read_csv(item)
        dfList.append(result)
    return dfList

def computeNumberOfRidesPerMonth(dfList):
    ridesList_male = []
    ridesList_female = []
    ridesList_other = []
    for item in dfList:
        ridesList_male.append( item[item['gender']==1]['tripduration'].count() )
        ridesList_female.append( item[item['gender']==2]['tripduration'].count() )
        ridesList_other.append( item[item['gender']==0]['tripduration'].count() )

    return ridesList_male, ridesList_female, ridesList_other

def plotRidesPerMonth(x, ym, yf, yo):
    plt.figure(2)
    fig, ax = plt.subplots()
    ax.plot(x, ym, 'bs', label='males')
    ax.plot(x, yf, 'r^', label='females')
    ax.plot(x, yo, 'g*', label='unknown')
    legend = ax.legend(loc='upper right', shadow=True)
    plt.ylabel('number of rides')
    plt.xlabel('date')
    plt.savefig('plot2.pdf')

def createLocationDataFrame(x):
    df = pandas.concat(x)
    df = df[df['start station latitude']==df['end station latitude']]
    df = df[df['start station longitude']==df['end station longitude']]

    stationDict = {}
    stationLatDict = {}
    stationLongDict = {}

    for row_index, row in df.iterrows():
        try:
            stid = df.iloc[row_index]['start station id']
        except IndexError:
            continue
        if stid in stationDict.keys():
            stationDict[stid] += 1
        else:
            stationDict[stid] = 1

        stationLatDict[stid] = df.iloc[row_index]['start station latitude']
        stationLongDict[stid] = df.iloc[row_index]['start station longitude']

    sortedRides = []
    sortedLats = []
    sortedLongs = []
    colorBinList = []
    for key in sorted(stationDict):
        sortedRides.append(float(stationDict[key]))
        sortedLats.append(float(stationLatDict[key]))
        sortedLongs.append(float(stationLongDict[key]))
                            
    plt.figure(1)
    plt.scatter(sortedLats, sortedLongs, c=sortedRides, s=50)
    plt.gray()
    plt.ylabel('station latitude')
    plt.xlabel('station longitude')
    plt.savefig('plot1.pdf')

def createMonthList(x):
    X = []
    for item in x:
        print item
        try:
            X.append(datetime.datetime(int(item[7:11]),int(item[12:14]),1))
        except ValueError:
            print item
            X.append(datetime.datetime(int(item[7:11]),int(item[11:13]),1))

    return X

def createFileList():
    return glob.glob("./data/*.csv")

def projectProposal():
    #file_list = download_files()
    #unzipped_file_list = unzip_files(file_list)
    unzipped_file_list = createFileList()
    print unzipped_file_list
    dictLists = createDicts(unzipped_file_list)
    monthList = createMonthList(unzipped_file_list)
    ridesList_male, ridesList_female, ridesList_other = computeNumberOfRidesPerMonth(dictLists)
    plotRidesPerMonth(monthList, ridesList_male, ridesList_female, ridesList_other)
    createLocationDataFrame(dictLists)
    plt.show()
    
projectProposal()
