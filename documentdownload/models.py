from django.db import models

class Document(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    upload = models.FileField(upload_to='documents/')

    def __str__(self):
        return self.title
    
    class Meta:
        app_label = 'documentdownload'


# models.py
from django.db import models

class Participant(models.Model):
    serial_no = models.IntegerField()  # S. No.
    reg_no = models.CharField(max_length=50)  # Reg. No.
    name = models.CharField(max_length=100)
    email = models.EmailField()
    registration_type = models.CharField(max_length=50)
    certificate_type = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.reg_no})"
    class Meta:
        app_label = 'documentdownload'
