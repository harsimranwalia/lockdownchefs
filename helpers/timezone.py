# import datetime as dt
# import googlemaps
# from datetime import datetime
# from .constants import GMAPS_APIKEY

# gmaps = googlemaps.Client(key=GMAPS_APIKEY)

def get_timezone_offset(time_from, time_to):
    # utc_now = datetime.datetime.utcnow()
    # date_today = str(datetime.date.today())
    # notif_time = datetime.datetime.strptime(date_today+" "+time_to, "%Y-%m-%d %H:%M")
    if time_to > time_from:
        tz_sign = "+"
        time_delta = time_to - time_from
    else:
        tz_sign = "-"
        time_delta = time_from - time_to
        
    time_delta_hrs = time_delta.seconds/3600
    tz = tz_sign + "0" + str(round(time_delta_hrs)) + ":00"
    if round(time_delta_hrs) < time_delta_hrs:
        tz = tz[:-2] + "30"
    
    return tz