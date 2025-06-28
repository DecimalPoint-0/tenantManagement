from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from core import models
from core.forms import CreatePropertyForm, CustomLoginForm, LoginForm, UserRegisterForm
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.contrib.auth import get_user_model
User = get_user_model()


def login_view(request):
    """View for handling login"""

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                print("valid credentials")
                return JsonResponse({
                    'code': '200',
                    'message': 'Login Successful',
                    'status': True
                })
            else:
                return JsonResponse({
                    'code': '403',
                    'message': 'Invalid login details',
                    'status': False
                })
        except ObjectDoesNotExist:
            return JsonResponse({
                'code': '404',
                'message': 'user not found',
                'status': False
            })
    return render(request, 'login.html')


def register_view(request):
    """View for registration"""

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
        
    return render(request, 'accounts/sign-up.html', {'form': form})


@login_required(login_url='login')
def dashboard(request):
    """View for dashboard"""

    total_users = models.User.objects.all().count()
    property_type = models.PropertyType.objects.all().count()
    property_count = models.Property.objects.all().count()
    tenant_count = 0
    total_report = 0
    total_payment = 0


    if request.user.app_level_role == 'landlord':
        property_count = models.Property.objects.filter(landlord=request.user).count()
        tenant_count = models.User.objects.filter(
            unit__property__landlord=request.user,
            app_level_role='tenant'
        ).distinct().count()
        total_payment = models.RentPayment.objects.filter(
            payment_status='PAID',
            unit__property__landlord=request.user
        ).aggregate(total=Sum('amount'))
        total_report = models.TenantReport.objects.filter(unit__property__landlord=request.user).count()

    elif request.user.app_level_role != 'landlord':
        property_count = models.Property.objects.all().count()
        tenant_count = models.Unit.objects.all().count()
        total_report = models.TenantReport.objects.all().count()
        total_payment = models.RentPayment.objects.filter(payment_status='PAID').aggregate(total=Sum('amount'))

    context = {
        'property_count': property_count or 0,
        'tenant_count': tenant_count or 0,
        'total_report': total_report or 0,
        'total_payment': total_payment['total'] or 0.0,
        'total_users': total_users or 0,
        'property_type': property_type or 0

    }

    return render(request, 'home.html', context=context)


def logout_view(request):
    """Logout view"""

    logout(request)
    return redirect('login')


@login_required(login_url='login')
def properties(request):
    """Properties view"""

    categories = models.PropertyType.objects.all()
    if request.method == 'POST':
        landlord = request.user
        name = request.POST.get('name')
        type = request.POST.get('type')
        house_type = categories.get(id=type)
        description = request.POST.get('description')
        image = request.POST.get('image')
        number_of_units = request.POST.get('number_of_units')
        address = request.POST.get('address')


        models.Property.objects.get_or_create(
                landlord=landlord, name=name, type=house_type, description=description, image=image, number_of_units=number_of_units, address=address
        )

        return JsonResponse({
            'code': '200',
            'message': 'Property added successfully',
            'status': True
        })

    if request.user.is_authenticated:
        if request.user.app_level_role == 'landlord':
            properties = models.Property.objects.filter(landlord=request.user)
        else:
            properties = models.Property.objects.all()

    return render(request, 'houses.html', {'properties': properties, 'categories': categories})


def property_list(request):
    """View for listing all properties """

    properties = models.Property.objects.all()
    if request.user.app_level_role == "landlord":
        properties = models.Property.objects.filter(landlord=request.user)
    
    return render(request, 'manage_houses.html', {'properties': properties})

from django.views.decorators.csrf import csrf_exempt


@login_required(login_url='login')
@csrf_exempt
def category_delete(request, id):
    """View for delete category """

    category = models.PropertyType.objects.get(id=id)
    if request.user.app_level_role == 'admin':
        category.delete()
    
        return JsonResponse({
            'code': '200',
            'message': 'Category deleted successfully',
            'status': True
        })
        

@login_required(login_url='login')
@csrf_exempt
def property_delete(request, id):
    """View for delete product """

    property = models.Property.objects.get(id=id)
    if request.user.app_level_role == 'admin' or request.user == property.landlord:
        property.delete()
    
        return JsonResponse({
            'code': '200',
            'message': 'Property deleted successfully',
            'status': True
        })


@login_required(login_url='login')
def property_edit(request, id):
    """Property edit view"""
    
    property = models.Property.objects.get(id=id)
    categories = models.PropertyType.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        type = request.POST.get('type')
        house_type = categories.get(id=type)
        description = request.POST.get('description')
        image = request.POST.get('image')
        number_of_units = request.POST.get('number_of_units')
        address = request.POST.get('address')

        property.name = name
        property.type = house_type
        property.description = description
        property.image = image
        property.number_of_units = number_of_units
        property.address = address
        property.save()

        return JsonResponse({
            'code': '200',
            'message': 'Property updated successfully',
            'status': True
        })

    return render(request, 'edit-prod.html', {'property': property, 'categories': categories})



"""
Categories / House Type views start here

"""
def categories(request):
    """View for adding house type"""

    property_type = models.PropertyType.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        if models.PropertyType.objects.filter(name=name).exists():
            return JsonResponse({
                'code': '401',
                'message': "House Type already exist",
                'status': False
            })

        models.PropertyType.objects.create(
            name=name, description=description
        )

        return JsonResponse({
            'code': '200',
            'message': 'Category added successfully',
            'status': True
        })

    return render(request, 'categories.html', context={
        'property_type': property_type
    })


def manage_categories(request):
    """View for managing house type"""

    house_types = models.PropertyType.objects.all()
    return render(request, 'manage_categories.html', {'house_types': house_types})


def edit_categories(request, id):
    """View for deleting house type"""

    house_type = models.PropertyType.objects.get(id=id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        house_type.name = name
        house_type.description = description
        house_type.save()
        return JsonResponse({
            'code': '200',
            'message': 'Category Updated successfully',
            'status': True
        })

    return render(request, 'edit-cate.html', {'house_type': house_type})


def tenants(request):
    """View for tenants"""
    
    tenants = models.TenantProfile.objects.filter(current_unit__property__landlord=request.user)
    print(tenants)

    return render(request, 'tenants.html', {'tenants': tenants})


@login_required(login_url='login')
def create_tenant(request):
    """View for creating a new tenant"""

    properties = models.Property.objects.filter(landlord=request.user)

    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        contact = request.POST.get('contact')
        unit_id = request.POST.get('unit')
        date_in = request.POST.get('date_in')
        duration = request.POST.get('duration')

        # Basic validation
        if not all([email, first_name, last_name, contact, unit_id, date_in, duration]):
           return JsonResponse({
               'code': '401',
               'message': "All fields are required",
               'status': False
           })

        try:
            unit = models.Unit.objects.get(id=unit_id)
        except models.Unit.DoesNotExist:
            
            return JsonResponse({
               'code': '401',
               'message': "Selected unit does not exist.",
               'status': False
            })

        if unit.is_occupied:
            return JsonResponse({
               'code': '401',
               'message': "Selected unit is already occupied.",
               'status': False
            })

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({
               'code': '403',
               'message': "A user with this email already exists.",
               'status': False
            })

        try:
            lease_start_date = datetime.strptime(date_in, "%Y-%m-%d").date()
            lease_end_date = lease_start_date + relativedelta(months=int(duration))

            # Create user manually
            password = "Tenant@123"
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                app_level_role='tenant'
            )

            # Assign unit and create tenant profile
            models.TenantProfile.objects.create(
                user=user,
                current_unit=unit,
                lease_start_date=lease_start_date,
                lease_end_date=lease_end_date,
                emergency_contact=contact
            )

            unit.is_occupied = True
            unit.tenant = user
            unit.save()

            return JsonResponse({
               'code': '201',
               'message': "Tenant Created Successfully",
               'status': True
            })
        
        except Exception as e:
            return JsonResponse({
               'code': '500',
               'message': f"An error occurred: {str(e)}",
               'status': False
            })

    return render(request, 'manage_tenant.html', {'properties': properties})


def edit_tenant(request, id):
    """View for editing tenant"""

    tenant = models.TenantProfile.objects.get(
        current_unit__property__landlord= request.user, id=id
    )

    if request.method == 'POST':
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        contact = request.POST.get('contact')
        unit_id = request.POST.get('unit')
        date_in = request.POST.get('date_in')
        duration = request.POST.get('duration')
        
        try:
            unit = models.Unit.objects.get(id=unit_id)
        except models.Unit.DoesNotExist:
            
            return JsonResponse({
               'code': '401',
               'message': "Selected unit does not exist.",
               'status': False
            })
        
        if unit.is_occupied:
            return JsonResponse({
               'code': '500',
               'message': "Selected Unit is already occupied.",
               'status': False
            })
        
        
        try: 
            # update property
            lease_start_date = datetime.strptime(date_in, "%Y-%m-%d").date()
            lease_end_date = lease_start_date + relativedelta(months=int(duration))

            tenants.user.first_name = first_name
            tenants.user.last_name = last_name
            tenants.emergency_contact = contact
            tenants.unit = unit
            tenants.lease_start_date = lease_start_date
            tenants.lease_end_date = lease_end_date

            tenants.save()

            return JsonResponse({
               'code': '200',
               'message': "Tenant Details Updated successfully",
               'status': True
            })

        except Exception as e:
            return JsonResponse({
               'code': '500',
               'message': f"An error occurred: {str(e)}",
               'status': False
            })
    return render(request, 'edit-tenant.html', {'tenant': tenant})

@csrf_exempt
@login_required(login_url='login')
def delete_tenant(request, id):
    """View for deleting tenant"""

    tenant = models.TenantProfile.objects.get(
        current_unit__property__landlord= request.user, id=id
    )

    if request.user.app_level_role != 'tenant':
        tenant.delete()
    
        return JsonResponse({
            'code': '200',
            'message': 'Tenant deleted successfully',
            'status': True
        })
    

def landlords(request):
    """View for landlords"""
    
    landlords = models.User.objects.filter(app_level_role="landlord")

    return render(request, 'landlord.html', {'landlords': landlords})


@login_required(login_url='login')
def create_landlord(request):
    """View for creating a new landlord"""

    landlords = models.User.objects.filter(app_level_role="landlord")

    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({
               'code': '403',
               'message': "A user with this email already exists.",
               'status': False
            })

        try:
            # Create user manually
            password = "Landlord@123"
            
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                app_level_role='landlord'
            )

           

            return JsonResponse({
               'code': '201',
               'message': "Landlord Created Successfully",
               'status': True
            })
        
        except Exception as e:
            return JsonResponse({
               'code': '500',
               'message': f"An error occurred: {str(e)}",
               'status': False
            })

    return render(request, 'manage_landlord.html', {'landlords': landlords})


def edit_landlord(request, id):
    """View for editing landlord"""

    landlord = models.User.objects.get(
        id=id
    )

    if request.method == 'POST':
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        
        try: 
            landlords.user.first_name = first_name
            landlords.user.last_name = last_name


            landlords.save()

            return JsonResponse({
               'code': '200',
               'message': "Landlord Details Updated successfully",
               'status': True
            })

        except Exception as e:
            return JsonResponse({
               'code': '500',
               'message': f"An error occurred: {str(e)}",
               'status': False
            })
    return render(request, 'edit-landlord.html', {'landlord': landlord})

@csrf_exempt
@login_required(login_url='login')
def delete_landlord(request, id):
    """View for deleting landlord"""

    landlord = models.User.objects.get(
        id=id
    )

    if request.user.app_level_role != 'tenant':
        landlord.delete()
    
        return JsonResponse({
            'code': '200',
            'message': 'Landlord deleted successfully',
            'status': True
        })


@login_required(login_url='login')
def get_units_by_property(request, property_id):
    """Returns units for a given property"""

    print("property_id")
    units = models.Unit.objects.filter(property__id=property_id)
    units_data = [{'id': unit.id, 'unit_number': unit.unit_number} for unit in units]

    return JsonResponse({'units': units_data})


@login_required(login_url='login')
def manage_unit(request):
    """View for managing unit"""
    units = models.Unit.objects.all()

    if request.user.app_level_role == 'landlord':
        units = models.Unit.objects.filter(property__landlord=request.user)
    return render(request, 'manage_units.html', {'units': units})


@login_required(login_url='login')
def create_unit(request):
    """View for creating unit"""
    
    properties = models.Property.objects.filter(landlord=request.user)
    if request.method == 'POST':
        prop_id = request.POST.get("prop_id")
        unit_number = request.POST.get("unit_number")
        monthly_rent = request.POST.get('monthly_rent')
       
        property = models.Property.objects.get(id=prop_id)
        models.Unit.objects.create(
            property=property,
            unit_number=unit_number,
            monthly_rent=monthly_rent
        )

        return JsonResponse({
            'code': '200',
            'message': 'Unit Added successfully',
            'status': True
        })
    return render(request, 'units.html', {'properties': properties})


def edit_unit(request, id):
    """View for editing unit"""

    unit = models.Unit.objects.get(id=id)

    if request.method == 'POST':
        prop_id = request.POST.get("prop_id")
        unit_number = request.POST.get("unit_number")
        monthly_rent = request.POST.get('monthly_rent')

        property = models.Property.objects.get(id=prop_id)

        unit.property = property
        unit.unit_number = unit_number
        unit.monthly_rent = monthly_rent

        return JsonResponse({
            'code': '200',
            'message': 'Unit Updated successfully',
            'status': True
        })


@login_required(login_url='login')
@csrf_exempt
def delete_unit(request, id):
    """View for deleting unit"""

    unit = models.Unit.objects.get(id=id)
    if request.user.app_level_role == 'admin' or request.user == unit.property.landlord:
        unit.delete()
    
        return JsonResponse({
            'code': '200',
            'message': 'Unit deleted successfully',
            'status': True
        })
    

@login_required(login_url='login')
def payments(request):
    """ View for list of payments"""

    if request.user.app_level_role == 'landlord':
        payments = models.RentPayment.objects.filter(
            unit__property__landlord=request.user
        )
    elif request.user.app_level_role == 'admin':
        payments = models.RentPayment.objects.all()
    else:
        payments = models.RentPayment.objects.filter(
            tenant=request.user
        )

    return render(request, 'payments.html', {'payments': payments})


from django.shortcuts import render, get_object_or_404
@login_required(login_url='login')
def rentage(request):
    rent = get_object_or_404(models.TenantProfile, user=request.user)
    payment_status = 'Not Paid'

    if rent.current_unit:
        payments = rent.current_unit.rent_payment.all()
        if payments.exists():
            payment = payments.latest('created_at')  # or use filter to get the current one
            payment_status = payment.payment_status

    return render(request, 'rentage.html', {
        'rent': rent,
        'payment_status': payment_status
    })


import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
@csrf_exempt
def verify_payment(request):
    if request.method == 'POST':
        reference = request.POST.get('reference')
        rent_id = request.POST.get('rent_id')

        headers = {
            "Authorization": "Bearer sk_test_0f5250fad4657fffea14ad4d8f127f3c5d71c8f1",  # Replace with your secret key
        }
        url = f"https://api.paystack.co/transaction/verify/{reference}"

        resp = requests.get(url, headers=headers)
        result = resp.json()

        if result.get('data') and result['data'].get('status') == 'success':
            try:
                rent = models.TenantProfile.objects.get(user=request.user)
                rent_payments = rent.current_unit.rent_payment.all()  # Reverse FK manager

                if rent_payments.exists():
                    payment = rent_payments.latest('created_at')
                else:
                    # Create a new RentPayment if none exists (optional based on your logic)
                    payment = models.RentPayment.objects.create(
                        tenant=request.user,
                        unit=rent.current_unit,
                        amount=result['data']['amount'] / 100,  # amount in NGN
                        payment_status='Paid',
                        transaction_reference=reference
                    )

                # Mark payment as successful
                # payment.tenant = request.user
                payment.payment_status = 'Paid'
                payment.payment_for_month = 'June'
                payment.transaction_reference = reference
                payment.save()

                return JsonResponse({
                    'code': '200',
                    'redirect_url': reverse('payment-receipt', args=[reference])
                })

            except models.TenantProfile.DoesNotExist:
                return JsonResponse({'code': '500', 'message': 'Tenant not found'}, status=False)
            except Exception as e:
                return JsonResponse({'code': '500', 'message': str(e)}, status=False)

        return JsonResponse({'code': '500', 'message': 'Payment not verified'}, status=False)


@login_required(login_url='login')
def payment_receipt(request, reference):
    payment = get_object_or_404(models.RentPayment, transaction_reference=reference)
    return render(request, 'receipt.html', {'payment': payment})


@login_required(login_url='login')
def add_report(request):
    """View for adding reports"""

    if request.method == 'POST':
        tenant = request.user

        unit = models.Unit.objects.get(tenant=tenant)

        title = request.POST.get('name')
        description = request.POST.get('description')

        models.TenantReport.objects.create(
            tenant= tenant,
            unit= unit,
            title= title,
            description= description
        )

        return JsonResponse({
            'code': '200',
            'message': "Report added successfully"
        })
    return render(request, 'report.html')


@login_required(login_url='login')
def list_report(request):
    """View of listing reports"""

    reports = models.TenantReport.objects.all()
    if request.user.app_level_role == "tenant":
        reports = models.TenantReport.objects.filter(tenant=request.user)
    elif request.user.app_level_role == "landlord":
        reports = models.TenantReport.objects.filter(unit__property__landlord=request.user)

    return render(request, 'report_list.html', {'reports': reports})
    
