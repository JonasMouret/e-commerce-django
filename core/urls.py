from django.urls import path
from .views import (
    HomeView, 
    OrderSummaryView, 
    CheckoutViews, 
    ItemDetailView, 
    add_to_card, 
    remove_from_card,
    remove_single_item_from_card 
    )

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutViews.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-card/<slug>', add_to_card, name='add-to-card'),
    path('remove-from-card/<slug>', remove_from_card, name='remove-from-card'),
    path('remove-item-from-card/<slug>', remove_single_item_from_card, name='remove-single-item-from-card'),
]
