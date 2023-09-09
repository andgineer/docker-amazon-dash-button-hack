# Amazon Dash Actions Configuration

In the configuration file, actions are defined that dictate the response to different Amazon Dash button presses. 
Each button links to a set of specified actions and, optionally, a summarized purpose.

---

## Structure

    ```json
      "actions": [
        "button1" " {
          "summary": [...],
          "actions": [...]  
        },
        "button2" " {
          "summary": [...],
          "actions": [...]  
        },
        ...
      ]
    ```

Each button corresponds to a key within the `actions` dictionary. 
This key holds actions executed upon the button's press and can be detailed as follows:

- **Summary** (Optional): 
    - Describes the button's purpose. Useful for user feedback or logging.
    - Can vary depending on time (e.g., actions before 12:00:00).
    
- **Actions**:
    - A list of actions to perform.
    - Actions have a specific `type` which determines their behavior.
    - Each action type might require different parameters.

---

## Action Types and Their Parameters:

1. **sheet** - Logs button presses in a Google Sheet.
    ```json
    {
      "type": "sheet",
      "name": "amazon_dash",
      "press_sheet": "press",
      "event_sheet": "event",
      "restart": 15,
      "autoclose": 10800,
      "default": 900
    }
    ```

2. **calendar** - Creates an event in a Google Calendar.
    ```json
    {
      "type": "calendar",
      "calendar_id": "eo2n7ip8p1tm6dgseh3e7p19no@group.calendar.google.com",
      "dashboard": "anna_work_out",
      "restart": 15,
      "autoclose": 10800,
      "default": 900
    }
    ```

3. **ifttt** - Initiates an IFTTT applet.
    ```json
    {
      "type": "ifttt",
      "summary": "{button}_amazon_dash",
      "value1": "",
      "value2": "",
      "value3": ""
    }
    ```

4. **openhab** - Sends commands to an openHAB item.
    ```json
    {
      "type": "openhab",
      "path": "http://localhost:8080",
      "item": "{button}_amazon_dash",
      "command": "ON;OFF"
    }
    ```

---

## Example

    ```json
    {
      "actions": {
        "white": {
          "summary": [
            {
              "summary": "Morning work-out",
              "before": "12:00:00",
              "image": "morning.png"
            },
            {
              "summary": "Physiotherapy",
              "image": "evening2.png"
            }
          ],
          "actions": [
            {
              "type": "sheet",
              "name": "amazon_dash",
              "press_sheet": "press",
              "event_sheet": "event",
              "restart": 15,
              "autoclose": 10800,
              "default": 900
            },
            {
              "type": "calendar",
              "calendar_id": "eo2n7ip8p1tm6dgseh3e7p19no@group.calendar.google.com",
              "dashboard": "anna_work_out",
              "restart": 15,
              "autoclose": 10800,
              "default": 900
            },
            {
              "type": "ifttt",
              "summary": "white_amazon_dash",
              "value1": "",
              "value2": "",
              "value3": ""
            }
          ]
        }
      }
    }
    ```

### "white" button:

Upon pressing:

- **Before 12:00:00**: 
    - Recognized as **Morning work-out**.
    - Image used: `morning.png`.

- **After 12:00:00**: 
    - Labeled as **Physiotherapy**.
    - Image used: `evening2.png`.

The actions executed:

1. Logging in the "amazon_dash" Google Sheet.
2. Registering an event in a specific Google Calendar.
3. Triggering an IFTTT applet.

### Default Configuration

If a button isn't uniquely configured, the "__DEFAULT__" configuration activates. 
This offers a standard set of actions for any non-specific button.

    ```json
    {
      "actions": {
        ...
        "__DEFAULT__": {
          "summary": "{button}",
          "actions": [
            {
              "type": "sheet",
              "name": "amazon_dash",
              "press_sheet": "press",
              "event_sheet": "event",
              "restart": 60,
              "autoclose": 10800,
              "default": 900
            },
            {
              "type": "calendar",
              "calendar_id": "eo2n7ip8p1tm6dgseh3e7p19no@group.calendar.google.com",
              "restart": 15,
              "autoclose": 10800,
              "default": 900
            },
            {
              "type": "ifttt",
              "summary": "{button}_amazon_dash",
              "value1": "",
              "value2": "",
              "value3": ""
            },
            {
              "type": "openhab",
              "path": "http://localhost:8080",
              "item": "{button}_amazon_dash",
              "command": "ON;OFF"
            }
          ]
        }
      }
    }
    ```