import config
import smtplib

MAIL_TEMPLATES = {
	"verify_mail": {
		"subject": "Mastok: Validation de votre adresse mail",
		"body": """Bonjour

Vous recevez ce courriel car vous avez demandé à sécuriser votre compte Mastok.
Voici le code de sécurité à entrer dans l'application: {passcode}

A bientôt,
Mastok
"""
	}

}
MAIL_PAYLOAD_TEMPLATE = """\
From: {mail_from}\r\n\
To: {mail_to}\r\n\
Subject: {mail_subject}\r\n\
\r\n\
{mail_body}
"""

def from_template(mail_to, name, subject_params={}, body_params={}, test=False):
    """Send Creates an account"""
    if not test:
        mail_from = config.get("smtp", "from")  
    else:
        mail_from = ""
    mail_subject = MAIL_TEMPLATES[name]["subject"].format(**subject_params)
    mail_body = MAIL_TEMPLATES[name]["body"].format(**body_params)
    mail_payload = MAIL_PAYLOAD_TEMPLATE.format(
        mail_from=mail_from,
        mail_to=mail_to,
        mail_subject=mail_subject,
        mail_body=mail_body)
    
    # Send mail
    if not test:
        server = smtplib.SMTP_SSL(config.get("smtp", "host"), config.get("smtp", "port"))
        server.ehlo()
        server.login(config.get("smtp", "user"), config.get("smtp", "password"))
        server.sendmail(mail_from, mail_to, mail_payload.encode('utf-8'))
        server.close()
    