"""
HubSpot Enumeration Property Updater

This script retrieves product categories from a custom object in HubSpot and updates
a corresponding enumeration property on the Products object with these categories.
It ensures that the enumeration property has the same options as the custom object,
using internal names for the values.
"""

import os
import sys

import hubspot
from hubspot.crm.objects import ApiException as ObjectsApiException
from hubspot.crm.schemas import ApiException

# Constants for object types and property names.
PRODUCT_OBJECT_TYPE = "products"
ENUMERATION_PROPERTY_NAME = "product_category"
PRODUCT_CATEGORY_OBJECT_NAME = "product_categories"
PRODUCT_CATEGORY_PROPERTY_ID = "product_category_id"
PRODUCT_CATEGORY_PROPERTY_NAME = "product_category"


def get_object_type(access_token, object_name):
    """Retrieves the object type ID for a given object name."""
    try:
        client = hubspot.Client.create(access_token=access_token)
        api_response = client.crm.schemas.core_api.get_all()

        for obj_type in api_response.results:
            if obj_type.name == object_name:
                return obj_type.object_type_id

        print(f"Object type '{object_name}' not found.")
        return None

    except ApiException as e:
        print(f"Exception when calling object_types_api->get_all: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_product_categories(
    access_token, object_type, category_name_property, category_id_property
):
    """Retrieves product categories and their IDs from the custom object, handling pagination."""
    try:
        client = hubspot.Client.create(access_token=access_token)

        filter_obj = hubspot.crm.objects.Filter(
            property_name=category_name_property,
            operator="HAS_PROPERTY",
            value=None,
        )
        filter_group = hubspot.crm.objects.FilterGroup(filters=[filter_obj])
        search_request = hubspot.crm.objects.PublicObjectSearchRequest(
            filter_groups=[filter_group],
            properties=[category_name_property, category_id_property],
            limit=100,
            after=None,
        )

        categories = {}
        while True:
            api_response = client.crm.objects.search_api.do_search(
                object_type=object_type, public_object_search_request=search_request
            )

            for result in api_response.results:
                category_name = result.properties[category_name_property]
                category_id = result.properties[category_id_property]
                categories[category_name] = str(category_id)

            if not api_response.paging or not api_response.paging.next.after:
                break

            search_request.after = api_response.paging.next.after

        return categories

    except ObjectsApiException as e:
        print(f"Exception when calling objects_api->do_search: {e}")
        return {}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def update_enumeration_property(
    access_token, object_type, property_name, enum_options
):
    """Updates the enumeration property with the provided options, including internal names."""
    try:
        client = hubspot.Client.create(access_token=access_token)

        property_definition = client.crm.properties.core_api.get_by_name(
            object_type=object_type, property_name=property_name
        )

        updated_options = [
            {
                "label": label,
                "value": value,
                "displayOrder": index,
                "hidden": False,
            }
            for index, (label, value) in enumerate(enum_options.items())
        ]

        property_definition.options = updated_options

        client.crm.properties.core_api.update(
            object_type=object_type,
            property_name=property_name,
            property_update=property_definition,
        )
        print(f"Successfully updated enumeration property '{property_name}'.")

    except ApiException as e:
        print(f"Exception when calling properties_api->update: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main(event=None):
    """Main function to be executed as HubSpot Custom Code or via Bash."""
    try:
        access_token = os.environ.get("HUBSPOT_ACCESS_TOKEN")

        if not access_token:
            raise ValueError("HUBSPOT_ACCESS_TOKEN environment variable not set.")

        product_category_object_type = get_object_type(
            access_token, PRODUCT_CATEGORY_OBJECT_NAME
        )

        if PRODUCT_OBJECT_TYPE and product_category_object_type:
            product_categories = get_product_categories(
                access_token,
                product_category_object_type,
                PRODUCT_CATEGORY_PROPERTY_NAME,
                PRODUCT_CATEGORY_PROPERTY_ID,
            )
            if product_categories:
                update_enumeration_property(
                    access_token,
                    PRODUCT_OBJECT_TYPE,
                    ENUMERATION_PROPERTY_NAME,
                    product_categories,
                )
        else:
            print("Failed to retrieve object type IDs.")

    except Exception as e:
        print(f"An error occurred in main: {e}")


if __name__ == "__main__":
    if "hubspotHandler.py" in sys.argv[0]:
        main(event={})
    else:
        main()