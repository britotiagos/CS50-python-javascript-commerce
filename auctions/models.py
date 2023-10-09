from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    categoryName = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.categoryName}"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=260)
    imageUrl = models.CharField(max_length=2000, blank=True)
    price = models.ForeignKey(
        "Bid", on_delete=models.CASCADE, blank=True, null=True, related_name="bidPrice")
    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    watchlist = models.ManyToManyField(
        User, blank=True, null=True, related_name="listingWatchlist")

    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):
    bid = models.FloatField(default=0)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name="userBid")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="bids")

    def __str__(self):
        return f"{self.bid}"


class Comments(models.Model):
    comment = models.CharField(max_length=260)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name="userComment")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="ListingComment")

    def __str__(self):
        return f"{self.author} comment on {self.listing}"
