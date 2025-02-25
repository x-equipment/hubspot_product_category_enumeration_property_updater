# HubSpot Product Category Enumeration Property Updater

[![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)](https://github.com/x-equipment/hubspot_product_category_enumeration_property_updater/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python->=3.6-blueviolet?style=flat-square)]()
[![Maintained](https://img.shields.io/badge/Maintained-Yes-green?style=flat-square)]()
[![Contributions](https://img.shields.io/badge/Contributions_welcome-Yes-blueviolet?style=flat-square)]()

This Python script automates the process of synchronizing product categories between a custom object in HubSpot and an enumeration property on the Products object. This ensures that your product category enumeration property always reflects the latest categories defined in your custom object.

## Features

-   **Automatic Synchronization:** Keeps the product category enumeration property up-to-date with the custom object.
-   **HubSpot Custom Code and Bash Compatibility:** Can be executed both as a HubSpot Custom Code action and directly from the command line (Bash).
-   **Pagination Handling:** Efficiently handles large numbers of product categories using HubSpot's pagination.
-   **Error Handling:** Includes robust error handling and logging.

## Prerequisites

-   A HubSpot account with a custom object representing product categories.
-   A HubSpot private app with the following scopes:
    -   `crm.objects.custom.read`
    -   `crm.schemas.properties.read`
    -   `e-commerce`
-   Python 3.6 or later.

## Installation

1.  **Clone the Repository:**

    ```bash
    git clone [https://github.com/x-equipment/hubspot_product_category_enumeration_property_updater.git](https://github.com/x-equipment/hubspot_product_category_enumeration_property_updater.git)
    cd hubspot_product_category_enumeration_property_updater
    ```

2.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set HubSpot API Key:**

    -   **For Bash Execution:** Set the `HUBSPOT_ACCESS_TOKEN` environment variable:

        ```bash
        export HUBSPOT_ACCESS_TOKEN="your_hubspot_api_key"
        ```

    -   **For HubSpot Custom Code:** Add the `HUBSPOT_ACCESS_TOKEN` secret to your Custom Code action in HubSpot.

## Usage

### HubSpot Custom Code

1.  In your HubSpot workflow, create a "Custom Code" action.
2.  Copy and paste the contents of `update_product_category_enum.py` into the code editor.
3.  In the "Secrets" section, add a secret named `HUBSPOT_ACCESS_TOKEN` and paste your HubSpot API key as the value.
4.  Test and publish the workflow.

### Bash Execution

1.  Set the `HUBSPOT_ACCESS_TOKEN` environment variable as described in the "Installation" section.
2.  Run the script from your terminal:

    ```bash
    python update_product_category_enum.py
    ```

## Configuration

-   **Constants:** The script uses the following constants, which you can modify within the script:
    -   `PRODUCT_OBJECT_TYPE`: The object type for Products (default: `"products"`).
    -   `ENUMERATION_PROPERTY_NAME`: The name of the enumeration property (default: `"product_category"`).
    -   `PRODUCT_CATEGORY_OBJECT_NAME`: The name of your custom object (default: `"product_categories"`).
    -   `PRODUCT_CATEGORY_PROPERTY_ID`: The internal name of the property containing the category IDs (default: `"product_category_id"`).
    -   `PRODUCT_CATEGORY_PROPERTY_NAME`: The internal name of the property containing the category names (default: `"product_category"`).

## Error Handling

The script logs errors to the console (for Bash) or to the HubSpot execution logs (for Custom Code). Check these logs for any issues.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the Apache 2.0 License.
