from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Mapping, Optional
from zoneinfo import ZoneInfo

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

import requests

from web.models import (
    House,
    Program,
)

base_url = 'http://optimal-power-time-calculator:80'


def index(request: HttpRequest) -> HttpResponse:
    houses = House.objects.all()
    return render(request, 'web/index.html', {'houses': houses})


def optimal_power_for_house(request: HttpRequest, house_id: int) -> HttpResponse:
    house = House.objects.get(pk=house_id)
    appliances = defaultdict(list)
    error_message = None
    latest_finish: Optional[str] = request.GET.get('latest_finish')

    try:
        for appliance in house.appliance_set.all():
            for program in appliance.program_set.all():
                hours_and_minutes = f'{program.time_in_minutes // 60}h{program.time_in_minutes % 60}m'
                params = {
                    'numHoursToForecast': hours_and_minutes,
                    'glnNumber': house.gln_number,
                }

                try:
                    error_message = populate_max_start_time(error_message, latest_finish, params, program)
                except ValueError as ve:
                    error_message = str(ve)
                    continue
                response = requests.get(f'{base_url}/api/next-optimal-hour', params=params)
                try:
                    response.raise_for_status()
                    optimal_time = json_to_optimal_time_appliance(program.name, response.json()['price'])
                    appliances[appliance.name].append(optimal_time)
                except requests.exceptions.HTTPError as e:
                    error_message = f"API Error: {e.response.text}"
                    continue
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"

    appliances.default_factory = None
    return render(request, 'web/house.html', {
        'appliances': appliances,
        'error_message': error_message
    })


def populate_max_start_time(
        error_message: str, latest_finish: str | None, params: dict[str, str], program: Program) -> str:
    if latest_finish:
        try:
            latest_finish_time = datetime.strptime(latest_finish, "%H:%M").time()
        except ValueError:
            error_message = f"Invalid latest_finish time format: {latest_finish}"
            raise ValueError(error_message)

        now = timezone.now().astimezone(ZoneInfo('Europe/Copenhagen'))
        # Build a datetime for "today" with latest_finish_time
        latest_finish_dt = now.replace(
            hour=latest_finish_time.hour,
            minute=latest_finish_time.minute,
            second=0, microsecond=0
        )
        duration = timedelta(minutes=program.time_in_minutes)
        max_start_time = latest_finish_dt - duration

        # If latest_finish already passed today, use tomorrow
        if max_start_time < now:
            max_start_time += timedelta(days=1)

        params['max_start_time'] = max_start_time.isoformat()
    return error_message


@dataclass
class OptimalTimeAppliance:
    program_name: str
    from_datetime: datetime
    to_datetime: datetime
    price: Decimal
    suboptimal_price_multiplier: Decimal

    @property
    def hours_to_start(self) -> float:
        return (self.from_datetime - timezone.now()).seconds / 3600


def json_to_optimal_time_appliance(
    program_name: str,
    json: Mapping[str, str],
) -> OptimalTimeAppliance:
    return OptimalTimeAppliance(
        program_name=program_name,
        from_datetime=datetime.fromisoformat(json['fromTs']),
        to_datetime=datetime.fromisoformat(json['toTs']),
        price=Decimal(json['price']),
        suboptimal_price_multiplier=Decimal(json['suboptimalPriceMultiplier']),
    )
