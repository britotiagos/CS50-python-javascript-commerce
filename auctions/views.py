from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Comments, Bid


def listing(request, id):
    listingData = Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = Comments.objects.filter(listing=listingData)
    isOwner = request.user == listingData.owner
    isActive = listingData.isActive
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "isOwner": isOwner,
        "isActive": isActive
    })


def closeListing(request, id):
    listingData = Listing.objects.get(pk=id)
    listingData.isActive = False
    listingData.save()
    isOwner = request.user.username == listingData.owner.username
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = Comments.objects.filter(listing=listingData)
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isOwner": isOwner,
        "isListingInWatchlist": isListingInWatchlist,
        "allComments": allComments,
        "updated": True,
        "message": "Listing successfully closed.",

    })


def addBid(request, id):
    newBid = request.POST["bid"]
    listingData = Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingData.watchlist.all()
    allComments = Comments.objects.filter(listing=listingData)
    isActive = listingData.isActive
    isOwner = request.user.username == listingData.owner.username

    try:
        newBid = float(newBid)
    except ValueError:
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": "Bid must be a number",
            "updated": False,
            "isListingInWatchlist": isListingInWatchlist,
            "allComments": allComments,
            "isActive": isActive,
            "isOwner": isOwner,
        })

    if float(newBid) > listingData.price.bid:
        updateBid = Bid(bid=float(newBid), user=request.user)
        updateBid.save()
        listingData.price = updateBid
        listingData.save()
        isActive = listingData.isActive
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": "Bid successfully added",
            "updated": True,
            "isListingInWatchlist": isListingInWatchlist,
            "allComments": allComments,
            "isActive": isActive,
            "isOwner": isOwner,
        })

    else:
        return render(request, "auctions/listing.html", {
            "listing": listingData,
            "message": "Bid must be higher than current bid",
            "updated": False,
            "isListingInWatchlist": isListingInWatchlist,
            "allComments": allComments,
            "isActive": isActive,
            "isOwner": isOwner,
        })


def addComment(request, id):
    currentUser = request.user
    listingData = Listing.objects.get(pk=id)
    comment = request.POST["comment"]
    newComment = Comments(
        comment=comment, author=currentUser, listing=listingData)

    newComment.save()
    return HttpResponseRedirect(reverse("listing", args=(id, )))


def displayWatchlist(request):
    currentUser = request.user
    listings = currentUser.listingWatchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": listings
    })


def addToWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))


def removeFromWatchlist(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args=(id, )))


def index(request):
    activeListings = Listing.objects.filter(isActive=True)
    allCategories = Category.objects.all()

    return render(request, "auctions/index.html", {
        "listings": activeListings,
        "categories": allCategories
    })


def displayCategory(request):
    if request.method == "POST":
        categoryFromForm = request.POST["category"]
        category = Category.objects.get(categoryName=categoryFromForm)
        activeListings = Listing.objects.filter(
            isActive=True, category__categoryName=category)
        allCategories = Category.objects.all()

    return render(request, "auctions/index.html", {
        "listings": activeListings,
        "categories": allCategories
    })


def createListing(request):
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": allCategories
        })
    else:
        title = request.POST["title"]
        description = request.POST["description"]
        imageurl = request.POST["imageurl"]
        price = request.POST["price"]
        category = request.POST["category"]
        categoryData = Category.objects.get(categoryName=category)
        bid = Bid(bid=float(price), user=request.user)
        bid.save()
        currentUser = request.user
        newListing = Listing(title=title, description=description, imageUrl=imageurl,
                             price=bid, owner=currentUser, category=categoryData)
        newListing.save()
        return HttpResponseRedirect(reverse("index"))


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
