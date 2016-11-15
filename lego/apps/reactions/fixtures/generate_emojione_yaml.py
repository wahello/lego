import json

import yaml

data = json.load(open('emojione.json'))

possible = set()

fixture_fields = []

for key, emoji in data.items():
    fixture_fields.append(dict(
        model="reactions.ReactionType",
        fields=dict(
            short_code=emoji['shortname'].replace(':', ''),
            unicode=emoji['unicode']
        )
    ))
    possible = possible.union(set(data[key].keys()))

with open('emojione_reaction_types.yaml', 'w') as outfile:
    yaml.dump(fixture_fields, outfile, default_flow_style=False)
