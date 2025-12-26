from django.urls import path
from .views import register, login_view,supplier_dashboard,farmer_dashboard,no_role,fieldofficer_dashboard,logout_view,farmer_profile,add_product,supplier_profile,edit_product,delete_product,place_order,supplier_orders,export_report_pdf,update_order_status

urlpatterns = [
    path('', login_view, name='login'),
    path('register', register, name='register'),
    path('supplier/dashboard/', supplier_dashboard, name='supplier_dashboard'),
    path('farmer/dashboard/', farmer_dashboard, name='farmer_dashboard'),
    path('fieldofficer/dashboard/', fieldofficer_dashboard, name='fieldofficer_dashboard'),
    path('no_role/', no_role, name='no_role'),
    path('logout/', logout_view, name='logout'),
    path('farmer/profile/', farmer_profile, name='farmer_profile'),
    path('supplier/profile/', supplier_profile, name='supplier_profile'),
    path('supplier/product/add/', add_product, name='add_product'),
    path('supplier/product/edit/<int:product_id>/', edit_product, name='edit_product'),
    path('supplier/product/delete/<int:product_id>/', delete_product, name='delete_product'),
    path('order/<int:product_id>/', place_order, name='place_order'),
    path('supplier/orders/', supplier_orders, name='supplier_orders'),
    path('supplier/orders/update/<int:order_id>/<str:status>/', update_order_status, name='update_order_status'),
    path('field-officer/report/', export_report_pdf, name='export_report'),




]
