from django.db import models
from djangotoolbox.fields import ListField
# Create your models here.


class Users(models.Model):
    """
    This class contains fields for User related information
    """
    Firstname = models.TextField()
    Lastname = models.TextField()
    Username = models.TextField()
    Password = models.TextField()
    Email = models.TextField()

    def __unicode__(self):
        return self.Username

class TackImages(models.Model):
    """
    This class contains fields for Tacks related information
    """
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
    """
    This class contains fields for Boards related information
    """
    Name = models.TextField()
    Description = models.TextField()
    Privacy = models.TextField()
    username = models.TextField()
    VisibleToUsers = ListField()
    Tacks = ListField()

    def __unicode__(self):
        return self.Name

class subscription(models.Model):
    """
    This class contains fields for Email Subscription related information
    """
    username=models.TextField()
    follow = models.TextField()
    addtack = models.TextField()
    favorite = models.TextField()


class Followers(models.Model):
    """
    This class contains the follower information
    """
    userName=models.TextField()
    followersList=ListField()

    def __unicode__(self):
        return self.userName