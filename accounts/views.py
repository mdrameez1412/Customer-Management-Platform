import imp
from multiprocessing import context
from pyexpat.errors import messages
from telnetlib import STATUS
from tokenize import group
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import Group
from requests import request
from .decorators import unauthenticated_user,allowed_users, admin_only
from .forms import CustomerForm, orderform, createuserform
from django.forms import inlineformset_factory
from .filters import *#OrderFilter
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.
from .models import *
from django.contrib import messages

@unauthenticated_user
def registerpage(request):
        form = createuserform()
        if request.method == 'POST':
            form= createuserform(request.POST)
            if form.is_valid():
                user=form.save()
                username = form.cleaned_data.get('username')
                group = Group.objects.get(name='customer')
                user.groups.add(group)
                customer.objects.create(
                    user=user,
                )
                messages.success(request, 'Account was created for ' + username)
                return redirect('login')
        context = {'form':form}
        return render(request,'accounts/register.html',context)

@unauthenticated_user
def loginpage(request):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username,password=password)
            if user is not None:
                login(request,user)
                return redirect('home')
            else:
                messages.info(request, 'Username OR password is incorrect')
        context = {}
        return render(request,'accounts/login.html',context)

def logoutuser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@admin_only
def home(request):
    orders = order.objects.all()
    customers = customer.objects.all()
    total_customers=customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status="Delivered").count()
    pending  = orders.filter(status="Pending").count()
    context = {'orders':orders ,'total_orders':total_orders,'customers':customers,'total_customers':total_customers,'delivered':delivered,'pending':pending}
    return render(request,'accounts/dashboard.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status="Delivered").count()
    pending  = orders.filter(status="Pending").count()
   
    context = {'orders':orders,'total_orders':total_orders,'delivered':delivered,'pending':pending}
    return render(request, 'accounts/user.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    user=request.user.customer
    form = CustomerForm(instance=user)

    if request.method == 'POST':
        form = CustomerForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
    context={'form':form}
    return render(request, 'accounts/account_settings.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = product.objects.all()
    return render(request,'accounts/products.html',{'products':products})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customers(request,pk):
    customer_id = customer.objects.get(id=pk)
    orders= customer_id.order_set.all()
    orderscnt=orders.count()
    #print(orderscnt)
    myfilter = orderfiter(request.GET, queryset=orders)
    orders=myfilter.qs
    context = {'customer':customer_id,'orders':orders,'myfilter':myfilter,'orderscnt':orderscnt}
    return render(request,'accounts/customer.html',context)
   
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createorders(request,pk):
    orderFormSet = inlineformset_factory(customer,order, fields=('product','status'),can_delete=False)
    customerpk = customer.objects.get(id=pk)
    formset= orderFormSet(queryset=order.objects.none(), instance=customerpk)
   # form = orderform(initial={'customer':customerpk})
    if request.method == 'POST':
       # print('Printing POST:',request.POST)
       # form = orderform(request.POST)
        formset= orderFormSet(request.POST,instance=customerpk)

        if formset.is_valid():
            formset.save()
            return redirect('/')
    context = {'formset':formset}
    return render(request,'accounts/order_form.html',context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateorder(request,pk):
    orderpk = order.objects.get(id=pk)
    form = orderform(instance=orderpk)
    if request.method == 'POST':
       # print('Printing POST:',request.POST)
        form = orderform(request.POST, instance=orderpk)
        if form.is_valid():
            form.save()
            return redirect('/')
    context={'form':form}
    return render(request,'accounts/order_form.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteorder(request,pk):
    orderpk = order.objects.get(id=pk)
    if request.method == 'POST':
        orderpk.delete()
        return redirect('/')
    context={'item':orderpk}
    return render(request, 'accounts/delete.html',context)