from django.db import models
from djangotoolbox.fields import ListField
# Create your models here.


class Users(models.Model):
    """
    This class contains fields for User related information
    """
    first_name = models.TextField()
    last_name = models.TextField()
    username = models.TextField()
    password = models.TextField()
    email = models.TextField()

    def __unicode__(self):
        return self.username

class TackImages(models.Model):
    """
    This class contains fields for Tacks related information
    """
    file_name = models.TextField()
    tack_file = models.FileField(upload_to="tackFiles")
    file_type = models.TextField()
    tags = ListField()
    bookmark = models.URLField()
    username = models.TextField()
    board = models.TextField()
    is_favorite=models.BooleanField()

    def __unicode__(self):
        return self.file_name

class Boards(models.Model):
    """
    This class contains fields for Boards related information
    """
    name = models.TextField()
    description = models.TextField()
    privacy = models.TextField()
    username = models.TextField()
    visible_to_users = ListField()
    tacks = ListField()

    def __unicode__(self):
        return self.name

class subscription(models.Model):
    """
    This class contains fields for email Subscription related information
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

