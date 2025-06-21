# CHJ SAIH Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/integration) <!-- Assuming it will be a default HACS repo -->

The CHJ SAIH integration allows you to monitor hydrological data from the Júcar River Hydrographic Confederation (Confederación Hidrográfica del Júcar - CHJ) SAIH (Sistema Automático de Información Hidrológica) network directly in Home Assistant.

## Features

*   Fetches real-time sensor data from specified CHJ SAIH monitoring points (variables).
*   Exposes data as sensor entities in Home Assistant.
*   Configurable update interval.
*   (More features to be added as developed)

## Prerequisites

*   Home Assistant installation.
*   [HACS (Home Assistant Community Store)](https://hacs.xyz/) installed and operational.

## Installation

### Via HACS (Recommended)

1.  Ensure HACS is installed.
2.  Go to HACS > Integrations.
3.  Click on the 3 dots in the top right corner and select "Custom repositories".
4.  Enter `https://github.com/carlos-48/ha-chj-saih` (replace with your actual repository URL if different) in the "Repository" field.
5.  Select "Integration" as the category.
6.  Click "Add".
7.  Find the "CHJ SAIH" integration in the HACS store and click "Install".
8.  Restart Home Assistant.

### Manual Installation

1.  Download the latest release from the [Releases page](https://github.com/carlos-48/ha-chj-saih/releases) (replace with your actual repository URL).
2.  Copy the `custom_components/chj_saih` directory into your Home Assistant `custom_components` directory.
3.  Restart Home Assistant.

## Configuration

After installation, the CHJ SAIH integration can be configured through the Home Assistant user interface:

1.  Go to **Settings** > **Devices & Services**.
2.  Click the **+ ADD INTEGRATION** button.
3.  Search for "CHJ SAIH" and select it.
4.  Follow the on-screen instructions:
    *   **Station IDs (comma-separated)**: Enter the `variable` IDs from the CHJ SAIH system for the monitoring points you want to track. You can usually find these IDs by exploring the CHJ SAIH public website. Each ID represents a specific metric (e.g., river level, flow rate) at a specific location.
    *   **Scan Interval (seconds)**: (Optional) How often to fetch new data. Defaults to 1800 seconds (30 minutes).
5.  Click **Submit**.

The integration will then attempt to connect to the CHJ SAIH service and create sensor entities for the configured station IDs.

## Entities

This integration primarily creates `sensor` entities. Each configured Station ID (variable) will typically result in one sensor entity.

*   **Sensor Name**: Derived from the description provided by the CHJ SAIH API (e.g., "Caudal rambla Gallinera").
*   **State**: The current value of the monitored metric.
*   **Attributes**:
    *   `last_update`: Timestamp of the last reading.
    *   `station_id`: The CHJ SAIH `variable` ID.
    *   `station_name`: Name of the physical station, if available from the API.
    *   `river_name`: Name of the river, if available from the API.
    *   Other metadata provided by the API.

## Contributing

Contributions are welcome! If you have ideas, bug reports, or want to contribute code, please open an issue or submit a pull request on the [GitHub repository](https://github.com/carlos-48/ha-chj-saih).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (assuming an MIT license will be added).
