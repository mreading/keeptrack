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
    seconds = s - (minutes * 60)
    return '%s:%s' % (minutes, seconds)
