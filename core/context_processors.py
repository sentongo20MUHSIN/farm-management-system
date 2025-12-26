from .models import FarmerProfile, SupplierProfile

def user_profiles(request):
    farmer_profile = None
    supplier_profile = None

    if request.user.is_authenticated:
        farmer_profile = FarmerProfile.objects.filter(user=request.user).first()
        supplier_profile = SupplierProfile.objects.filter(user=request.user).first()

    return {
        "farmer_profile": farmer_profile,
        "supplier_profile": supplier_profile,
        "is_farmer": farmer_profile is not None,
        "is_supplier": supplier_profile is not None,
    }
