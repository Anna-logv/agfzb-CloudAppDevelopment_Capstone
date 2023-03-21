from django.db import models
from django.utils.timezone import now
from datetime import datetime

# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object

class CarMake(models.Model):
    name=models.CharField(null=False, max_length=100, default='Car')
    description=models.CharField(null=True,blank=True,max_length=255)
    is_lux=models.BooleanField(default=False)
    def _is_lux_str(self):
        if self.is_lux:
            return " (LUX) "
        else:
            return ""
    def __str__(self):
        return self.name + self._is_lux_str()

# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
#Sedan · Hatchback · MPV/Minivan · SUV · CUV/Crossover · Pickup · Jeep · Coupe
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object
class CarModel(models.Model):
    CAR_TYPE_CHOICES = [
        ('SEDAN', 'Sedan'),
        ('HATCHBACK', 'Hatchback'),
        ('MPV', 'MPV/Minivan'),
        ('SUV', 'SUV'),
        ('CUV', 'CUV/Crossover'),
        ('PICKUP', 'Pickup'),
        ('JEEP', 'Jeep'),
        ('COUPE', 'Coupe'),
        ('OTHER', 'Other'),
    ]
    carmake=models.ForeignKey(CarMake, null=True, on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    dealer_id=models.IntegerField(default=0)
    type=models.CharField(
        null=False,
        max_length=20,
        choices=CAR_TYPE_CHOICES,
        default='SEDAN'
    )
    year=models.DateField(default=datetime.now)
    number_of_seats=models.PositiveIntegerField(default=5)
    def __str__(self):
        return self.name+" ("+self.type+") - "+self.year.strftime('%Y')
# <HINT> Create a plain Python class `CarDealer` to hold dealer data


# <HINT> Create a plain Python class `DealerReview` to hold review data
