from django.shortcuts import render, reverse, redirect
from django.views.generic import TemplateView, FormView
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from .forms import ContactForm


class ContactView(FormView):
    """A view for handling the contact form submission."""
    form_class = ContactForm
    template_name = 'contact_us.html'

    def get_success_url(self):
        """Returns the URL to redirect to after successful form submission."""
        return reverse("thankyou")

    def form_valid(self, form):
        """
        Processes a valid form submission.

        Extracts data from the form, sends a notification email, and then redirects the user to the success URL.
        """
        email = form.cleaned_data.get("email")
        subject = form.cleaned_data.get("subject")
        message = form.cleaned_data.get("message")

        # Prepare and send the notification email
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = settings.NOTIFY_EMAIL
        mail_template = 'contact_enquiry.html'

        context = {
            'email': email,
            'subject': subject,
            'message': message,
        }

        message = render_to_string(mail_template, context)

        mail = EmailMessage(subject, message, from_email, [to_email])
        mail.content_subtype = "html"  # Set the email content type to HTML

        try:
            mail.send()
        except Exception as e:
            print(f"Failed to send notification email: {e}")

        return super(ContactView, self).form_valid(form)


class ThankyouView(TemplateView):
    """
    A view for displaying the thank-you page.

    This view is shown after a successful contact form submission.
    """
    template_name = 'thankyou.html'
