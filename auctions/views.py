from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import *
from .utils import *


class ListingForm(forms.Form):
    title = forms.CharField(label="Title")
    description = forms.CharField(label="")
    placeholder = "Enter the description  ..."
    description.widget = forms.Textarea(attrs={"placeholder": placeholder})
    minBid = forms.FloatField(label="Initial Bid")
    imgURL = forms.CharField(label="Img URL (Optional)", required=False)
    category = forms.CharField(label="Add a Category (Optional)", required=False)
    selectCategory = forms.ChoiceField

class CommentForm(forms.Form):
    commentTitle = forms.CharField(label="Comment Title")
    message = forms.CharField(label="")
    placeholder = "Enter comment message  ..."
    message.widget = forms.Textarea(attrs={"placeholder": placeholder})


def index(request):
    return render(request, "auctions/index.html", {"listings": Listing.objects.all(), "catName": ""})



def createComment (request, listingId):
    if request.method == "POST":
        setComment(request, listingId)
        return HttpResponseRedirect(reverse("visit", kwargs={"id": listingId}))
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
    wl = Listing.objects.get(id=id)
    if wl.watchlistedBy.contains(request.user):
        return HttpResponse("Already in wl TODO")
    else:
        wl.watchlistedBy.add(request.user)
        return HttpResponseRedirect(reverse("watchlist"))


def categories(request):
    return render(
        request, "auctions/categories.html", {"categories": Category.objects.all()}
    )


def categoryListings(request, catName):
    catListings = Category.objects.get(catName=catName)
    return render(
        request, "auctions/index.html", {"catName": catName, "listings": catListings.listings.all()}
    )


def visitListing(request, id):
    listing = Listing.objects.get(id=id)
    return render(
        request,
        "auctions/viewListing.html",
        {"listing": listing, "comments": listing.listingComments.all()},
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
