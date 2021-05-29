import requests
import logging
import pandas as pd
import datetime, time

API_KEY = "174314"
PHN_NUMBER = "+919182290293"
PREV_TIME = time.time()

def startLogging():
    with open('info.log', 'w'):
        pass
    logging.basicConfig(level=logging.DEBUG, filename='info.log')
    logging.debug("This will be logged!")


def sendMessage(msg):
    req = "https://api.callmebot.com/signal/send.php?"
    req += "phone=+919182290293"
    req += "&" + "apikey=" + API_KEY
    req += "&" + "text=" + msg
    logging.info("Making Request...")
    reply = requests.api.request("GET", req)
    logging.info(reply)


def loadDistricts(path='data/district_mapping.csv'):
    dists = pd.read_csv(path)
    data = [dists['district id'], dists['district name'].apply(lambda x: x.lower())]
    headers = ["ID", "district"]
    return pd.concat(data, axis=1, keys=headers)


def getDistrictID(data, district):
    dist_id = data.loc[data['district'] == district]['ID'].values[0]
    return str(dist_id)


def cowinAPIExec(url):
    response = None
    global PREV_TIME
    while True:
        if(time.time() - PREV_TIME >= 3.05):
            PREV_TIME = time.time()
            break
    try:
        tm = time.time()
        response = requests.api.request("GET", url)
        logging.info("Time taken for coWin API request : " + str(time.time() - tm))
    except:
        pass
    if(response is not None):
        return response.json()
    return response


def getURLByDist(dist_id, date):
    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?"
    url += "district_id=" + dist_id
    url += "&date=" + date
    return url


def getCowinDataByDistrict(dist_data, district="hyderabad"):
    dist_id = getDistrictID(dist_data, district)
    date = datetime.date.today().strftime("%d-%m-%Y")
    url = getURLByDist(dist_id, date)
    return cowinAPIExec(url)


def checkAvailability(vaccine_centers, prev_count):
    count = 0
    for center in vaccine_centers:
        if(center['available_capacity_dose1'] > 0):
            count += 1

    if(count == prev_count):
        pass
    else:
        msg = "First dose is available in " + str(count) + " centers."
        sendMessage(msg)
    return count

def main():
    startLogging()
    prev_count = 0
    availability_state = False
    dists = loadDistricts()
    while True:
        if(availability_state and prev_count == 0):
            try:
                sendMessage("Slots Filled ;)")
            except:
                logging.error("Couldn't send Message!")
            availability_state = False

        try:
            vaccine_centers = getCowinDataByDistrict(dists)['sessions']
            prev_count = checkAvailability(vaccine_centers, prev_count)
            logging.info(str(prev_count) + " centers are found")
        except:
            pass

        if(prev_count > 0):
            availability_state = True

if(__name__ == "__main__"):
    main()