from django.db import models

class Item(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    class Meta:
        app_label = 'ElasticSearch'  # <--- Add this line

    def __str__(self):
        return self.title