from django.contrib import admin
# from .models import related models
from .models import CarMake, CarModel
from datetime import date
from django import forms

#widjet to change datefield to year
class DateSelectorWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        current_year=date.today().strftime("%Y")
        years = [(year, year) for year in range(1940,int(current_year)+1)]
        widgets = [
            #forms.Select(attrs=attrs, choices=days),
            #forms.Select(attrs=attrs, choices=months),
            forms.Select(attrs=attrs, choices=years),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if isinstance(value, date):
            return [value.year]
        elif isinstance(value, str):
            year = value.split('-')
            return [year[0]]
        return [None]

    def value_from_datadict(self, data, files, name):
        year = super().value_from_datadict(data, files, name)
        print(year[0])
        return '{}-01-01'.format(year[0])
# Register your models here.

# CarModelInline class
class CarModelInline(admin.StackedInline):
    model = CarModel 
    extra = 0
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'year':
            kwargs['widget'] = DateSelectorWidget()
        return super(CarModelInline,self).formfield_for_dbfield(db_field,**kwargs)

#  class
# form to attach year widget
class YearCarModelAdminForm(forms.ModelForm):
  class Meta:
    model = CarModel
    widgets = {
      'year': DateSelectorWidget(),
    }
    fields = '__all__'

class CarModelAdmin(admin.ModelAdmin):
    form = YearCarModelAdminForm
    fields = ['carmake', 
              'name',  
              'dealer_id',  
              'type',  
              'year',  
              'number_of_seats']
    list_filter = ['carmake', 'type']

# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'is_lux']
    inlines = [CarModelInline]
    list_filter = ['is_lux']

# Register models here
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)