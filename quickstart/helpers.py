from graphrag_sdk.helpers import *

def map_dict_to_cypher_properties(d: dict):
    cypher = "{"
    if isinstance(d, list):
        # Lists should be converted to a comma-separated string
        if len(d) == 0:
            return "{}"
        # If list contains dictionaries, extract the values
        if any(isinstance(item, dict) for item in d):
            values = []
            for item in d:
                if isinstance(item, dict):
                    values.extend(item.values())
                else:
                    values.append(item)
            d = values
        # Join all values with commas
        cypher += f"values: '{','.join(str(x) for x in d)}'"
        cypher += "}"
        return cypher
        
    for key, value in d.items():
        # Check value type
        if isinstance(value, str):
            # Find unescaped quotes
            value = value.replace('"', '\\"').replace("'", "\\'")
            value = f'"{value}"' if f"{value}" != "None" else '""'
        elif isinstance(value, dict):
            # For nested dictionaries, flatten them into dot notation
            for subkey, subvalue in value.items():
                if isinstance(subvalue, str):
                    subvalue = subvalue.replace('"', '\\"').replace("'", "\\'")
                    cypher += f'{key}_{subkey}: "{subvalue}", '
            continue
        else:
            value = str(value) if f"{value}" != "None" else '""'
        cypher += f"{key}: {value}, "
    
    cypher = (cypher[:-2] if len(cypher) > 1 else cypher) + "}"
    return cypher
