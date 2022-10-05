from govapp import emails
from django.core.management.base import BaseCommand
from django.conf import settings
from confy import env, database
import requests
import json

class Command(BaseCommand):
    help = 'Test email'

    def add_arguments(self, parser):
          parser.add_argument('-t' '--to', type=str , help='To Email Address')

    def handle(self, *args, **options):
         to_arg = options['t__to']
         # add variables into the email.
         context= {'test' :  'test'}
         cc = None
         bcc = None
         from_email='no-reply@dbca.wa.gov.au'
         template_group='pvs'

         emails.sendHtmlEmail([to_arg],'Test Email',context,'email/test-body.html',cc,bcc,from_email,template_group,attachments=None)   

         
