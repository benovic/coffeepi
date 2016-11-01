from datetime import datetime, timedelta

class Config(object):

    JOBS = [
        {
            'id': 'cron_coffee',
            'func': 'jobs:make_coffee',
		    'trigger': 'cron',
		    'hour': '7',
		    'minute': '1',
        },
    ]

    SCHEDULER_VIEWS_ENABLED = True


