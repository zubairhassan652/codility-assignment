from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    date_posted = models.CharField(max_length=100, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    job_url = models.URLField(unique=True)

    def __str__(self):
        return f"{self.title} @ {self.company}"
