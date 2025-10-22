from django.shortcuts import render
from django.http import FileResponse, Http404
from .models import Document
import os
from django.shortcuts import render, redirect
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.contrib.auth import get_user_model, login
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
import pandas as pd
from .models import Participant




User = get_user_model()


def request_magic_link(request):
    if request.method == "POST":
        email = request.POST.get('email')

        user=Participant.objects.filter(email=email)
        certificates=Participant.objects.filter(email=email)
        if not user.exists():
            messages.error(request, "Email not found in participant list.")
            return render(request, 'request_link.html')
               
        return render(request, 'show_certificates.html', {'certificates': certificates})

    return render(request, 'request_link.html')

def show_certificates(request):
    if request.method == "POST":
        certificate=request.POST.get('certificate_type')
        user=Participant.objects.filter(certificate_id=certificate)

        return redirect('request_magic_link')

    return redirect('request_magic_link')



def upload_certificate(request):
    if request.method == 'POST' and request.FILES.get('file'):
        excel_file = request.FILES['file']

        try:
            df = pd.read_excel(excel_file)

            for _, row in df.iterrows():
                Participant.objects.update_or_create(
                    reg_no=row['Reg. No.'],
                    defaults={
                        'serial_no': row['S. No.'],
                        'name': row['Name'],
                        'email': row['Email'],
                        'registration_type': row['Regitration  Type'],  # match Excel header
                        'certificate_type': row['certificate type'],
                    }
                )
            messages.success(request, "Excel data imported successfully!")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

    return render(request, 'upload_certificate.html')






import os
import base64
from io import BytesIO
from django.shortcuts import render
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

def certificate_preview(request, cert_id):
    certificate=Participant.objects.get(id=cert_id)
    name = certificate.name
    certificate_type = certificate.certificate_type
    

    # Open certificate template
    if certificate_type == 'Delegate':
        template_path = os.path.join(settings.BASE_DIR, 'static/certificate_Delegate.png')
        
    else:
        if certificate_type == 'Type B':
            template_path = os.path.join(settings.BASE_DIR, 'static/certificate_Faculty.png')
        else:
            template_path = os.path.join(settings.BASE_DIR, 'static/certificate.png')
            
    
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)

    # Load font
    font_path = os.path.join(settings.BASE_DIR, 'static/fonts/arial.ttf')
    try:
        font = ImageFont.truetype(font_path, 80)
    except OSError:
        font = ImageFont.load_default()

    # Prepare text
    text = f"{name}"
    lines = text.split('\n')

    # Calculate total height
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])
    total_height = sum(line_heights) + (len(lines)-1) * 10  # 10 px spacing
    y_text = (img.height - total_height) / 2

    # Draw each line centered
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0,0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x_text = (img.width - text_width) / 2
        draw.text((x_text, y_text), line, fill=(0, 0, 0), font=font)
        y_text += line_heights[i] + 10

    # Convert image to base64 for preview
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    img_data = f"data:image/png;base64,{img_base64}"

    return render(request, 'certificate_preview.html', {'img_data': img_data, 'name': name , 'cert':certificate})


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse
from PIL import Image
import os
from django.conf import settings

def certificate_download(request, cert_id):
  

    name = Participant.objects.get(id=cert_id).name
    certificate_type = Participant.objects.get(id=cert_id).certificate_type

    # Open template to get size
    if certificate_type == 'Delegate':
        template_path = os.path.join(settings.BASE_DIR, 'static/certificate_Delegate.png')
        
    else:
        if certificate_type == 'Type B':
            template_path = os.path.join(settings.BASE_DIR, 'static/certificate_Faculty.png')
        else:
            template_path = os.path.join(settings.BASE_DIR, 'static/certificate.png')
    template_path = os.path.join(settings.BASE_DIR, 'static/certificate.png')
    img = Image.open(template_path)
    img_width, img_height = img.size

    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{name}.pdf"'
    c = canvas.Canvas(response, pagesize=(img_width, img_height))
    
    # Draw certificate image as background
    c.drawImage(template_path, 0, 0, width=img_width, height=img_height)

    # Add user name text (adjust position as needed)
    c.setFont("Helvetica-Bold", 40)
    text = f" {name}"
    text_width = c.stringWidth(text, "Helvetica-Bold", 40)
    x = (img_width - text_width) / 2
    y = img_height / 2
    c.drawString(x, y, text)

    c.showPage()
    c.save()
    return response



