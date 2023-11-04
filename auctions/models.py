from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    catName = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f"{self.catName}"


class Listing(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=50)
    description = models.TextField()
    initialPrice = models.FloatField()
    active = models.BooleanField()
    imgLink = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,blank=True, null=True, related_name="listings")
    winningBid = models.FloatField(null=False)
    watchlistedBy = models.ManyToManyField(User, null=True, blank=True, related_name="watchlist")

    def __str__(self) -> str:
        return f"Seller: {self.poster}, Title: {self.title}"

class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="userComments"
    )   
    commentTitle = models.CharField(max_length=255) 
    message = models.TextField()
    target = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="listingComments"
    )

    def __str__(self) -> str:
        return f"Author: {self.author}, Listing: {self.target}"


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userBids")
    target = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="listingBids"
    )
    bidValue = models.FloatField()
    

    def __str__(self) -> str:
        return f"Bidder: {self.bidder}, Listing: {self.target}, Offer: {self.bidValue}"
