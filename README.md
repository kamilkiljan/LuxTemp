# LuxTemp!

This project demonstrates how to implement a simple pipeline with a dedicated API endpoint for a weather app called **LuxTemp!**. It uses Django Rest Framework as the backend server with PostgreSQL as the database. Additionally, the `drf-spectacular` package provides the information about the schema following the Open API 3.0 specification. The project is dockerized to allow for better portability and easier setup and deployment.

__Note: The app configuration is not production safe! The `DEBUG = True` setting should be disabled and any secret keys changed and hidden before external deployment!__

## Setup

To run the application open a terminal window and run the command below:

    docker compose up

On the first run of the application, you need to apply the required migrations by executing the command below in a separate terminal window:

    docker compose run api python manage.py migrate

We should also create a user to be able to query the data (you need to set password when prompted):

    docker compose run api python manage.py createsuperuser --username admin --email example@example.com

## Loading the data

Once the migrations have been applied, you can run the loader fetching hourly temperature observations for selected coordinates and date range. If you need to load data for a specific location you need to find its latitude and longitude coordinates. For example, to load data for Luxembourg run:
   
    docker compose run api python manage.py run_open_meteo_loader --lat=49.61 --lon=6.13 --start_date=2022-11-01 --end_date=2022-11-07 --interpolate_missing

To load data for Esch-sur-Alzette run:

    docker compose run api python manage.py run_open_meteo_loader --lat=49.50 --lon=5.98 --start_date=2022-11-01 --end_date=2022-11-07 --interpolate_missing

The loader carries out additional processing on the fetched data and interpolates missing values.

## Querying the data

With the default configuration, the server listens for incoming requests at http://0.0.0.0:8000/ and uses basic authentication for the API endpoint - you should authorize with username `admin` and the password you chose during setup.

The app provides a browsable SwaggerUI schema documentation for the API available at http://127.0.0.1:8000/api/schema/swagger-ui/ with interactive authentication.

Alternatively, you can send plain HTTP requests to the API with:

    >>> import requests
    >>> response = requests.get('http://127.0.0.1:8000/hourly_observations/', auth=('admin', <password>))
    >>> response.json()
    {"count":48,"next":null,"previous":null,"results":[{"id":1,"lat":49.61,"lon":6.13,"time":"2022-11-26T00:00:00Z"...

Queries can use filters for date range and coordinates as URL query params and the results list is paginated.

## Next steps

With Django Rest Framework as its backbone the app is easily extendable and scalable. The schema can be changed and maintained with built-in migrations, new loaders added and more sophisticated querying or authentication methods enabled.