from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Notification

def create_notification(recipient, notification_type, title, message, link=''):
    """
    Create a notification
    """
    return Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link
    )

def send_email_notification(recipient_email, subject, message, html_message=None):
    """
    Send email notification
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_application_notification(application, notification_type):
    """
    Send notification when application is created or updated
    """
    if notification_type == 'new':
        # Notify employer
        employer_user = application.job.employer.user
        title = f"New Application for {application.job.title}"
        message = f"{application.candidate.full_name} has applied for {application.job.title}"
        link = f"/employer/applications/{application.id}"
        
        create_notification(employer_user, 'application_received', title, message, link)
        
        # Send email
        subject = f"New Application: {application.job.title}"
        email_message = f"""
        Hello {application.job.employer.company_name},
        
        You have received a new application for the position: {application.job.title}
        
        Candidate: {application.candidate.full_name}
        Email: {application.candidate.user.email}
        Applied on: {application.applied_at.strftime('%B %d, %Y')}
        
        Please log in to your dashboard to review the application.
        
        Best regards,
        Job Board Team
        """
        
        send_email_notification(employer_user.email, subject, email_message)
    
    elif notification_type == 'status_update':
        # Notify candidate
        candidate_user = application.candidate.user
        title = f"Application Status Updated: {application.job.title}"
        message = f"Your application status has been updated to: {application.get_status_display()}"
        link = f"/candidate/applications/{application.id}"
        
        create_notification(candidate_user, 'application_status_changed', title, message, link)
        
        # Send email
        subject = f"Application Status Update: {application.job.title}"
        email_message = f"""
        Hello {application.candidate.full_name},
        
        Your application for {application.job.title} at {application.job.employer.company_name} has been updated.
        
        New Status: {application.get_status_display()}
        
        {f"Employer Notes: {application.employer_notes}" if application.employer_notes else ""}
        
        Please log in to your dashboard for more details.
        
        Best regards,
        Job Board Team
        """
        
        send_email_notification(candidate_user.email, subject, email_message)

def send_job_posted_notification(job):
    """
    Send notification when a new job is posted
    """
    # This could notify relevant candidates based on their preferences
    # For now, we'll just create a notification for the employer
    title = f"Job Posted Successfully: {job.title}"
    message = f"Your job posting '{job.title}' is now live and accepting applications."
    link = f"/employer/jobs/{job.slug}"
    
    create_notification(job.employer.user, 'job_posted', title, message, link)