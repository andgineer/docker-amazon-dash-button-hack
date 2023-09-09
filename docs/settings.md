# Settings for the Amazon Dash button

## Root Keys

### `latitude` and `longitude`

- **Type**: String (decimal representation)
- **Description**: Specifies the geographical coordinates for the location of use. Essential for functionalities dependent on location-based triggers or conditions.

**Example**:

```json
"latitude": "60.002228",
"longitude": "30.296947"
```

### `credentials_file_name`

- **Type**: String (path)
- **Description**: The path to the credentials file that is necessary for accessing certain functionalities or APIs.

**Example**:

```json
"credentials_file_name": "../amazon-dash-private/amazon-dash-hack.json"
```

### `ifttt_key_file_name`

- **Type**: String (path)
- **Description**: The path to the IFTTT (If This Then That) service key file, which enables the integration with IFTTT services.

**Example**:

```json
"ifttt_key_file_name": "../amazon-dash-private/ifttt-key.json"
```

### `openweathermap_key_file_name`

- **Type**: String (path)
- **Description**: The path to the OpenWeatherMap API key file. This is essential if any functionality uses weather-related triggers or conditions.

**Example**:

```json
"openweathermap_key_file_name": "../amazon-dash-private/openweathermap-key.json"
```

### `images_folder`

- **Type**: String (path)
- **Description**: Path to the directory where the relevant images (icons, graphics) are stored.

**Example**:

```json
"images_folder": "../amazon-dash-private/images/"
```

### `chatter_delay`

- **Type**: Integer
- **Description**: The delay (in seconds) before the system will respond or react to a subsequent trigger. This can prevent rapid, repeated triggers from overloading the system.

**Example**:

```json
"chatter_delay": 5
```

### `dashboards`

[Dasboards settings](settings_dashboards.md)

### `actions`

[Actions settings](settings_actions.md)
