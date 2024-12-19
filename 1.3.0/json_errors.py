"""
python 1.3.0/json_errors.py
"""
import json

from neo4j_graphrag.experimental.components.entity_relation_extractor import fix_invalid_json

WRONG_JSONS = [
    # missing closing bracket
    '["a", "b"',
    '{"a": []',
    '{"a": [}',
    '{"a": [{"type": "XX", "properties": {}} }',
    '{"a": [{"type": "XX", "properties": {} ]}',
    # all closing brackets at the end
    '{"a": [{"type": "XX", {"type": "YY, {"type": "ZZ ]} }}}',
    # trailing comma
    '{"a": [],}',
    # missing value
    '{"a": {"type"}}',
    # missing quote
    '{"a": {"type: "b"}}'
]

not_fixed = 0

for wrong_json in WRONG_JSONS:
    fixed_json = fix_invalid_json(wrong_json)
    try:
        json.loads(fixed_json)
        print(wrong_json, fixed_json)
    except json.JSONDecodeError:
        not_fixed += 1

print("#" * 50)
print(len(WRONG_JSONS), " to fix")
print(not_fixed, " not fixed")
print("#" * 50)
