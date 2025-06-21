# Integración CHJ SAIH para Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/integration) <!-- Asumiendo que será un repositorio por defecto de HACS -->

La integración CHJ SAIH te permite monitorizar datos hidrológicos de la red SAIH (Sistema Automático de Información Hidrológica) de la Confederación Hidrográfica del Júcar (CHJ) directamente en Home Assistant.

## Características

*   Obtiene datos de sensores en tiempo real desde los puntos de monitorización (variables) especificados del SAIH CHJ.
*   Expone los datos como entidades de sensor en Home Assistant.
*   Intervalo de actualización configurable.
*   (Más características se añadirán a medida que se desarrollen)

## Prerrequisitos

*   Instalación de Home Assistant.
*   [HACS (Home Assistant Community Store)](https://hacs.xyz/) instalado y operativo.

## Instalación

### Vía HACS (Recomendado)

1.  Asegúrate de que HACS esté instalado.
2.  Ve a HACS > Integraciones.
3.  Haz clic en los 3 puntos en la esquina superior derecha y selecciona "Repositorios personalizados".
4.  Introduce `https://github.com/carlos-48/ha-chj-saih` (reemplaza con la URL de tu repositorio real si es diferente) en el campo "Repositorio".
5.  Selecciona "Integración" como categoría.
6.  Haz clic en "Añadir".
7.  Busca la integración "CHJ SAIH" en la tienda de HACS y haz clic en "Instalar".
8.  Reinicia Home Assistant.

### Instalación Manual

1.  Descarga la última versión desde la [Página de Releases](https://github.com/carlos-48/ha-chj-saih/releases) (reemplaza con la URL de tu repositorio real).
2.  Copia el directorio `custom_components/chj_saih` en tu directorio `custom_components` de Home Assistant.
3.  Reinicia Home Assistant.

## Configuración

Después de la instalación, la integración CHJ SAIH se puede configurar a través de la interfaz de usuario de Home Assistant:

1.  Ve a **Ajustes** > **Dispositivos y Servicios**.
2.  Haz clic en el botón **+ AÑADIR INTEGRACIÓN**.
3.  Busca "CHJ SAIH" y selecciónala.
4.  Sigue las instrucciones en pantalla:
    *   **IDs de Estación (separados por comas)**: Introduce los IDs de `variable` del sistema SAIH CHJ para los puntos de monitorización que deseas seguir. Normalmente puedes encontrar estos IDs explorando el sitio web público del SAIH CHJ. Cada ID representa una métrica específica (ej. nivel del río, caudal) en una ubicación específica.
    *   **Intervalo de Sondeo (segundos)**: (Opcional) Con qué frecuencia obtener nuevos datos. Por defecto es 1800 segundos (30 minutos).
5.  Haz clic en **Enviar**.

La integración intentará entonces conectarse al servicio SAIH CHJ y crear entidades de sensor para los IDs de estación configurados.

## Entidades

Esta integración crea principalmente entidades de tipo `sensor`. Cada ID de Estación (variable) configurado típicamente resultará en una entidad de sensor.

*   **Nombre del Sensor**: Derivado de la descripción proporcionada por la API del SAIH CHJ (ej., "Caudal rambla Gallinera").
*   **Estado**: El valor actual de la métrica monitorizada.
*   **Atributos**:
    *   `last_update`: Marca de tiempo de la última lectura.
    *   `station_id`: El ID de `variable` del SAIH CHJ.
    *   `station_name`: Nombre de la estación física, si está disponible en la API.
    *   `river_name`: Nombre del río, si está disponible en la API.
    *   Otros metadatos proporcionados por la API.

## Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas, informes de errores o quieres contribuir con código, por favor abre un "issue" o envía un "pull request" en el [repositorio de GitHub](https://github.com/carlos-48/ha-chj-saih).

## Licencia

Este proyecto está bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles (asumiendo que se añadirá una licencia MIT).
