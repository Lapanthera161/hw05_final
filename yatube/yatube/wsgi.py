"""
WSGI config for yatube project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

project_home = '/home/lapanthera/hw0w05_final/yatube/'

if project_home not in sys.path:
    sys.path.insert(0, project_home)
os.environ['DJANGO_SETTINGS_MODULE'] = 'yatube.settings'   
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yatube.settings')

application = get_wsgi_application()
