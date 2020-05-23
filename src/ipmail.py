# smtplib module send mail

import smtplib



def create_message(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  return {'raw': base64.urlsafe_b64encode(message.as_string())}




def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print 'Message Id: %s' % message['id']
    return message
  except errors.HttpError, error:
    print 'An error occurred: %s' % error







TO = ['henrique.luiz@totvs.com.br','henriqueluiz_silva@yahoo.com.br']
SUBJECT = '[PROTHEUS CLI] - TESTE E-MAIL'
TEXT = 'Here is a message from python.'
# Gmail Sign In
gmail_sender = 'hl.silva89@gmail.com'
gmail_passwd = 'Henr@@488606'

msg = create_message(gmail_sender, 'henrique.luiz@totvs.com.br', SUBJECT, TEXT)


send_message( msg)