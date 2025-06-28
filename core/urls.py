
from django.conf import settings
from django.urls import path
from core import views
from django.conf.urls.static import static


urlpatterns = [
    # authentication urls
    path('', views.login_view, name='login'),
    path('register', views.register_view, name='register'),

    # dashboard urls
    path('dashboard', views.dashboard, name='dashboard'),


    # manage properties
    path('properties', views.properties, name='properties'),
    path('properties/edit/<int:id>', views.property_edit, name='property-edit'),
    path('properties/list', views.property_list, name='property-list'),
    path('properties/delete/<int:id>', views.property_delete, name='property-delete'),

    # manage categories 
    path('categories', views.categories, name='categories'),
    path('categories/manage', views.manage_categories, name='manage_categories'),
    path('categories/<int:id>/manage', views.edit_categories, name='edit_categories'),
    path('categories/<int:id>/delete', views.category_delete, name='category_delete'),

    # tenants
    path('tenants', views.tenants, name="tenants"),
    path('tenants/create', views.create_tenant, name="create-tenant"),
    path('tenants/delete/<int:id>', views.delete_tenant, name="delete-tenant"),
    path('tenants/edit/<int:id>', views.edit_tenant, name="edit-tenant"),


    # landlord
    path('landlords', views.landlords, name="landlords"),
    path('landlords/create', views.create_landlord, name="create-landlord"),
    path('landlords/delete/<str:id>', views.delete_landlord, name="delete-landlord"),
    path('landlords/edit/<str:id>', views.edit_landlord, name="edit-landlord"),

    # Units
    path('units', views.manage_unit, name="manage-units"),
    path('unit/create', views.create_unit, name="create-unit"),
    path('unit/edit/<int:id>', views.edit_unit, name="edit-unit"),
    path('unit/delete/<int:id>', views.delete_unit, name="delete-unit"),
    path('get-units-by-property/<int:property_id>/', views.get_units_by_property, name='get_units_by_property'),

    # rentage
    path('rentage', views.rentage, name="rentage"),
    path('add-report', views.add_report, name="add-report"),
    path('list-report', views.list_report, name="list-report"),

    # payments
    path('payments', views.payments, name="payments"),
    path('verify_payment', views.verify_payment, name="verify-payment"),
    path('receipt/<str:reference>/', views.payment_receipt, name='payment-receipt'),

    # logout
    path('logout', views.logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)