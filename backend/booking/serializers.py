from rest_framework import serializers
from .models import Clinic, ServiceDetail, ServiceCategory, Booking, Customer

class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = '__all__'

class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = '__all__'

class ServiceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceDetail
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    clinic = ClinicSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'

from .models import SiteSettings, MenuLink, ClinicBranch, SocialLink

class ClinicBranchSerializer(serializers.ModelSerializer):
    class Meta: 
        model = ClinicBranch
        fields = '__all__'

class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta: 
        model = SocialLink
        fields = '__all__'

class SiteSettingsSerializer(serializers.ModelSerializer):
    branches = ClinicBranchSerializer(many=True, read_only=True)
    social_links = SocialLinkSerializer(many=True, read_only=True)
    class Meta: 
        model = SiteSettings
        fields = '__all__'

class MenuLinkSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    class Meta:
        model = MenuLink
        fields = ['id', 'title', 'url', 'order', 'parent', 'children']
    def get_children(self, obj):
        children = obj.children.filter(is_active=True).order_by('order')
        return MenuLinkSerializer(children, many=True).data
