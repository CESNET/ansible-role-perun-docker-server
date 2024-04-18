#!/usr/bin/env python3
import os
import sys
import json

DIR = os.getenv('HOME') + "/perun_sync_json"
RESOURCE_ATTR_NAME = "urn:perun:resource:attribute-def:def:authorizationResourceId"
os.umask(0o022)


def update_json(data):
    for user_uuid, user_data in data["users"].items():
        allowed_resources_uuids = list(user_data.get("allowed_resources", {}).keys())
        for resource_uuid in allowed_resources_uuids:
            if resource_uuid in data["resources"]:
                data["resources"].setdefault(resource_uuid, {}).setdefault("members", {})
                data["resources"][resource_uuid]["members"][user_uuid] = user_data["attributes"]
        data["users"][user_uuid].pop("allowed_resources", None)

    # add the empty members block to empty resources
    for resource_uuid, resource_data in data["resources"].items():
        if "members" not in resource_data:
            data["resources"][resource_uuid]["members"] = {}

    return data


def remove_unmatched_files(data):
    all_resources_names = []
    for resource_uuid, resource_data in data["resources"].items():
        all_resources_names.append(resource_data["attributes"][RESOURCE_ATTR_NAME])

    for filename in os.listdir(DIR):
        if filename.endswith(".json") and filename.split(".json")[0] not in all_resources_names:
            filepath = os.path.join(DIR, filename)
            os.remove(filepath)


def replace_files(data):
    for resource_uuid, resource_data in data["resources"].items():
        resource_name = resource_data["attributes"][RESOURCE_ATTR_NAME]
        filepath = os.path.join(DIR, resource_name)
        with open(f"{filepath}.tmp", "w") as tmp_file:
            json.dump(resource_data, tmp_file, indent=4)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
        os.replace(f"{filepath}.tmp", f"{filepath}.json")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)

    # Load JSON from file
    file_path = sys.argv[1]

    with open(file_path, "r") as f:
        data = json.load(f)

    data = update_json(data)
    remove_unmatched_files(data)
    replace_files(data)
