from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from django.shortcuts import render
from django.utils import timezone

import requests

from web.models import House


base_url = 'http://optimal-power-time-calculator:80'
def index(request):

    response1 = requests.get(f'{base_url}/api/next-optimal-hour?numHoursToForecast=3h35m')
    price1 = json_to_optimal_time_appliance("Test", response1.json()['price'])

    response = requests.get(f'{base_url}/api/next-optimal-hour?numHoursToForecast=1h35m')
    price = json_to_optimal_time_appliance("Test", response.json()['price'])

    return render(request, 'index.html', {'optimal_times': [price, price1]})


def optimal_power_for_house(request, house_id):
    house = House.objects.get(pk=house_id)

    appliances = defaultdict(list)
    for appliance in house.appliance_set.all():
        for program in appliance.program_set.all():
            hours_and_minutes = f'{program.time_in_minutes // 60}h{program.time_in_minutes % 60}m'
            print(hours_and_minutes)
            response = requests.get(f'{base_url}/api/next-optimal-hour?numHoursToForecast={hours_and_minutes}')
            print(response.json())

            optimal_time = json_to_optimal_time_appliance(program.name, response.json()['price'])
            appliances[appliance.name].append(optimal_time)

    appliances.default_factory = None
    for appliance, programs in appliances.items():
        print(appliance)
        for program in programs:
            print(program.program_name)
    return render(request, 'index.html', {'appliances': appliances})

@dataclass
class OptimalTimeAppliance:
    program_name: str
    from_datetime: datetime
    to_datetime: datetime
    price: Decimal
    suboptimal_price_multiplier: Decimal

    @property
    def hours_to_start(self):
        return (self.from_datetime - timezone.now()).seconds / 3600

def json_to_optimal_time_appliance(program_name, json):
    print(json['fromTs'])
    return OptimalTimeAppliance(
        program_name=program_name,
        from_datetime=datetime.fromisoformat(json['fromTs']),
        to_datetime=datetime.fromisoformat(json['toTs']),
        price=Decimal(json['price']),
        suboptimal_price_multiplier=Decimal(json['suboptimalPriceMultiplier']),
    )
