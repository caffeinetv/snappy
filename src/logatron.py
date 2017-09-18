"""Log analysis and reporting"""

from base64 import b64decode
import datetime
import json
import logging
import os
import re
import urllib
from zlib import decompress, MAX_WBITS

# Import our dependencies
import vendored

import requests


LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
LOG.info('Loading function...')

# Environment variable config
AWS_REGION = os.environ['AWS_REGION']
SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']


# A list of regular expressions to look for
_compiled_patterns = [
    ('error', re.compile('\\[FATAL\\]')),
    ('error', re.compile('\\[ERROR\\]')),
    ('warning', re.compile('\\[WARNING\\]')),
    ('error', re.compile('Traceback', flags=re.I)),
    ('error', re.compile('Unable to import module', flags=re.I)),
    ('pulse', re.compile('\\[PULSE\\]', flags=re.I)),
]

_ignore_patterns = [
    re.compile('Protocol Buffers not installed properly'),
]


def encode(string):
    '''Double URL encode a string like the AWS Web Console expects'''
    # return urllib.quote_plus(urllib.quote_plus(string))
    return urllib.quote_plus(string)


def log_url(log_group, log_stream, start_time, end_time):
    # https://us-west-2.console.aws.amazon.com/cloudwatch/home?region=us-west-2#logEventViewer:group=/prod/ecs/roadhog;stream=roadhog/roadhog/73485b15-d285-41c9-97e0-c6ad0d986d2c;start=2016-09-13T13:00:00Z;end=2016-09-13T13:52:04Z;tz=Local

    '''Create the link to the exact point in the AWS logs'''
    template = (
        'https://{region}.console.aws.amazon.com/cloudwatch/home?'
        'region={region}#'
        'logEventViewer:group={log_group};'
        'stream={log_stream};'
        'start={start_time};'
        'end={end_time};'
        'tz=UTC'
    )

    start = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    url = template.format(
        region=AWS_REGION,
        log_group=encode(log_group),
        log_stream=encode(log_stream),
        start_time=encode(start),
        end_time=encode(end))
    return url


def send_notification(log_group, log_stream, log_events):
    ts0 = log_events[0][1]['timestamp'] / 1000.0
    tsn = log_events[-1][1]['timestamp'] / 1000.0
    start_timestamp = datetime.datetime.fromtimestamp(ts0)
    end_timestamp = datetime.datetime.fromtimestamp(tsn + 600)
    url = log_url(log_group, log_stream, start_timestamp, end_timestamp)

    for (notification_type, log_event) in log_events:

        # Message text
        if notification_type == 'pulse':
            msg = log_event['message']
            pattern = '[PULSE]'
            pos = msg.find(pattern) + len(pattern) + 1
            msg = msg[pos:]
        else:
            msg = log_event['message']

        # Color
        if notification_type == 'pulse':
            color = '#58abfc'
        elif notification_type == 'warning':
            color = '#d86920'
        else:
            color = '#f01000'

        # Put it all together
        msg = {
            'attachments': [
                {
                    'author_name': log_group,
                    'author_link': url,
                    'color': color,
                    'text': '```{}```'.format(msg),
                    'fallback': msg,
                    'mrkdwn_in': ["text"]
                }
            ]
        }

    # Send it to the incoming web hook
    post_hook(msg)


def post_hook(message):
    LOG.debug('Posting to Slack')
    payload = json.dumps(message)
    LOG.debug(payload)
    req = requests.post(SLACK_WEBHOOK_URL, data=payload)
    LOG.debug('Response code: %d', req.status_code)


def process_event(log_event):
    '''Loop through the list of patterns looking for a match.'''

    LOG.debug('Looking at: %s', log_event)
    for (notification_type, regex) in _compiled_patterns:
        match = regex.search(log_event['message'])
        if match:
            for skip_regex in _ignore_patterns:
                skip_match = regex.search(log_event['message'])
                if not skip_match:
                    LOG.debug('Match found!')
                    return (notification_type, match)

    return (None, False)


def process_log_events(log_data):
    '''Loop through all log events'''

    log_group = log_data.get('logGroup')
    log_stream = log_data.get('logStream')
    log_events = log_data.get('logEvents')

    num_events = 0
    num_matches = 0
    log_matches = []
    for log_event in log_events:
        (notification_type, match) = process_event(log_event)
        if match:
            log_matches.append((notification_type, log_event))
            num_matches += 1
        else:
            if len(log_matches) > 0:
                # Send and reset
                send_notification(log_group, log_stream, log_matches)
                log_matches = []

        num_events += 1

    if len(log_matches) > 0:
        send_notification(log_group, log_stream, log_matches)

    return (num_matches, num_events)


def handler(event, context):
    '''Main entry point for the Lambda function.'''

    assert context
    LOG.debug(event)

    raw_data = event.get('awslogs', {}).get('data')

    if not raw_data:
        LOG.error('No data')
        return

    decoded_data = decompress(b64decode(raw_data), 16 + MAX_WBITS)
    data = json.loads(decoded_data)

    (num_matches, num_events) = process_log_events(data)

    msg = "Processed {} log entries of which {} matched.".format(
        num_events, num_matches)
    LOG.info(msg)
    return msg


LOG.info('Function loaded successfully')
