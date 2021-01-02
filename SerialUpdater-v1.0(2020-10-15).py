from urllib.request import urlopen as uOpen
from bs4 import BeautifulSoup as bSoup
import sys
from io import StringIO
import re
import csv
import time


# **********************************************


def urlParser(my_url, parserType):
    urlHTML = uOpen(my_url)
    page_html = urlHTML.read()
    urlHTML.close()
    PParser = bSoup(page_html, parserType)
    return PParser


# **********************************************


def sortContainers(containers, lastUpdateEpi):
    tempNINI = {}
    StopUpdate = 'n'
    for eContainer in containers:
        try:
            # print(eContainer[0])

            # print(eContainer[0])
            SerialName = eContainer[0].findAll(
                "h3", {"class": "vw-post-box__title"})[0].a.text.lstrip()
            print(SerialName)

            SerialLink = eContainer[0].a["href"]
            # print(SerialLink)

            EpisodePage = urlParser(SerialLink, "html.parser")

            # print(EpisodePage)
            EpiContainer = EpisodePage.findAll(
                "div", {"class": "vw-post-content clearfix"})
            # print(EpiContainer[0].find_all({'iframe': 'src'}))
            ipart = 0
            for iframe in EpiContainer[0].find_all({'iframe': 'src'}):
                sLink = iframe["src"].replace(",", "|")
                print(sLink)
                if sLink[:4] != 'http':
                    EpiImagePage = urlParser('https:' + sLink, "html.parser")
                else:
                    EpiImagePage = urlParser(sLink, "html.parser")

                EpiImageContainer = EpiImagePage.findAll("script")
                # print(EpiImageContainer[8])
                # print(eContainer)

                try:
                    GetImgLink = str(str(EpiImageContainer[8]).split('"poster_url":"')[
                                         1]).split('"')[0].replace('\\', '')  # + ".jpg"

                except:
                    GetImgLink = 'https://raw.githubusercontent.com/pravanjam/TamilSerialz/master/NoPic.jpg'

                if all(substr in sLink for substr in ['dailymotion']):
                    SerialUID = (sLink.split('/video/')
                                 )[1].split('?autoplay')[0]
                    print(SerialUID)
                    ipart = ipart + 1
                    EpiUID = SerialName.strip().replace("–", "-") + " " + str(ipart)

                    EpiImage = GetImgLink
                    print(EpiUID)
                    # print(EpiImage)
                    # print(lastUpdateEpi)
                    if EpiUID == lastUpdateEpi.strip():
                        # print("vignvig")
                        StopUpdate = "y"
                        return [tempNINI, StopUpdate]
                    else:
                        tempNINI.update({str(EpiUID): [SerialUID, EpiImage]})
        except:
            pass

    return [tempNINI, StopUpdate]


# ************************************************
start_time = time.time()

MasterSerialList = uOpen(
    'https://raw.githubusercontent.com/pravanjam/TamilSerialz/master/Master_Serial_List.csv')
dataMst = StringIO(MasterSerialList.read().decode('ascii', 'ignore'))
dreader = csv.reader(dataMst)
Serial_Mst = []
SerialMeta = []

for row in dreader:
    Serial_Mst.append(row)

for SerialListID in range(1, len(Serial_Mst)):
    # print(Serial_Mst[SerialListID][1])
    SerialMeta.append({'SearchID': Serial_Mst[SerialListID][1],
                       'bkURL': Serial_Mst[SerialListID][2],
                       'Genre': Serial_Mst[SerialListID][3],
                       'VideoData': []})

# print(SerialMeta)
lastUpdateEpi = 'none'
for MetaID in range(0, len(SerialMeta)):

    bkdata = uOpen(SerialMeta[MetaID]['bkURL'])
    datafile = StringIO(bkdata.read().decode('ascii', 'ignore'))
    dreader = csv.reader(datafile)
    data = []

    for row in dreader:
        data.append(row)
        # print(data)

    for epi in range(1, len(data)):
        SerialMeta[MetaID]['VideoData'].append({'name': data[epi][0],
                                                'thumb': data[epi][1],
                                                'video': data[epi][2],
                                                'genre': data[epi][3]})

    lastUpdateEpi = data[-1][0]
    print(lastUpdateEpi)
    baseurl = 'https://www.tamiltwistya.com/'
    my_url = baseurl + '?s=' + SerialMeta[MetaID]['SearchID']
    print(my_url)
    PParser = urlParser(my_url, "html.parser")

    try:
        TotalPages = PParser.findAll("a", {"class": "page-numbers"})
        if len(TotalPages) >= 1:
            pagenumber = int(TotalPages[len(TotalPages) - 2].text)
        else:
            pagenumber = 1
        print(pagenumber)
    except:
        pagenumber = 1

    NINI = {}
    StopUpdate = 'n'
    for i in range(0, pagenumber):
        try:
            if pagenumber > 1:
                my_url = baseurl + 'page/' + \
                         str(i + 1) + '/?s=' + SerialMeta[MetaID]['SearchID']
            else:
                my_url = baseurl + 'page/' + \
                         str(i + 1) + '/?s=' + SerialMeta[MetaID]['SearchID']

            PParser = urlParser(my_url, "html.parser")

            ulcontainers = PParser.findAll(
                "div", {"class": "vw-flex-grid__item"})

            print(len(ulcontainers))

            containers = []
            for ulCC in range(len(ulcontainers)):
                # print(ulCC)
                containers.append(ulcontainers[ulCC].findAll(
                    "div", {"class": "vw-post-box__inner"}))

            print("page " + str(i + 1))
            tempNINI, StopUpdate = sortContainers(containers, lastUpdateEpi)
            NINI.update(tempNINI)

            if StopUpdate == 'y':
                break
        except:
            pass
    NINIKEYS = list(NINI.keys())
    NINIKEYS.reverse()
    for epi in NINIKEYS:
        SerialMeta[MetaID]['VideoData'].append({'name': epi,
                                                'thumb': NINI[epi][1],
                                                'video': 'plugin://plugin.video.dailymotion_com/?url=' + NINI[epi][
                                                    0] + '&mode=playVideo',
                                                'genre': SerialMeta[MetaID]['Genre']})

# VIDEOS = {'Naam Iruvar Namku Iruvar': SerialMeta[0]['VideoData'], 'Siva Manasula Sakthi' : SerialMeta[1]['VideoData'], 'Arundhati' : SerialMeta[2]['VideoData']}
VIDEOS = {}
filename = []
for SerialListID in range(1, len(Serial_Mst)):
    VIDEOS.update({Serial_Mst[SerialListID][0]: SerialMeta[SerialListID - 1]['VideoData']})
    filename.append(Serial_Mst[SerialListID]
                    [0].replace(" ", "") + "_SerialData.csv")

# filename = ["NaamIruvar_SerialData.csv", "SivaMaasula_SerialData.csv", "Arundhati_SerialData.csv"]
# print(filename)
for fileid in range(0, len(filename)):
    f = open(filename[fileid], "w")
    headers = "Serial Episode, Thumbnail Link, Video Link, Genre\n"
    f.write(headers)

    NI_VIDEO = SerialMeta[fileid]['VideoData']
    for k in range(0, len(NI_VIDEO)):
        f.write(NI_VIDEO[k]['name'].replace(",", "|") + "," + NI_VIDEO[k]['thumb'].replace(",", "|") +
                "," + NI_VIDEO[k]['video'].replace(",", "|") + "," + NI_VIDEO[k]['genre'].replace(",", "|") + "\n")

    f.close()
