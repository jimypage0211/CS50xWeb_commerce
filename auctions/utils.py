from .models import *

def setListing(request):
    title = request.POST["title"]
    description = request.POST["description"]
    minBid = request.POST["minBid"]
    imgURL = request.POST["imgURL"]
    category = Category(catName = request.POST["category"])
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
    commentTitle = request.POST["commentTitle"]
    message = request.POST["message"]
    user = request.user
    target = Listing.objects.get(id=listingID)
    comment = Comment(
        commentTitle= commentTitle,
        message= message,
        author= user,
        target= target
    )
    comment.save()

def getHighestBid(listing):
    bids = listing.listingBids.all()
    max = 0
    if not len(bids):
        return "No bids"
    else:
        for bid in bids:
            if bid.bidValue > max:
                max = bid.bidValue
        return max
    


