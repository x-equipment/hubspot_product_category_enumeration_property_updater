"""
HubSpot Enumeration Property Updater

This script retrieves product categories from a custom object in HubSpot and updates
a corresponding enumeration property on the Products object with these categories.
It allows syncing either a single category or all categories, and can remove non-existent categories.
"""

import os
import sys
import argparse

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
    access_token, object_type, category_name_property, category_id_property, category_id=None
):
    """Retrieves product categories and their IDs from the custom object, handling pagination."""
    try:
        client = hubspot.Client.create(access_token=access_token)

        filters = []
        if category_id:
            filters.append(hubspot.crm.objects.Filter(
                property_name=category_id_property,
                operator="EQ",
                value=category_id,
            ))
        else:
            filters.append(hubspot.crm.objects.Filter(
                property_name=category_name_property,
                operator="HAS_PROPERTY",
                value=None,
            ))

        filter_group = hubspot.crm.objects.FilterGroup(filters=filters)
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
                category_id_result = result.properties[category_id_property]
                categories[category_name] = str(category_id_result)

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
    access_token, object_type, property_name, enum_options, category_id=None
):
    """Updates the enumeration property with the provided options, including internal names."""
    try:
        client = hubspot.Client.create(access_token=access_token)

        property_definition = client.crm.properties.core_api.get_by_name(
            object_type=object_type, property_name=property_name
        )

        if category_id is None:  # update all
            updated_options = [
                {
                    "label": label,
                    "value": value,
                    "displayOrder": index,
                    "hidden": False,
                }
                for index, (label, value) in enumerate(enum_options.items())
            ]
            action = "all"
            message = f"Enumeration property '{property_name}' updated all."
        else:  # Update single category or remove if not found
            existing_options = property_definition.options
            existing_values = {option.value: option for option in existing_options}

            if not enum_options: # Category ID was not found, remove from enum.
                updated_options = [
                    option for option in existing_options if option.value != category_id
                ]
                action = "delete"
                message = f"Enumeration property '{property_name}' deleted category_id {category_id}."
            else:
                updated_options = []
                for label, value in enum_options.items():
                    if value in existing_values: #Update existing option
                        existing_option = existing_values[value]
                        updated_options.append({
                            "label": label,
                            "value": value,
                            "displayOrder": existing_option.display_order,
                            "hidden": existing_option.hidden,
                        })
                        action = "update"
                        message = f"Enumeration property '{property_name}' updated category_id {category_id}."
                        break # break the loop, since only one category is being updated.
                    else: #Add new option
                        updated_options.append({
                            "label": label,
                            "value": value,
                            "displayOrder": len(existing_options) + len(updated_options),
                            "hidden": False,
                        })
                        action = "create"
                        message = f"Enumeration property '{property_name}' created category_id {category_id}."
                        break # break the loop, since only one category is being updated.

                #Add all other existing options to the updated options.
                for option in existing_options:
                    if option.value not in enum_options.values():
                        updated_options.append(option)

        property_definition.options = updated_options

        client.crm.properties.core_api.update(
            object_type=object_type,
            property_name=property_name,
            property_update=property_definition,
        )
        print(f"Successfully updated enumeration property '{property_name}'.")
        return {"result": "success", "message": message, "category_id": category_id, "action": action}

    except ApiException as e:
        print(f"Exception when calling properties_api->update: {e}")
        return {"result": "error", "message": f"Exception: {e}", "category_id": category_id, "action": "error"}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"result": "error", "message": f"An error occurred: {e}", "category_id": category_id, "action": "error"}


def main(event=None):
    """Main function to be executed as HubSpot Custom Code or via Bash."""
    try:
        access_token = os.environ.get("HUBSPOT_ACCESS_TOKEN")

        if not access_token:
            raise ValueError("HUBSPOT_ACCESS_TOKEN environment variable not set.")

        product_category_object_type = get_object_type(
            access_token, PRODUCT_CATEGORY_OBJECT_NAME
        )

        # Get category_id from event or args
        category_id = None
        if event and event.get("inputFields") and event.get("inputFields").get("category_id"):
            category_id = event.get("inputFields").get("category_id")
        else:
            try:
                import argparse
                parser = argparse.ArgumentParser(description="Sync HubSpot product categories.")
                parser.add_argument("--category_id", type=str, help="Sync a specific category by ID.")
                args = parser.parse_args()
                if args.category_id:
                    category_id = args.category_id
            except ImportError:
                pass # argparse not available, likely running in hubspot.
            except SystemExit:
                pass # argparse finished, likely called from command line without args.

        if PRODUCT_OBJECT_TYPE and product_category_object_type:
            product_categories = get_product_categories(
                access_token,
                product_category_object_type,
                PRODUCT_CATEGORY_PROPERTY_NAME,
                PRODUCT_CATEGORY_PROPERTY_ID,
                category_id=category_id,
            )

            result = update_enumeration_property(
                access_token,
                PRODUCT_OBJECT_TYPE,
                ENUMERATION_PROPERTY_NAME,
                product_categories,
                category_id=category_id,
            )
            if result:
                if "hubspotHandler.py" in sys.argv[0]:
                    return result
                else:
                    print(result)
        else:
            print("Failed to retrieve object type IDs.")

    except Exception as e:
        print(f"An error occurred in main: {e}")
        if "hubspotHandler.py" in sys.argv[0]:
            return {"result": "error", "message": f"An error occurred in main: {e}"}
        else:
            print({"result": "error", "message": f"An error occurred in main: {e}"})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync HubSpot product categories.")
    parser.add_argument(
        "--category_id", type=str, help="Sync a specific category by ID."
    )
    args = parser.parse_args()

    if "hubspotHandler.py" in sys.argv[0]:
        main(event={})
    else:
        main()