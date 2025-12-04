from django.shortcuts import render
from amadeus import Client, ResponseError
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from .models import Booking

# Inisialisasi Amadeus
amadeus = Client(
    client_id='vFbN077c0hBphSN9h9ngVdD9vdUQ6A7N',
    client_secret='eyaupfdWxITm13vq'
)

def home(request):
    return render(request, 'home.html')

def search_flight(request):
    return render(request, 'search.html')

def flight_result(request):
    
    def clean_iata(text):
        if text and '(' in text and ')' in text:
            return text.split('(')[-1].replace(')', '').strip()
        return text 

    raw_origin = request.GET.get('origin')
    raw_destination = request.GET.get('destination')
    departure_date = request.GET.get('departure_date')
    return_date = request.GET.get('return_date')
    
    origin_code = clean_iata(raw_origin).upper()
    destination_code = clean_iata(raw_destination).upper()

    if not origin_code or not destination_code or not departure_date:
        return render(request, 'search.html', {'error': 'Mohon isi semua data penerbangan.'})

    try:
        kwargs = {
            'originLocationCode': origin_code,     
            'destinationLocationCode': destination_code, 
            'departureDate': departure_date,
            'adults': 1,
            'max': 10 
        }

        if return_date:
            kwargs['returnDate'] = return_date

        response = amadeus.shopping.flight_offers_search.get(**kwargs)
        flights = response.data
        
        parsed_flights = []
        for flight in flights:
            price_total = float(flight['price']['total'])
            price_idr = price_total * 16000 

            for itinerary in flight['itineraries']:
                for segment in itinerary['segments']:
                    if isinstance(segment['departure']['at'], str):
                        segment['departure']['at'] = parse_datetime(segment['departure']['at'])
                    if isinstance(segment['arrival']['at'], str):
                        segment['arrival']['at'] = parse_datetime(segment['arrival']['at'])

            offer = {
                'id': flight['id'],
                'airline': flight['validatingAirlineCodes'][0],
                'price': flight['price']['total'],
                'currency': flight['price']['currency'],
                'price_idr': int(price_idr),
                'itineraries': flight['itineraries'], 
                'full_data': flight
            }
            parsed_flights.append(offer)

        return render(request, 'result.html', {'flights': parsed_flights})

    except ResponseError as error:
        print(f"Error Amadeus: {error}")
        return render(request, 'search.html', {'error': 'Penerbangan tidak ditemukan. Coba ganti rute atau tanggal.'})

def flight_booking(request):
    
    if request.method == 'POST':
        name = request.POST.get('name')
        passport = request.POST.get('passport')
        
        
        origin = request.GET.get('origin', 'Unknown')
        destination = request.GET.get('destination', 'Unknown')
        airline = request.GET.get('airline', 'Unknown')
        price_str = request.GET.get('price_idr', '0').replace(',','').replace('.','')
        
       
        try:
            Booking.objects.create(
                passenger_name=name,
                passport_number=passport,
                origin=origin,
                destination=destination,
                airline=airline,
                price=int(price_str)
            )
            print("Data berhasil disimpan ke database!")
        except Exception as e:
            print(f"Gagal simpan database: {e}")

        
        context = {'name': name, 'passport': passport, 'success': True}
        return render(request, 'booking.html', context)

    airline = request.GET.get('airline')
    price_idr = request.GET.get('price_idr')
    origin = request.GET.get('origin')
    destination = request.GET.get('destination')
    duration = request.GET.get('duration')
    
    departure_str = request.GET.get('departure_time')
    arrival_str = request.GET.get('arrival_time')
    
    departure_time = parse_datetime(departure_str) if departure_str else None
    arrival_time = parse_datetime(arrival_str) if arrival_str else None

    # Data Pulang
    return_origin = request.GET.get('return_origin')
    return_destination = request.GET.get('return_destination')
    return_duration = request.GET.get('return_duration')
    return_dep_str = request.GET.get('return_departure_time')
    return_arr_str = request.GET.get('return_arrival_time')
    return_departure_time = parse_datetime(return_dep_str) if return_dep_str else None
    return_arrival_time = parse_datetime(return_arr_str) if return_arr_str else None

    is_round_trip = return_departure_time is not None

    context = {
        'airline': airline,
        'price_idr': price_idr,
        'origin': origin,
        'destination': destination,
        'duration': duration,
        'departure_time': departure_time,
        'arrival_time': arrival_time,
        'is_round_trip': is_round_trip,
        'return_origin': return_origin,
        'return_destination': return_destination,
        'return_duration': return_duration,
        'return_departure_time': return_departure_time,
        'return_arrival_time': return_arrival_time,
    }
    return render(request, 'booking.html', context)

def city_search(request):
    term = request.GET.get('term', '').lower()
    if not term:
        return JsonResponse([], safe=False)
    
    results = []
    try:
        response = amadeus.reference_data.locations.get(
            keyword=term,
            subType='AIRPORT,CITY'
        )
        for location in response.data:
            iata = location['iataCode']
            if not any(d['value'] == iata for d in results):
                label = f"{location['address']['cityName']} - {location['name']} ({iata})"
                results.append({'label': label, 'value': iata})
    except Exception:
        pass 

    return JsonResponse(results, safe=False)