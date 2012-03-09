"""SMSified logic for the MTA application."""

import os
import requests as req
from three import Three

# Create a Three instance specific to Macon.
macon = Three('http://seeclicktest.com/open311/v2')


class AddressError(Exception):
    """Can't parse an address from a text message."""
    pass


class AuthenticationError(Exception):
    """
    Error should be raised when the SMSified username and password
    aren't known.
    """
    pass


def auth():
    """
    Get SMSified username and password authentication from environment
    variables.
    """
    try:
        username = os.environ['SMS_USER']
        password = os.environ['SMS_PASS']
    except KeyError:
        message = "You haven't set the SMS_USER and SMS_PASS env variables."
        raise AuthenticationError(message)
    return (username, password)


def process(text):
    """Process an incoming text message."""
    number = text['senderAddress'].lstrip('tel:+')
    message = text['message']
    address, message = find_address(message)
    request = macon.post('0', address=address, description=message,
                         phone=number)
    return respond(number)


def find_address(message):
    """Parse the address from a text message."""
    data = message.split('. ')
    if len(data) == 1:
        raise AddressError("Can't process the address from your text message.")
    else:
        street = data[0]
    address = street + ' Macon, GA'
    return address, message


def respond(number):
    """Send an SMS text message."""
    user_pass = auth()
    number = number.replace('-', '')
    message = "Thanks for reporting your issue!"
    params = {'address': number, 'message': message}
    send = "https://api.smsified.com/v1/smsmessaging/outbound/4782467248/requests"
    sms = req.post(send, auth=user_pass, params=params)
    return sms
