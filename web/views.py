from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from django.shortcuts import render

import requests


def index(request):
    response1 = requests.get('http://optimal_power_time_calculator:80/api/next-optimal-hour?numHoursToForecast=3h35m')
    price1 = json_to_optimal_time_appliance("Test", response1.json()['price'])

    response = requests.get('http://optimal_power_time_calculator:80/api/next-optimal-hour?numHoursToForecast=1h35m')
    price = json_to_optimal_time_appliance("Test", response.json()['price'])

    return render(request, 'index.html', {'optimal_times': [price, price1]})


@dataclass
class OptimalTimeAppliance:
    name: str
    from_dt: datetime
    to_dt: datetime
    price: Decimal
    suboptimal_price_multiplier: Decimal

def json_to_optimal_time_appliance(name, json):
    return OptimalTimeAppliance(
        name=name,
        from_dt=datetime.fromisoformat(json['fromTs']),
        to_dt=datetime.fromisoformat(json['toTs']),
        price=Decimal(json['price']),
        suboptimal_price_multiplier=Decimal(json['suboptimalPriceMultiplier']),
    )
