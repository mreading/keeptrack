from .models import Athlete, Coach

def athlete_privacy(current_user, log_owner):
    """---------------------------------------------------------
	 given the user who is trying to access the page, and the log owner,
     determine whether the action is allowed
	---------------------------------------------------------"""
    can_edit = True
    can_view = True

    if len(list(Coach.objects.filter(user=current_user))):
        return can_view, can_edit

    #if the current user is an athlete
    if len(list(Athlete.objects.filter(user=log_owner))) > 0:
        if current_user.id != log_owner.id:
            can_edit = False
            if log_owner.athlete_set.all()[0].log_private:
                can_view = False
    return can_view, can_edit
