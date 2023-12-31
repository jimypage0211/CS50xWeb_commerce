from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist",views.watchlist, name="watchlist"),
    path("addWatchlist/<str:id>",views.addWatchlist, name="addWatchlist"),
    path("removeWatchlist/<str:id>",views.removeWatchlist, name="removeWatchlist"),
    path("create",views.createListing, name="createListing"),
    path("createComment/<str:listingId>", views.createComment, name="createComment"),
    path("categoryListings/<str:catName>", views.categoryListings, name="categoryListings"),
    path("categories",views.categories, name="categories"), 
    path("listing/<str:id>/<str:alert>",views.visitListing, name="visit" ),
    path("bid/<str:listingId>",views.bid, name= "bid" ),
    path("finalize/<str:listingId>", views.finalize, name="finalize"),
    path("delete/<str:listingId>", views.delete, name="delete")
]
