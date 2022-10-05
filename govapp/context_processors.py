from django.conf import settings
from govapp import models
from django.core.cache import cache
import json

def variables(request):
    session_id = request.COOKIES.get('sessionid', None)
    is_authenticated = False
    if request.user.is_authenticated is True:
        is_authenticated = request.user.is_authenticated

    return {
        'template_group' : 'parks',
        'template_title' : '',
    }

