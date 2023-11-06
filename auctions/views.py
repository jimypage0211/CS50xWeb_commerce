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

class CommentForm(forms.Form):    
    message = forms.CharField(label="")
    placeholder = "Enter comment message  ..."
    message.widget = forms.Textarea(attrs={"placeholder": placeholder})


def index(request):
    activeListings = Listing.objects.filter(active = True)
    return render(request, "auctions/index.html", {"listings": activeListings, "catName": ""})

def delete(request, listingId):
    toDelete = Listing.objects.get(id=listingId)
    toDelete.delete()
    return HttpResponseRedirect(reverse("index"))


def finalize (request, listingId):
    toCloseListing = Listing.objects.get(id=listingId)
    toCloseListing.active= False
    toCloseListing.save()
    return HttpResponseRedirect(reverse("index"))
    

def bid(request, listingId):
    target = Listing.objects.get(id = listingId)
    highestBid = getHighestBid(target)
    if highestBid != "No bids" :
        target.winningBid = highestBid.bidValue 
        target.save()
    bidValue = float (request.POST["bidValue"])   
    if bidValue <= target.winningBid:
        return  HttpResponseRedirect(reverse("visit", kwargs={"id": listingId, "alert": "badBid"}))
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
    if request.method == "POST":
        setComment(request, listingId)
        return HttpResponseRedirect(reverse("visit", kwargs={"id": listingId, "alert": "okComment"}))
    else:        
        return render(request, "auctions/createComment.html", {"form": CommentForm()})  

@login_required(login_url="login")
def createListing(request):
    if request.method == "POST":
        setListing(request)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/createListing.html", {"form": ListingForm()})


def watchlist(request):
    userListings = Listing.objects.filter(watchlistedBy=request.user)
    return render(request, "auctions/watchlist.html", {"listings": userListings})


def addWatchlist(request, id):
    toWatch = Listing.objects.get(id=id)
    if toWatch.watchlistedBy.contains(request.user):
        return HttpResponse("Already in WL TODO")
    else:
        toWatch.watchlistedBy.add(request.user)
        return  HttpResponseRedirect(reverse("visit", kwargs={"id": id, "alert": "okWatchlist"}))

def removeWatchlist(request, id):    
    toRemove = Listing.objects.get(id=id)
    toRemove.watchlistedBy.remove(request.user)
    return  HttpResponseRedirect(reverse("visit", kwargs={"id": id, "alert": "badWatchlist"}))


def categories(request):
    return render(
        request, "auctions/categories.html", {"categories": Category.objects.all()}
    )


def categoryListings(request, catName):
    catListings = Category.objects.get(catName=catName)
    return render(
        request, "auctions/index.html", {"catName": catName, "listings": catListings.listings.all()}
    )


def visitListing(request, id, alert):
    listing = Listing.objects.get(id=id)
    highestBid = getHighestBid(listing)
    activeUserWL = request.user.watchlist.all()
    wlListingsIDs = []
    for wlListing in activeUserWL:
        wlListingsIDs.append(wlListing.id)
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
