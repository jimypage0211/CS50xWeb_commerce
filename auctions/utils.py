from .models import *

def setListing(request):
    title = request.POST["title"]
    description = request.POST["description"]
    minBid = request.POST["minBid"]
    imgURL = request.POST["imgURL"]
    category = Category(name = request.POST["category"])    
    user = request.user
    listing = Listing(
        poster = user,
        title = title,
        description = description,
        initialPrice = minBid,
        active = True,
        imgLink = imgURL,
        category = category
        )
    listing.save()   


def setComment(request):
    pass

def getComment():
    pass

def setBid(request):
    pass

def getBid():
    pass

