# Home Assistant custom components
My own custom components for Home Assistant

## Askey RFT3505 Fiber Router (Spain) - Device Tracker
### Configuration variables:
**host**: The hostname or IP of your router.<br/>
**password**: The password of your router.<br/>

### Installation:
1. Download and unzip all the content from _askey_rft3505_ directory to your `/config/custom_components/askey_rft3505/` directory.
2. Add the configuration to the `configuration.yaml`:
```
    device_tracker:
      - platform: askey_rft3505
        host: ROUTER_IP
        password: YOUR_PASSWORD
        interval_seconds: 120
        consider_home: 200
        new_device_defaults:
          track_new_devices: False
          hide_if_away: False
```
3. Restart the Home Assistant server.