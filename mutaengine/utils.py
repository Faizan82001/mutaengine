import requests
import tempfile
import logging

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter

from django.conf import settings
from rest_framework.response import Response

logger = logging.getLogger(__name__)

def custom_response(status_code: int, message: str, data=None):
    """
    Returns a consistent response structure with status, message, and data.

    :param status: Boolean to indicate success (True) or failure (False)
    :param message: A short message describing the response
    :param data: The actual data payload to send (can be None if not applicable)
    :param status_code: HTTP status code (default is 200 OK)
    :return: Django Rest Framework Response object
    """
    if status_code == 204:
        return Response(status=status_code)
    return Response({
            'status': status_code,
            'message': message,
            'data': data
        }, 
        status=status_code
    )
    
    
def send_password_reset_email(user, reset_link):
    subject = "Password Reset Request"
    html_content = render_to_string('password_reset_email.html', {
        'user': user,
        'reset_link': reset_link
    })
    text_content = strip_tags(html_content)

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [user.email]

    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    try:
        email.send()
        logger.info(f"Password Reset email successfully sent to {user.email}")
        return True
    except Exception as e:
        logger.exception(f"500 Error(Failed to send email): {str(e)}")
        raise Exception(f"Error sending email: {str(e)}")
    

def verify_recaptcha(recaptcha_response):
    """
    Verifies reCAPTCHA token with Google's API
    """
    url = settings.RECAPTCHA_VERIFICATION_URL
    data = {
        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }
    
    response = requests.post(url, data=data)
    result = response.json()

    if not result.get('success') or result.get('score', 0) < 0.5:
        logger.info(f"Invalid reCaptcha used. Probably a bot tried to access the endpoint.")
        return False

    return True


def generate_invoice_pdf(user, order):
    # Create an invoice directory if it doesn't exist
    logger.info(f"Starting PDF generation for order#{order.id}")
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmpfile:
        invoice_pdf_path = tmpfile.name

        # Create a PDF document
        pdf = SimpleDocTemplate(invoice_pdf_path, pagesize=letter)

        # Add logo image
        # logo_path = "path/to/your/logo.png"  # Update this path
        # logo = Image(logo_path)
        # logo.drawHeight = 1 * inch
        # logo.drawWidth = 2 * inch

        # Create the elements list to build the PDF
        elements = []

        # Add the logo and company name at the top
        # elements.append(logo)
        
        # Add invoice title
        styles = getSampleStyleSheet()
        styles['Title'].alignment = TA_CENTER
        elements.append(Paragraph(f"Invoice for Order #{order.id}", styles['Title']))

        # Add a line separator
        elements.append(Paragraph("<br/>", styles['Normal']))
        elements.append(Paragraph("<br/>", styles['Normal']))

        # Add customer details
        customer_info = [
            f"Customer Name: {user.first_name} {user.last_name}",
            f"Customer Email: {user.email}",
            f"Order ID: {order.id}",
            f"Order Date: {order.created_at.strftime('%Y-%m-%d')}",
        ]

        for info in customer_info:
            elements.append(Paragraph(info, styles['Normal']))

        elements.append(Paragraph("<br/>", styles['Normal']))
        elements.append(Paragraph("<br/>", styles['Normal']))
        elements.append(Paragraph("<br/>", styles['Normal']))

        # Table of ordered items
        data = [["Product", "Quantity", "Unit Price", "Total Price"]]

        # Populate order items
        for item in order.items.all():
             data.append([
                Paragraph(item.product.title, styles['Normal']),  # Use Paragraph for wrapping
                Paragraph(str(item.quantity), styles['Normal']),
                Paragraph(f"${item.product.price:.2f}", styles['Normal']),
                Paragraph(f"${item.quantity * item.product.price:.2f}", styles['Normal'])
            ])

        # Add total amount row at the end of the table
        data.append(["", "", "Total Amount", f"${order.total_amount:.2f}"])

        # Create the table
        table = Table(data, colWidths=[3.5 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])

        # Add table style for better presentation
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)

        # Footer
        elements.append(Paragraph("<br/>", styles['Normal']))
        elements.append(Paragraph("<br/>", styles['Normal']))
        elements.append(Paragraph("<br/>", styles['Normal']))

        styles = getSampleStyleSheet()
        normal_style = styles['Normal']  # Get the Normal style

        # Custom style for the clickable link
        clickable_email = f'<a href="mailto:{settings.SUPPORT_EMAIL}"><font color="blue"><u>support</u></font></a>'

        # Constructing the paragraph with a clickable email link
        text = f'If you have any questions, feel free to contact us at {clickable_email}.'

        # Add paragraph with clickable email using the correct style object
        elements.append(Paragraph(text, normal_style))
        elements.append(Paragraph("Thank you for your purchase!", styles['Normal']))

        # Build the PDF
        pdf.build(elements)

        logger.info(f"Successful PDF generation for order#{order.id}")
        return invoice_pdf_path

def send_invoice_email(user, order):
    # Generate the PDF invoice
    invoice_pdf_path = generate_invoice_pdf(user, order)

    # Order details for the email body
    order_details = []
    for item in order.items.all():
        order_details.append({
            "image_url": item.product.image,  # Make sure you access the URL
            "product_name": item.product.title,
            "quantity": str(item.quantity),
            "price": str(item.price)
        })

    # Prepare the email subject and body
    subject = "Your Invoice from Our Store"
    html_content = render_to_string('invoice_email.html', {
        'user_name': f"{user.first_name} {user.last_name}",
        'order_details': order_details,
        'total_amount': str(order.total_amount),
        'support_email': settings.SUPPORT_EMAIL,
    })
    text_content = strip_tags(html_content)

    # Create the email
    email = EmailMultiAlternatives(
        subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email]
    )
    email.attach_alternative(html_content, "text/html")

    # Attach the PDF invoice
    with open(invoice_pdf_path, 'rb') as f:
        email.attach(f"invoice_{order.id}.pdf", f.read(), "application/pdf")
        logger.info(f"Invoice PDF successfully attached to email({user.email})")

    try:
        email.send()
        logger.info(f"Invoice email successfully sent to {user.email} for order#{order.id}")
        return True
    except Exception as e:
        logger.error(f"500 Error(Failed to send invoice email): {str(e)}")
        raise Exception(f"Failed to send invoice email: {str(e)}")