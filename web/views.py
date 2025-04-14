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
    houses = House.objects.all()
    return render(request, 'web/index.html', {'houses': houses})


def optimal_power_for_house(request, house_id):
    house = House.objects.get(pk=house_id)
    appliances = defaultdict(list)
    error_message = None

    try:
        for appliance in house.appliance_set.all():
            for program in appliance.program_set.all():
                hours_and_minutes = f'{program.time_in_minutes // 60}h{program.time_in_minutes % 60}m'
                response = requests.get(f'{base_url}/api/next-optimal-hour?numHoursToForecast={hours_and_minutes}&glnNumber={house.gln_number}')
                try:
                    response.raise_for_status()
                    optimal_time = json_to_optimal_time_appliance(program.name, response.json()['price'])
                    appliances[appliance.name].append(optimal_time)
                except requests.exceptions.HTTPError as e:
                    error_message = f"API Error: {e.response.text}"
                    break
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"

    appliances.default_factory = None
    return render(request, 'web/house.html', {
        'appliances': appliances,
        'error_message': error_message
    })

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
    return OptimalTimeAppliance(
        program_name=program_name,
        from_datetime=datetime.fromisoformat(json['fromTs']),
        to_datetime=datetime.fromisoformat(json['toTs']),
        price=Decimal(json['price']),
        suboptimal_price_multiplier=Decimal(json['suboptimalPriceMultiplier']),
    )
