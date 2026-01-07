from django.contrib.auth.models import Group
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm,FarmerProfileForm,SupplierProfileForm
from django import forms
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import FarmerProfile,SupplierProfile,Product,Order

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            role = form.cleaned_data['role']
            group = Group.objects.get(name=role)
            user.groups.add(group)

            # ✅ create farmer profile automatically
            if role == 'Farmer':
                FarmerProfile.objects.create(
                    user=user,
                    full_name=user.username
                )

            elif role == 'Supplier':
                 SupplierProfile.objects.create(
                    user=user,
                    company_name=user.username
                )


            messages.success(request, f'Account created as {role}')
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'register.html', {'form': form})

@login_required
def farmer_profile(request):
    if not request.user.groups.filter(name='Farmer').exists():
        return redirect('login')

    profile, created = FarmerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = FarmerProfileForm(
            request.POST,
            request.FILES,   # ✅ VERY IMPORTANT
            instance=profile
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('farmer_dashboard')
        else:
            print(form.errors)  # 👈 Debug helper
    else:
        form = FarmerProfileForm(instance=profile)

    return redirect('farmer_dashboard')


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username', 'required': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'required': True})
    )


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")

            # role-based redirect
            if user.groups.filter(name="Supplier").exists():
                return redirect("supplier_dashboard")
            elif user.groups.filter(name="Farmer").exists():
                return redirect("farmer_dashboard")
            elif user.groups.filter(name="Field Officer").exists():
                return redirect("fieldofficer_dashboard")
            else:
                return redirect("no_role")

        else:
            messages.error(request, "Invalid username or password")

    # GET request OR failed login
    return render(request, "login.html")

def no_role(request):
    messages.error(request, 'No role assigned. Contact admin.')
    return render(request, 'login.html')


@login_required
def farmer_dashboard(request):

    if not request.user.groups.filter(name="Farmer").exists():
        return redirect("login")

    farmer_profile, _ = FarmerProfile.objects.get_or_create(user=request.user)

    products = Product.objects.all()

    orders = Order.objects.filter(
        farmer=farmer_profile
    ).order_by('-created_at')

    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity"))

        product = Product.objects.get(id=product_id)

        Order.objects.create(
            farmer=farmer_profile,
            supplier=product.supplier,
            product=product,
            quantity=quantity,
            status="pending"
        )

        return redirect("farmer_dashboard")

    return render(request, "farmer/farmer_dashboard.html", {
        "farmer_profile": farmer_profile,
        "products": products,
        "orders": orders,
        "total_products": products.count(),
        "total_orders": orders.count(),
    })


@login_required
def fieldofficer_dashboard(request):
    # Only Field Officers
    if not request.user.groups.filter(name="Field Officer").exists():
        return redirect("login")

    farmers = FarmerProfile.objects.all()
    suppliers = SupplierProfile.objects.all()
    products = Product.objects.all()
    orders = Order.objects.all()

    context = {
        "farmers": farmers,
        "suppliers": suppliers,
        "products": products,
        "orders": orders,

        # Summary
        "total_farmers": farmers.count(),
        "total_suppliers": suppliers.count(),
        "total_products": products.count(),
        "total_orders": orders.count(),
    }

    return render(request, "fieldofficer/fieldofficer_dashboard.html", context)


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return render(request, 'login.html')





# @login_required
# def farmer_orders(request):
#     orders = Order.objects.filter(farmer=request.user)
#     return render(request, 'orders/farmer_orders.html', {'orders': orders})


@login_required
def export_report_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="system_report.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 40

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, y, "FARM MANAGEMENT SYSTEM REPORT")
    y -= 40

    # ================= FARMERS =================
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Farmers")
    y -= 20

    for farmer in FarmerProfile.objects.all():
        p.setFont("Helvetica", 10)
        p.drawString(50, y, f"- {farmer.full_name} | {farmer.phone}")
        y -= 15

    y -= 20

    # ================= SUPPLIERS =================
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Suppliers")
    y -= 20

    for s in SupplierProfile.objects.all():
        p.setFont("Helvetica", 10)
        p.drawString(50, y, f"- {s.company_name} | {s.phone}")
        y -= 15

    y -= 20
    
    # ================= PRODUCTS =================
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Products")
    y -= 20

    for pdt in Product.objects.all():
        p.setFont("Helvetica", 10)
        p.drawString(
            50, y,
            f"- {pdt.name} | Price: {pdt.price} | Stock: {pdt.stock}"
        )
        y -= 15

    y -= 20

    # ================= ORDERS =================
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Orders")
    y -= 20

    for order in Order.objects.all():
        p.setFont("Helvetica", 10)
        p.drawString(
            50,
            y,
            f"- {order.product} | Farmer: {order.farmer.user.username} | Status: {order.status}"
        )
        y -= 15

    p.showPage()
    p.save()

    return response



# ---------------- Supplier Dashboard ----------------
@login_required
def supplier_dashboard(request):
    if not request.user.groups.filter(name="Supplier").exists():
        return redirect("login")

    supplier_profile, _ = SupplierProfile.objects.get_or_create(user=request.user)

    products = Product.objects.filter(supplier=supplier_profile)
    orders = Order.objects.filter(supplier=supplier_profile).order_by('-created_at')

    total_products = products.count()
    total_orders = orders.count()

    return render(request, "supplier/supplier_dashboard.html", {
        "products": products,
        "orders": orders,
        "supplier_profile": supplier_profile,
        "total_products": total_products,
        "total_orders": total_orders,
    })


# ---------------- Add Product ----------------
@login_required
def add_product(request):
    if not request.user.groups.filter(name='Supplier').exists():
        return redirect('login')

    supplier = SupplierProfile.objects.get(user=request.user)

    if request.method == 'POST':
        Product.objects.create(
            supplier=supplier,
            name=request.POST['name'],
            price=request.POST['price'],
            stock=request.POST['stock']
        )
        messages.success(request, 'Product added successfully')
        return redirect('supplier_dashboard')
    return redirect('supplier_dashboard')


# ---------------- Edit Product ----------------
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.supplier.user != request.user:
        return redirect("login")

    if request.method == "POST":
        product.name = request.POST['name']
        product.price = request.POST['price']
        product.stock = request.POST['stock']
        product.save()
        messages.success(request, 'Product updated successfully')
    return redirect("supplier_dashboard")


# ---------------- Delete Product ----------------
@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.supplier.user != request.user:
        return redirect("login")

    product.delete()
    messages.success(request, 'Product deleted successfully')
    return redirect("supplier_dashboard")


# ---------------- Supplier Profile ----------------
@login_required
def supplier_profile(request):
    if not request.user.groups.filter(name="Supplier").exists():
        return redirect("login")

    supplier_profile, _ = SupplierProfile.objects.get_or_create(
        user=request.user,
        defaults={'company_name': request.user.username}
    )

    if request.method == "POST":
        form = SupplierProfileForm(request.POST, request.FILES, instance=supplier_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect("supplier_dashboard")
    else:
        form = SupplierProfileForm(instance=supplier_profile)

    return redirect("supplier_dashboard")


# ---------------- Place Order (Farmer Side) ----------------
@login_required
def place_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    farmer_profile = get_object_or_404(FarmerProfile, user=request.user)
    supplier = product.supplier

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 0))
        if quantity > 0 and quantity <= product.stock:
            Order.objects.create(
                product=product,
                supplier=supplier,
                farmer=farmer_profile,
                quantity=quantity
            )
            product.stock -= quantity
            product.save()
            messages.success(request, f"Order for {product.name} placed successfully!")
        else:
            messages.error(request, "Invalid quantity")
    return redirect('farmer_dashboard')


# ---------------- Supplier Orders ----------------
@login_required
def supplier_orders(request):
    if not request.user.groups.filter(name="Supplier").exists():
        return redirect('login')

    supplier = SupplierProfile.objects.get(user=request.user)
    orders = Order.objects.filter(supplier=supplier).order_by('-created_at')

    return render(request, 'supplier/orders.html', {
        'orders': orders,
        'is_supplier': True
    })


# ---------------- Update Order Status ----------------
@login_required
def update_order_status(request, order_id, status):
    if not request.user.groups.filter(name="Supplier").exists():
        return redirect('login')

    order = get_object_or_404(Order, id=order_id)
    if order.supplier.user == request.user:
        order.status = status
        order.save()
        messages.success(request, f"Order status updated to {status}")
    return redirect('supplier_dashboard')
