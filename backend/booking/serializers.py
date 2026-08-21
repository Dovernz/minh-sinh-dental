from rest_framework import serializers
from .models import Clinic, Service, Booking, Customer

class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    clinic = ClinicSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
