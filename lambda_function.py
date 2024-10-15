import json
import requests

def lambda_handler(event, context):
    # Cek apakah fungsi dipanggil via API Gateway dengan body atau queryStringParameters
    if 'body' in event:
        # Jika body ada, coba parse sebagai JSON jika itu string, atau gunakan langsung jika sudah dict
        try:
            request_data = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": "Invalid JSON in request body"
            }
        city = request_data.get('city')
    elif 'queryStringParameters' in event and event['queryStringParameters']:
        # Jika dipanggil dengan query string via GET
        city = event['queryStringParameters'].get('city')
    else:
        # Cek jika event langsung mengandung 'city' (kasus pemanggilan langsung via AWS SDK)
        city = event.get('city')

    # Jika kota tidak diberikan dalam semua kasus
    if not city:
        return {
            "statusCode": 400,
            "body": "City parameter is missing in the request"
        }
    
    # URL dari EC2 instance dengan faasd
    faasd_url = f"http://172.31.82.144:8080/function/weather"
    
    # Request ke service weather di EC2
    response = requests.post(faasd_url, json={"city": city})
    
    if response.status_code == 200:
        weather_data = response.json()
        temperature_celsius = float(weather_data['temperature'][:-2])
        
        # Convert from Celsius to Fahrenheit
        temperature_fahrenheit = (temperature_celsius * 9/5) + 32
        weather_data['temperature'] = f"{temperature_fahrenheit:.1f}ºF"
        
        # Return the final result
        return {
            "statusCode": 200,
            "body": json.dumps(weather_data)
        }
    else:
        return {
            "statusCode": response.status_code,
            "body": "Error fetching weather data"
        }
