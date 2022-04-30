import requests
import sched
import time
import logging
import webbrowser
from win10toast_click import ToastNotifier
import PIL.Image
import os


CREW_NAME = 'BlackPinkBp'


event_schedule = sched.scheduler(time.time, time.sleep)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename='check_crew_spaces.log', encoding='utf-8', level=logging.DEBUG)


def open_url():
    try:
        url_crewname = CREW_NAME.lower().replace(" ", "_")
        webbrowser.open_new(f'https://socialclub.rockstargames.com/crew/{url_crewname}/wall') 
    except Exception as e:
        logging.warning(f'Failed to open URL: {type(e)}: {e}.')


def check_for_space_in_crew():

    URL = f'https://scapi.rockstargames.com/search/crew?sort=&crewtype=all&includeCommentCount=true&pageSize=30&searchTerm={CREW_NAME}'
    REQ_HEADER = {'x-requested-with': 'XMLHttpRequest'}
    
    # get HTML response in JSON format
    req = requests.get(URL, headers=REQ_HEADER)
    data = req.json()

    for crew in data['crews']:

        numMembers = crew['memberCount']
        crewName = crew["crewName"]
        crewIdNo = crew['crewId']
        
        URL_IMG = f'https://prod.cloud.rockstargames.com/crews/sc/2206/{crewIdNo}/publish/emblem/emblem_128.png'

        if crewName.lower() == CREW_NAME.lower():

            if int(numMembers) == 1000:
                logging.info(f'Crew {crewName} is full at {numMembers} members.')

            elif int(numMembers) < 1000:
                logging.info(f'Crew {crewName} has {numMembers} members - sending alert.')
            
                # download crew logo
                if not os.path.isfile(f'{crewName}_emblem.ico'):
                    req_img = requests.get(URL_IMG)
                    with open(f'{crewName}_emblem.png', 'wb') as f:
                        f.write(req_img.content)

                    img = PIL.Image.open(f'{crewName}_emblem.png')
                    img.save(f'{crewName}_emblem.ico')

                # send notification
                toaster = ToastNotifier()
                toaster.show_toast(
                    f'Free space in the {crewName} crew!',
                    f'Currently at {numMembers} members - click to join.',
                    icon_path=f'{crewName}_emblem.ico', duration=None, threaded=True, callback_on_click=open_url)

                # remove icon files
                if os.path.exists(f'{crewName}_emblem.png'):
                    os.remove(f'{crewName}_emblem.png')

    # repeat every 30 seconds
    event_schedule.enter(30, 1, check_for_space_in_crew)

event_schedule.enter(0, 1, check_for_space_in_crew)
event_schedule.run()
