from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Listing (models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=50)
    description = models.TextField()
    initialPrice = models.FloatField()
    active = models.BooleanField()
    imgLink = models.CharField(max_length=100, blank=True) 
    watchlistedBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")      

    def __str__(self) -> str:
        return f"Seller: {self.poster}, Title: {self.title}"


class Comment (models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userComments")
    message = models.TextField()
    target = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingComments")

    def __str__(self) -> str:
        return f"Author: {self.author}, Listing: {self.target}"    


class Bid (models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userBids")
    target = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingBids")
    bidValue = models.FloatField()
    active = models.BooleanField()

class Category(models.Model):
    name = models.CharField(max_length=20)
    listings = models.ManyToManyField(Listing, related_name="categories")
    


