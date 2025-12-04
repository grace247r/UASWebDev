from django.db import models


class Booking(models.Model):
    
    passenger_name = models.CharField(max_length=100)
    passport_number = models.CharField(max_length=50)
    
    
    origin = models.CharField(max_length=10)
    destination = models.CharField(max_length=10)
    airline = models.CharField(max_length=50)
    flight_date = models.DateTimeField(null=True, blank=True)
    price = models.IntegerField() 
    
   
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.passenger_name} - {self.origin} ke {self.destination}"