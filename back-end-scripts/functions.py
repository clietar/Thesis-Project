def minutes(str): # hh:mm --> mm
    if str == 'None': return ''
    split = str.split(':')
    return int(split[0]) * 60 + int(split[1])

def minutes_to_string(time): # mm --> hh:mm
    h = int(time/60)
    mins = time % 60
    if mins < 10:
        string =  str(h)+':0'+str(mins)
    else : string =  str(h)+':'+str(mins)
    return string
