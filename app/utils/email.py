from flask import current_app, render_template
from flask_mail import Message
from app import mail

def send_email(to, subject, template, **kwargs):
    """Send an email with the given template to the specified recipients."""
    msg = Message(subject, recipients=[to])
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)

def send_invitation_email(invitation, invitation_type):
    """Send an invitation email based on the invitation type."""
    if invitation_type == 'company':
        subject = "Finco - Company Registration Invitation"
        template = "emails/company_invitation"
    else:  # employee
        subject = "Finco - Employee Registration Invitation"
        template = "emails/employee_invitation"
    
    send_email(
        to=invitation.email,
        subject=subject,
        template=template,
        invitation=invitation,
        invitation_type=invitation_type
    )
