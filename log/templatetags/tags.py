from django import template

register = template.Library()

@register.filter(name='format_pace')
def format_pace(duration):
    if duration == None:
        return '-'

    s = duration.seconds
    hours = s // 3600
    s = s - (hours * 3600)
    minutes = s // 60
    seconds = str(s - (minutes * 60))
    if len(seconds) == 1:
        seconds = '0' + seconds
    return '%s:%s' % (minutes, seconds)

@register.filter(name='format_units')
def format_units(unit):
    if unit == "Miles":
        return " mi"
    return " k"
