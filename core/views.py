from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, OrderItem, Order, Category, BillingAddress
from .forms import CheckoutForms
from django.views.generic import ListView, DetailView, View
from django.utils import timezone

class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = 'home.html'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        context['categories'] = categories
        return context

class OrderSummaryView(LoginRequiredMixin ,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect ('/')
        

class ItemDetailView(DetailView):
    model = Item
    template_name = 'product-page.html'

class CheckoutViews(View):
    def get(self, *args, **kwargs):
        form = CheckoutForms()
        context = {
            'form': form
        }
        return render(self.request, 'checkout-page.html', context)
    
    def post(self, *args, **kwargs):
        form = CheckoutForms(self.request.POST or None)

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data('street_address')
                apartement_address = form.cleaned_data('apartement_address')
                country = form.cleaned_data('country')
                zip_code = form.cleaned_data('zip_code')
                # TODO: add functionality for those fields
                # same_shipping_address = form.cleaned_data('same_shipping_address')
                # save_info = form.cleaned_data('save_info')
                payment_option = form.cleaned_data('payment_option')
                billing_address = BillingAddress(
                    user = self.request.user,
                    street_address = street_address,
                    apartement_address = apartement_address,
                    country = country,
                    zip_code = zip_code,
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                # TODO: add redirect to the selected payment option
                return redirect('core:checkout')
            messages.warning(self.request, 'Failed checkout')
            return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect ('core:oreder-summary')

        

@login_required
def add_to_card(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item, 
        user=request.user, 
        ordered=False
        )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # Check if order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'This item quantity was updated')
            return redirect('core:order-summary')
        else:
            order.items.add(order_item)
            messages.info(request, 'This item was added to your card')
            return redirect('core:order-summary')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        return redirect('core:order-summary')

@login_required
def remove_from_card(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # Check if order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item, 
                user=request.user, 
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, 'This item was remove from your cart.')
            return redirect('core:order-summary')
        else:
            messages.info(request, 'This item was not in your cart.')
            return redirect('core:product', slug=slug)
    else:
        messages.info(request, 'You do not have an active order.') 
        return redirect('core:product', slug=slug)
    
@login_required
def remove_single_item_from_card(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # Check if order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item, 
                user=request.user, 
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
            else:
                order.items.remove(order_item)
            order_item.save()
            messages.info(request, 'This item quantity was updated.')
            return redirect('core:order-summary')
        else:
            messages.info(request, 'This item was not in your cart.')
            return redirect('core:product', slug=slug)
    else:
        messages.info(request, 'You do not have an active order.') 
        return redirect('core:product', slug=slug)
    