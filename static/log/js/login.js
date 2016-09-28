from django.contrib.auth import authenticate, login

def login(request):
    if login_form.is_valid():
        user = authenticate(login_form.getElementsByName('username'), login_form.getElementsByName('password'))
        if user is not None:
            //user = login(request, login_form.get_user())
            return HttpResponseNotFound(request.REQUEST.get(request.GET.next))
        return HttpResponseForbidden() # catch invalid ajax and all non ajax
