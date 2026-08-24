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
    category = ServiceCategorySerializer(read_only=True)
    service_detail = ServiceDetailSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
