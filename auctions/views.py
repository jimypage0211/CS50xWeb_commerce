from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required


from .models import *
from .utils import *

#Form for creating a Listing 
class ListingForm(forms.Form):
    title = forms.CharField(label="Title")
    description = forms.CharField(label="")
    placeholder = "Enter the description  ..."
    description.widget = forms.Textarea(attrs={"placeholder": placeholder})
    minBid = forms.FloatField(label="Initial Bid")
    imgURL = forms.CharField(label="Img URL (Optional)", required=False) 
    category = forms.CharField(label="Category (Optional)", required=False)    

#Form For creating a Comment
class CommentForm(forms.Form):    
    message = forms.CharField(label="")
    placeholder = "Enter comment message  ..."
    message.widget = forms.Textarea(attrs={"placeholder": placeholder})


def index(request):
    """ 
    Renders all active listings. Category name (catName) is passed empty since this template is also 
    used for showing all listing from an specific category. 
    """
    activeListings = Listing.objects.filter(active = True)
    return render(request, "auctions/index.html", {"listings": activeListings, "catName": ""})


def delete(request, listingId):
    """ 
    Given a the current listing id deletes a listing. After deletion it redirects to the index page. 
    """
    toDelete = Listing.objects.get(id=listingId)
    toDelete.delete()
    return HttpResponseRedirect(reverse("index"))


def finalize (request, listingId):
    """ 
    Closes a listing. After the listing is closed it wont be showed when listing the listings.
    It redirects to the index page
    """
    toCloseListing = Listing.objects.get(id=listingId)
    toCloseListing.active= False
    toCloseListing.save()
    return HttpResponseRedirect(reverse("index"))
    

def bid(request, listingId):
    """ 
    Given the current listing id, creates a new bid from the viewListing page. It also sets the 
    highest bid for bidded listing. If the bid is less than     the winning bid, render the same
    listing with an error message and the bid is not created, else, render a success message and
    the bid is created and saved.
    """
    target = Listing.objects.get(id = listingId)
    highestBid = getHighestBid(target)
    if highestBid != "No bids" :
        #If there are bids set the listiing winning bid to the highest
        target.winningBid = highestBid.bidValue 
        target.save()
    bidValue = float (request.POST["bidValue"])   
    if bidValue <= target.winningBid:
        #if bid < winningbid go to the listing page with a badBid alert
        return  HttpResponseRedirect(reverse("visit", kwargs={"id": listingId, "alert": "badBid"}))
        
    #Create the new bid
    bid = Bid(
        bidder= request.user,
        target= target,
        bidValue= request.POST["bidValue"]
    )
    bid.save()
    #every bided listing goes into WL
    target.watchlistedBy.add(request.user)
    return  HttpResponseRedirect(reverse("visit", kwargs={"id": listingId, "alert": "okBid"}))


def createComment (request, listingId):
    """
    If the request is a POST, given the current listing id, creates a comment, else, renders the 
    create comment form. 
    """
    if request.method == "POST":
        setComment(request, listingId)
        return HttpResponseRedirect(reverse("visit", kwargs={"id": listingId, "alert": "okComment"}))
    else:        
        return render(request, "auctions/createComment.html", {"form": CommentForm()})  

@login_required(login_url="login")
def createListing(request):
    """
    If the request is a POST, given the current listing id, creates a listing, else, renders the 
    create listing form. 
    """
    if request.method == "POST":
        setListing(request)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/createListing.html", {"form": ListingForm()})


def watchlist(request):
    """
    Filters all listing watchlisted by the active user and renders them. 
    """
    userListings = Listing.objects.filter(watchlistedBy=request.user)
    return render(request, "auctions/watchlist.html", {"listings": userListings})


def addWatchlist(request, id):
    """
    Given the current listing Id add the listing to the active user WL, then , renders the listing 
    page with a successful creation message. Now in the listing page it will appear a remove from WL 
    button instead of an add to WL.
    """
    toWatch = Listing.objects.get(id=id)
    toWatch.watchlistedBy.add(request.user)
    return  HttpResponseRedirect(reverse("visit", kwargs={"id": id, "alert": "okWatchlist"}))
        

def removeWatchlist(request, id):   
    """
    Given the current listing Id add the listing to the active user WL, then , renders the listing 
    page with a succesful deletion message. Now in the listing page it will appear a add to WL button
    instead of a remove from WL.
    """ 
    toRemove = Listing.objects.get(id=id)
    toRemove.watchlistedBy.remove(request.user)
    return  HttpResponseRedirect(reverse("visit", kwargs={"id": id, "alert": "badWatchlist"}))


def categories(request):
    """
    Render all categories buttons in the categories page. 
    """
    return render(
        request, "auctions/categories.html", {"categories": Category.objects.all()}
    )


def categoryListings(request, catName):
    """
    Render all listing from the clicked button category. 
    """
    catListings = Category.objects.get(catName=catName)
    return render(
        request, "auctions/index.html", {"catName": catName, "listings": catListings.listings.all()}
    )


def visitListing(request, id, alert):
    """
    Given the listing ID and an alert type, renders the listing page for that listing. This page will 
    alsor renders the success and failure messages from all redirections (bids, comments and WL). 
    """
    listing = Listing.objects.get(id=id)    
    if request.user.is_authenticated:
        #Creates a list of listing ids to check in page if the actual listing is in the WL of user
        activeUserWL = request.user.watchlist.all()
        wlListingsIDs = []
        for wlListing in activeUserWL:
            wlListingsIDs.append(wlListing.id)
    else:
        wlListingsIDs = []
    #Needed to do this to update the winning bid when visiting the page    
    highestBid = getHighestBid(listing)
    if highestBid == "No bids":
        listing.winningBid = listing.initialPrice
    else:
        listing.winningBid = highestBid.bidValue
    listing.save()
    return render(
        request,
        "auctions/viewListing.html",
        {"listing": listing,
        "comments": listing.listingComments.all(),
        "winningBid": highestBid, "alert":alert,
        "wlListingsIDs": wlListingsIDs},
    )


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
