from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from django.shortcuts import render

import requests


def index(request):
    response = requests.get('http://optimal_power_time_calculator:80/api/next-optimal-hour?numHoursToForecast=3h35m')
    price = json_to_price("Test", response.json()['price'])
    print(price)
    return render(request, 'index.html', {'price': price})


@dataclass
class OptimalTimeAppliance:
    name: str
    from_dt: datetime
    to_dt: datetime
    price: Decimal
    suboptimal_price_multiplier: Decimal

def json_to_price(name, json_price):
    return OptimalTimeAppliance(
        name=name,
        from_dt=datetime.fromisoformat(json_price['fromTs']),
        to_dt=datetime.fromisoformat(json_price['toTs']),
        price=Decimal(json_price['price']),
        suboptimal_price_multiplier=Decimal(json_price['suboptimalPriceMultiplier']),
    )
