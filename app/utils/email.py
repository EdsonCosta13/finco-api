from flask import current_app, render_template
from flask_mail import Message
from app import mail
import traceback

def send_email(to, subject, template, **kwargs):
    """Send an email with the given template to the specified recipients."""
    try:
        msg = Message(subject, recipients=[to])
        msg.html = render_template(template + '.html', **kwargs)
        mail.send(msg)
        print(f"Email sent successfully to {to}")
        return True
    except Exception as e:
        print(f"Error sending email to {to}: {str(e)}")
        print(traceback.format_exc())
        return False

def send_invitation_email(invitation, invitation_type):
    """Send an invitation email based on the invitation type."""
    if invitation_type == 'company':
        subject = "Finco - Company Registration Invitation"
        template = "emails/company_invitation"
    else:  # employee
        subject = "Finco - Employee Registration Invitation"
        template = "emails/employee_invitation"
    
    success = send_email(
        to=invitation.email,
        subject=subject,
        template=template,
        invitation=invitation,
        invitation_type=invitation_type
    )
    
    print(f"Invitation email for {invitation_type} to {invitation.email}, code: {invitation.invitation_code}, success: {success}")
    return success
