from twilio.rest import Client

def send_text(text):

    account_sid = '***'
    auth_token = '***'

    client = Client(account_sid, auth_token)

    client.messages.create(from_='+***', to='+***', body=text)

    return print("Confirmation Sent")
