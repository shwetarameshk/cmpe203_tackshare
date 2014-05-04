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
    tackFile = models.FileField(upload_to="tackFiles")
    fileType = models.TextField()
    tags = ListField()
    bookmark = models.URLField()
    username = models.TextField()
    board = models.TextField()
    isFavorite=models.BooleanField()

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

class UserStats (models.Model):
    userName = models.TextField()
    numBoards = models.TextField()
    numPublicBoards = models.TextField()
    numPrivateBoards = models.TextField()
    numTacks = models.TextField()