
from django.contrib import admin
from django.urls import path
from .views import request_magic_link  ,certificate_preview,certificate_download, upload_certificate,show_certificates
urlpatterns = [
    path("", request_magic_link, name="request_magic_link"),
    path('upload/certificate' , upload_certificate, name='document_upload'),
    path('show/certificates' , show_certificates, name='show_certificates'),
    path('certificate/preview/<int:cert_id>/', certificate_preview, name='certificate_preview'),
    path('certificate/download/<int:cert_id>/', certificate_download, name='certificate_download'),


]
