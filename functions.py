def minutes(str): # hh:mm --> mm
    if str == 'None': return ''
    split = str.split(':')
    return int(split[0]) * 60 + int(split[1])