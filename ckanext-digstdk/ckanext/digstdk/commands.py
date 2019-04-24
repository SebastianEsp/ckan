import json
import logging

from pylons import config
from ckan import plugins


class DigstdkAdmin(plugins.toolkit.CkanCommand):
    """
    Handles Data needed for Digst solutions.
    """

    def __init__(self, name):
        super(DigstdkAdmin, self).__init__(name)

    def command(self):
        cmd = self.args
        self.log = logging.getLogger(__name__)

        self.log.info("DIGSTDK paster command reporting...")

        if cmd == 'initdb':
            self.log.info("executing initdb ...")

        self.log.info("DIGSTDK paster command done ...")
