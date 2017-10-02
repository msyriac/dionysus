from weather import Weather


def is_str_in_list(text,alist):
    for item in alist:
        if item in text: return True
    return False

def is_it_nice_out(woeid):
    weather = Weather()
    lookup = weather.lookup(woeid)
    condition = lookup.condition()

    
    bad_weather = ['Rain','Thunderstorms','Showers']
    cold_temp = 64

    outside = condition['text'].strip()
    temp = int(condition['temp'])

    if not(is_str_in_list(outside,bad_weather)) and temp>=cold_temp:
        return True, outside, temp
    else:
        return False, outside, temp


def test_weather():
    # woeid = 2476729
    # print is_it_nice_out(woeid)        

    import numpy as np
    N = 1000
    for i in range(N):
        woeid = np.random.randint(100000)
        #print woeid
        try:
            is_it, outside, temp = is_it_nice_out(woeid)
            print is_it, outside,temp
        except:
            pass
