# SDRAngel + AIS + MQTT

Stream AIS data captured with SDRAngel to MQTT

## SDR Angel

Configure SDR Angel to stream AIS packets in NMEA format using UDP:

- "Add RX device" and select your SDR device from list.
- Tune into `162.000 MHz`, this is the center frecuency between AIS 1 and AIS 2.
- Add `AIS` _channel_  to RX device, demodulator should be `+0,025,000 Hz` or `-0,025,000 Hz` in order to match one of the AIS frequencies.
- Change format to `NMEA`, check that address is `127.0.0.1` and port `9999`.
- Check `UDP` checkbox.

Demodulator is ready on SDRAngel for sdrangel-ais-mqtt to connect.

## sdrangel-ais-mqtt

Configure MQTT broker and topic.

Run script with `python3 sdrangel-ais-mqtt.py`:

```python
$ python3 sdrangel-ais-mqtt.py --mqtt-host test.mosquitto.org --mqtt-topic aispacketstopic
2025-06-16 20:56:20,133 - INFO - UDP socket bound to 127.0.0.1:9999 for node node-montevideo-1
2025-06-16 20:56:20,756 - INFO - Connected to MQTT broker at test.mosquitto.org:1883
2025-06-16 20:56:20,756 - INFO - Connected to AIS NMEA servers...
2025-06-16 20:56:22,599 - DEBUG - Received from node-montevideo-1: b'!AIVDM,1,1,,,1;Np@Rh000sw4;5d1UtMuGb`08=9,0*22\r\n'
2025-06-16 20:56:22,599 - DEBUG - Published: {"raw": "!AIVDM,1,1,,,1;Np@Rh000sw4;5d1UtMuGb`08=9,0*22", "node": "node-montevideo-1"}
2025-06-16 20:56:26,437 - DEBUG - Received from node-montevideo-1: b'!AIVDM,1,1,,,1;Np@RhP@0sw4;7d1UtMuGbf06sP,0*1f\r\n'
2025-06-16 20:56:26,437 - DEBUG - Published: {"raw": "!AIVDM,1,1,,,1;Np@RhP@0sw4;7d1UtMuGbf06sP,0*1f", "node": "node-montevideo-1"}
```

## MQTT

Message format is JSON with:

- `node`: Name of the SDRAngel service (host/port).
- `raw`: Raw AIS message in NMEA format. 

Use mosquitto MQTT client to check for messages:

```bash
$ mosquitto_sub -h localhost -t aispacketstopic

{"raw": "!AIVDM,1,1,,,1;Np@RhP@0sw4:ud1UteuGb`0H<w,0*64", "node": "node-montevideo-1"}
{"raw": "!AIVDM,1,1,,,1;Np@Rh001sw4:ud1UteuGbf0400,0*44", "node": "node-montevideo-1"}
{"raw": "!AIVDM,1,1,,,1;Np>lhP01sw46Ud1UTv2Ovl2D15,0*5c", "node": "node-montevideo-1"}
```

## AIS

Frequencies:

- 161.975 MHz (AIS 1)
- 162.025 MHz (AIS 2)

References:

- https://gpsd.gitlab.io/gpsd/AIVDM.html