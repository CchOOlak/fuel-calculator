# Fuel Calculator

This project is a Django-based API that calculates the optimal fuel stops along a route within the USA. The API takes inputs of start and finish locations, returns a map of the route, and provides the optimal locations to fuel up based on fuel prices. The vehicle is assumed to have a maximum range of 500 miles and achieves 10 miles per gallon.

## Features

- Geocodes start and finish addresses
- Calculates the route and total distance
- Finds the most cost-effective fuel stops along the route
- Returns the total money spent on fuel
- Visualizes the route and fuel stops on a map

## Requirements

- Django 3.2.23
- requests
- geopy
- rdp

## Environments

- ORS_API_KEY
- USER_AGENT

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/fuel-calculator.git
    cd fuel-calculator
    ```

2. Create and activate a virtual environment:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

4. Apply migrations:

    ```sh
    python manage.py migrate
    ```

5. Import fuel price data:

    ```sh
    python manage.py import_fuel_data data/fuel-prices-for-be-assessment.csv
    ```

6. Geocode fuel stops:

    ```sh
    python manage.py geocode_fuel_data
    ```

## Usage

1. Start the Django development server:

    ```sh
    python manage.py runserver
    ```

2. Access the API endpoint to optimize the route:

    ```
    http://localhost:8000/api/optimize-route/?start=New+York,NY&finish=Chicago,IL
    ```

3. Access the map visualization:

    ```
    http://localhost:8000/map/
    ```
