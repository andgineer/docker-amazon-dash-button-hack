# Amazon Dash Dashboard Configuration
---

## Structure

    ```json
      "dashboards": [
        "dashboard1" " {
          "summary": [...],
          "actions": [...]  
        },
        ...
      ]
    ```

- **Type**: Object
- **Description**: Contains configurations for different dashboards. 
Each dashboard has its own properties, such as `summary`, `empty_image`, and `absent`.

    - `summary`: A textual description or title for the dashboard.
    - `empty_image`: The image displayed when no specific condition is met or data is empty.
    - `absent`: An array of objects specifying different reasons for being absent, and their associated images for grid and plot views.

**Example**:

```json
    "dashboards": {
        "anna_work_out": {
          "summary": "Anna work-out",
          "empty_image": "old-woman.png",
          "absent": [
            {
              "summary": "Sick",
              "image_grid": "absent_ill_grid.png",
              "image_plot": "absent_ill_plot.png"
            }
          ]
        }
    }
```
