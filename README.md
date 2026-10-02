# LIFAair for Home Assistant

Custom Home Assistant integration for LIFAair air purifiers using the local Broadlink-based protocol.

## Supported

Tested with LIFAair LA333.

The integration provides:
- fan control
- fan modes: Auto, Night, Turbo, Anti-Allergy, Manual, Off
- manual fan speed
- temperature
- humidity
- CO2
- TVOC
- PM1
- PM2.5
- PM10

Communication is local over the network.

## Installation

Install through HACS as a custom repository:

1. Open HACS.
2. Open **Integrations**.
3. Open the three-dot menu and select **Custom repositories**.
4. Add this repository URL.
5. Select **Integration**.
6. Install **LIFAair**.
7. Restart Home Assistant.
8. Go to **Settings → Devices & services → Add Integration** and search for **LIFAair**.

Enter the IP address of the purifier.

## Notes

The LIFAair protocol implementation is based on the open-source LIFAair support proposed in python-broadlink PR #807 and has been adapted for a standalone Home Assistant integration.
