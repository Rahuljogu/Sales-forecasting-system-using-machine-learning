from django.contrib import admin
from .models import SalesData

admin.site.register(SalesData)

from .models import Dataset

admin.site.register(Dataset)