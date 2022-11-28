from dataclasses import dataclass
from datetime import datetime, date, timedelta
from logging import getLogger
from typing import Union, Tuple
from urllib.parse import urlencode

import numpy as np
import pandas as pd
import requests

from api.models import HourlyObservation

logger = getLogger(__name__)

OPEN_METEO_API_URL = "https://api.open-meteo.com/v1/forecast"


def extract(
    lat: float,
    lon: float,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    hourly_fields: Tuple[str] = ("temperature_2m", "apparent_temperature"),
    endpoint_url=OPEN_METEO_API_URL,
) -> pd.DataFrame:
    """Extracts hourly meteorological data from Open Meteo API for the selected coordinates and date."""
    start_date = start_date.date().isoformat()
    end_date = end_date.date().isoformat()
    query = urlencode(
        {
            "latitude": lat,
            "longitude": lon,
            "hourly": ",".join(hourly_fields),
            "start_date": start_date,
            "end_date": end_date,
        },
        safe=",",
    )
    url = f"{endpoint_url}?{query}"
    logger.info(f"Fetching data from Open Meteo API. URL: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(f"Error when fetching data from {url}: {response.text}")
    else:
        resp_data = response.json()
        logger.info(f"{len(resp_data.get('hourly', {}))} records fetched successfully!")
        return pd.DataFrame({"lat": lat, "lon": lon, **resp_data.get("hourly")})


def transform(
    df: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp, interpolate_missing: bool
) -> pd.DataFrame:
    """
    Calculates difference between real and apparent temperatures and daily maximum and minimum. In case of missing data
    either interpolates missing values or raises an error.
    """
    logger.info("Applying transforms to the data...")
    # Create continuous hourly date range index
    if end_date >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
        end_date = df["time"].max()
    else:
        end_date = end_date.replace(hour=23)
    time_index = pd.date_range(start_date, end_date, freq="H", tz="UTC").to_frame().drop(columns=0)
    time_index.index.name = "time"
    # Set dataframe index
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df.set_index("time", inplace=True)
    # Join on time index and, if data is missing, interpolate values or raise error
    df = time_index.join(df)
    if df.isnull().values.any():
        rows_with_nans = np.count_nonzero(df.isnull())
        if interpolate_missing:
            logger.warning(
                f"Data includes missing values for {rows_with_nans} out of {len(df)} timestamps. "
                f"The missing values will be interpolated from existing values."
            )
            df = df.interpolate()
        else:
            raise ValueError(f"Data is missing for {rows_with_nans} out of {len(df)} timestamps.")
    # Additional processing
    df["apparent_diff"] = (df["apparent_temperature"] - df["temperature_2m"]).round(decimals=2)
    df["daily_max"] = df["temperature_2m"].resample("D").transform("max")
    df["daily_min"] = df["temperature_2m"].resample("D").transform("min")
    df.reset_index(drop=False, inplace=True)
    return df


def store(df: pd.DataFrame):
    """Stores the data into the database."""
    logger.info(f"Storing {len(df)} rows into database...")
    for idx, row in df.iterrows():
        HourlyObservation.objects.update_or_create(
            lat=row["lat"], lon=row["lon"], time=row["time"], defaults=row.to_dict()
        )


@dataclass
class OpenMeteoLoader:
    """
    Loads hourly temperature data from Open Meteo API for the selected lat and lon coordinates within the selected date
    range (with last hour of end_date exclusive). If interpolate_missing is set to True, any missing values
    will be interpolated from available data. Otherwise, an error will be raised if missing data is found.
    """

    lat: float
    lon: float
    start_date: Union[datetime, date, str]
    end_date: Union[datetime, date, str]
    interpolate_missing: bool = False

    def run(self):
        start_date = pd.to_datetime(self.start_date)
        end_date = pd.to_datetime(self.end_date)
        data = extract(self.lat, self.lon, start_date, end_date)
        data = transform(data, start_date, end_date, self.interpolate_missing)
        store(data)
        logger.info(f"Pipeline finished successfully!")
