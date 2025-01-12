from django.db import models
from django.core.validators import MinValueValidator

class BHAComponent(models.Model):
    name = models.CharField(max_length=100)
    length = models.FloatField(validators=[MinValueValidator(0.1)])
    diameter = models.FloatField(validators=[MinValueValidator(0.1)])
    image = models.ImageField(upload_to='bha_components/', null=True, blank=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    weight = models.FloatField(validators=[MinValueValidator(0)], null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.length}m"

class BHAConfiguration(models.Model):
    """Model to store complete BHA configurations"""
    name = models.CharField(max_length=100)
    total_length = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bha_image = models.ImageField(
        upload_to='bha_configurations/', 
        null=True, 
        blank=True
    )

    def __str__(self):
        return f"BHA Configuration: {self.name}"

class BHAConfigurationItem(models.Model):
    """Represents individual components in a BHA configuration"""
    configuration = models.ForeignKey(BHAConfiguration, related_name='items', on_delete=models.CASCADE)
    component = models.ForeignKey(BHAComponent, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField()
    position = models.FloatField(default=0)  # Position from top in meters

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.quantity} x {self.component.name}"