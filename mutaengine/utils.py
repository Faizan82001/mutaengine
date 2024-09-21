import os
import base64
import requests
import mailtrap as mt

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter

from django.conf import settings
from rest_framework.response import Response

def custom_response(status_code: int, message: str, data=None):
    """
    Returns a consistent response structure with status, message, and data.

    :param status: Boolean to indicate success (True) or failure (False)
    :param message: A short message describing the response
    :param data: The actual data payload to send (can be None if not applicable)
    :param status_code: HTTP status code (default is 200 OK)
    :return: Django Rest Framework Response object
    """
    return Response({
            'status': status_code,
            'message': message,
            'data': data
        }, 
        status=status_code
    )
    
    
def send_password_reset_email(user, reset_link):
    mail = mt.MailFromTemplate(
        sender=mt.Address(email=settings.DEFAULT_FROM_EMAIL, name=settings.MAILTRAP_SERVICE_NAME),
        to=[mt.Address(email=user.email)],
        template_uuid=settings.PASSWORD_RESET_MAIL_TEMPLATE_ID,
        template_variables={
            "user_email": user.email,
            "pass_reset_link": reset_link,
            "support_email": settings.SUPPORT_EMAIL
        }
    )

    client = mt.MailtrapClient(token=settings.EMAIL_HOST_PASSWORD)
    response = client.send(mail)
    
    if not response.get('success'):
        raise Exception(f"Failed to send email: {response.text}")
    

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
        return False

    return True


def generate_invoice_pdf(user, order, invoice_dir="invoices"):
    # Create an invoice directory if it doesn't exist
    if not os.path.exists(invoice_dir):
        os.makedirs(invoice_dir)

    # Define the invoice file path
    pdf_filename = f"invoice_{order.id}.pdf"
    pdf_path = os.path.join(invoice_dir, pdf_filename)

    # Create a PDF document
    pdf = SimpleDocTemplate(pdf_path, pagesize=letter)

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
        data.append([item.product.title, item.quantity, f"${item.product.price:.2f}", f"${item.quantity * item.product.price:.2f}"])

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

    return pdf_path

def send_invoice_email(user, order):
    # Generate the PDF invoice
    invoice_pdf_path = generate_invoice_pdf(user, order)

    # Order details (for the email body)
    order_details = []

    for item in order.items.all():
        order_details.append({
            "image_url": item.product.image,
            "product_name": item.product.title,
            "quantity": str(item.quantity),
            "price": str(item.price)
        })

    mail = mt.MailFromTemplate(
        sender=mt.Address(email=settings.DEFAULT_FROM_EMAIL, name=settings.MAILTRAP_SERVICE_NAME),
        to=[mt.Address(email=user.email)],
        template_uuid=settings.INVOICE_MAIL_TEMPLATE_ID,  # Replace with your template ID
        template_variables={
            "user_name": f"{user.first_name} {user.last_name}",
            "order_details": order_details,
            "support_email": settings.SUPPORT_EMAIL,
            "total_amount": str(order.total_amount),
        }
    )

    # Attach the PDF invoice to the email
    with open(invoice_pdf_path, 'rb') as f:
        mail.attachments = [
            mt.Attachment(
                content=base64.b64encode(f.read()),
                filename=f"invoice_{order.id}.pdf",
                mimetype="application/pdf"
            )
        ]

    client = mt.MailtrapClient(token=settings.EMAIL_HOST_PASSWORD)
    response = client.send(mail)
    
    if not response.get('success'):
        raise Exception(f"Failed to send invoice email: {response.text}")

    return response