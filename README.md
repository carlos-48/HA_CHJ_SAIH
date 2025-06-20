# CHJ SAIH Integration for Home Assistant

Integrates data from CHJ SAIH (Sistema Automático de Información Hidrológica de la Confederación Hidrográfica del Júcar) into Home Assistant.

## Features

*   Fetches data for hydrological observation stations.
*   Configurable via Home Assistant UI.
*   Two methods for selecting stations:
    *   Add a single, specific station by its ID.
    *   Add all stations of selected types within a specified radius from a central point.
*   Configurable update interval for fetching data.

## Requirements

*   Home Assistant
*   The `chj-saih` Python library (version 0.2.2 or as specified in `manifest.json`). This will be installed automatically by Home Assistant.

## Configuration

1.  Ensure you have the CHJ SAIH custom integration files in your `<config_dir>/custom_components/chj_saih/` directory.
2.  Restart Home Assistant.
3.  Go to **Settings > Devices & Services**.
4.  Click **+ ADD INTEGRATION** and search for "CHJ SAIH".
5.  The configuration flow will start.

### Configuration Steps

You will be asked to choose a configuration method:

**Option 1: Single Station**
*   Select "Single Station".
*   **Station ID**: Enter the unique identifier for the station you want to monitor.

**Option 2: Stations by Radius**
*   Select "Stations by Radius".
*   **Latitude**: The latitude of the center point for your search.
*   **Longitude**: The longitude of the center point for your search.
*   **Radius (km)**: The radius in kilometers around the central point to search for stations.
*   **Sensor Types**: Select one or more sensor types to include. Available types:
    *   RainGauge
    *   Flow
    *   Reservoir
    *   Temperature

**Global Settings**
After providing the station-specific configuration, you will be asked for:
*   **Scan Interval (seconds)**: How often to fetch new data from the CHJ SAIH service. Default is 1800 seconds (30 minutes).

## Provided Entities

Once configured, the integration will create sensor entities in Home Assistant for each selected/found station.

*   **Sensor Naming**: Sensors will typically be named based on the station ID or name provided by the API (e.g., "CHJ SAIH {station_id}" or "Station Name").
*   **State**: The primary state of the sensor will attempt to represent a key measurement or status (e.g., last update timestamp, "Online"). This is dependent on the data provided by the CHJ SAIH API for each station.
*   **Attributes**: Additional data fetched for the station will be available as attributes on the sensor. This can include:
    *   Station ID
    *   River name (if applicable)
    *   Last update timestamp from the source
    *   Specific measurements (e.g., flow rate, water level, temperature readings) depending on the station type and available data.

## Troubleshooting

*   If you encounter issues, check the Home Assistant logs (Settings > System > Logs) for messages from the `custom_components.chj_saih` logger.
*   Ensure the `chj-saih` library is installed correctly and is compatible.
*   Verify your network connection if data is not updating.

## Note on `chj-saih` Library

This integration relies on the `chj-saih` Python library to interact with the CHJ SAIH services. The functionality and data availability are dependent on this library. The assumed version is `chj-saih==0.2.2`, but this may be updated in `manifest.json`. The specific API calls used are `APIClient().get_stations_by_radius(...)` and `APIClient().get_station_data(...)`. The exact behavior and data returned by these calls will determine the final sensor characteristics.
