from .models import *

def setListing(request):
    title = request.POST["title"]
    description = request.POST["description"]
    minBid = request.POST["minBid"]
    imgURL = request.POST["imgURL"]
    categoryName = request.POST["category"]
    try:
        category = Category.objects.get(catName = categoryName)
    except Category.DoesNotExist:
        category = Category(catName = categoryName)
        category.save()
    user = request.user
    listing = Listing(
        poster = user,
        title = title,
        description = description,
        initialPrice = minBid,
        winningBid = minBid,
        active = True,
        imgLink = imgURL,
        category = category
        )
    listing.save()   


def setComment(request,listingID):    
    message = request.POST["message"]
    user = request.user
    target = Listing.objects.get(id=listingID)
    comment = Comment(        
        message= message,
        author= user,
        target= target
    )
    comment.save()

def getHighestBid(listing):
    bids = listing.listingBids.all()
    if len(bids) == 0:
        return "No bids"       
    else:
        maxValue = 0
        maxBid = bids[0] 
        for bid in bids:
            if bid.bidValue > maxValue:
                maxValue = bid.bidValue
                maxBid = bid
        return maxBid
    


