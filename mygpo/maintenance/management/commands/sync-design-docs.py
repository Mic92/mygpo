import os.path

from django.conf import settings
from django.core.management.base import BaseCommand
from couchdbkit.loaders import FileSystemDocsLoader

from mygpo.core.models import Podcast



class Command(BaseCommand):
    """ Sync design docs from filesystem """

    def handle(self, *args, **options):

        for part in ('general', 'user'):
            path = os.path.join(settings.BASE_DIR, '..', 'couchdb', part, '_design')
            db = Podcast.get_db()
            loader = FileSystemDocsLoader(path)
            loader.sync(db, verbose=True)

