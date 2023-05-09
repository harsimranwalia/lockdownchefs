import smtplib  
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# The email body for recipients with non-HTML email clients.
BODY_TEXT = ("Amazon SES Test\r\n"
             "This email was sent through the Amazon SES SMTP "
             "Interface using the Python smtplib package."
            )

# The HTML body of the email.
BODY_HTML = """<html>
<head></head>
<body>
  <h1>Amazon SES SMTP Email Test</h1>
  <p>This email was sent with Amazon SES using the
    <a href='https://www.python.org/'>Python</a>
    <a href='https://docs.python.org/3/library/smtplib.html'>
    smtplib</a> library.</p>
</body>
</html>
            """
AWS = {
    "smtp_host" : "email-smtp.ap-south-1.amazonaws.com",
	"smtp_port" : 587,
	"smtp_user" : "AKIARPQCHHYEUHJ73VMK",
	"smtp_pass" : "BNQjj1Zg7JDHuEr7llRUaCs30CAg/ZQKMBrNv8Kdm4kC"
}


def send_email(recipient, subject, body_text="", body_html="", sender="recipe@skillbeyond.com", sendername="Lockdown Chefs"):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = email.utils.formataddr((sendername, sender))
    msg['To'] = recipient

    # Record the MIME types of both parts - text/plain and text/html.
    if body_html != "":
        part = MIMEText(body_html, 'html')
    elif body_text != "":
        part = MIMEText(body_text, 'plain')
    else:
        return {"error": True, "message":"Empty body"}
    
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part)

    # Try to send the message.
    try:  
        server = smtplib.SMTP(AWS['smtp_host'], AWS['smtp_port'])
        server.ehlo()
        server.starttls()
        #stmplib docs recommend calling ehlo() before & after starttls()
        server.ehlo()
        server.login(AWS['smtp_user'], AWS['smtp_pass'])
        server.sendmail(sender, recipient, msg.as_string())
        server.close()
    # Display an error message if something goes wrong.
    except Exception as e:
        print ("Error: ", e)
    else:
        print ("Email sent!")