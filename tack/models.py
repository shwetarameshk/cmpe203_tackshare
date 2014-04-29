from django.db import models
from djangotoolbox.fields import ListField
# Create your models here.


class Users(models.Model):
    Firstname = models.TextField()
    Lastname = models.TextField()
    Username = models.TextField()
    Password = models.TextField()
    Email = models.TextField()

    def __unicode__(self):
        return self.Username

class TackImages(models.Model):
    Filename = models.TextField()
    image = models.ImageField(upload_to="photos")
    tags = ListField()
    bookmark = models.URLField()
    username = models.TextField()
    board = models.TextField()

    def __unicode__(self):
        return self.Filename

class Boards(models.Model):
    Name = models.TextField()
    Description = models.TextField()
    Privacy = models.TextField()
    username = models.TextField()
    VisibleToUsers = ListField()
    Tacks = ListField()

    def __unicode__(self):
        return self.Name

class subscription(models.Model):
    username=models.TextField()
    follow = models.TextField()
    addtack = models.TextField()
    favorite = models.TextField()
