#! /usr/bin/env python3
from collections import OrderedDict

import graphql


ORIG_SCHEMA = """
    schema {
      query: RootQuery
    }
    type RootQuery {
      officers: [Officer]
    }

    type Officer {
      title: String
      first: String
      last: String
      uniform: Uniform
    }
    type Uniform {
      pips: Float
    }
"""

NEW_SCHEMA = """
    schema {
      query: RootQuery
    }
    type RootQuery {
      officers: [Officer]
      new_thing: String!
    }

    type Officer {
      title: String
      first: String
      last: String
      uniform: Uniform
    }
    type Uniform {
      pips: Float
    }
"""



def has_description(schema):
    import pdb; pdb.set_trace()


def sort_fields(fields):
    # Fields are two-tuples of name and field object. Sort on name.
    return OrderedDict(sorted(fields.items(), key=lambda f: f[0]))

def build_change_set(original, proposed):
    additions = []

    original = graphql.build_ast_schema(graphql.parse(original))
    proposed = graphql.build_ast_schema(graphql.parse(proposed))

    original_root = list(original.get_type_map().items())[0][1]
    proposed_root = list(proposed.get_type_map().items())[0][1]

    def _recurse_tree(original, proposed):
        new_keys = proposed.keys() - original.keys()

        for k in new_keys:
            additions.append(proposed[k])

            # remove the addition from the proposed schema because we're
            # already tracking them
            del proposed[k]

        # sort them to ensure we're comparing the same roots
        original_fields = sort_fields(original)
        proposed_fields = sort_fields(proposed)

        for o, p in zip(original_fields.values(), proposed_fields.values()):
            # ensure they're of the same type
            if type(o) != type(p):
                # TODO: call this out as an issue
                continue

            # can't recurse on scalars
            if not isinstance(o, graphql.GraphQLObjectType):
                continue

            _recurse_tree(
                _unwrap_type(o.type).fields,
                _unwrap_type(p.type).fields,
            )

    _recurse_tree(original_root.fields, proposed_root.fields)

    return additions


def _unwrap_type(_type):
    """Handle meta types like NonNull and Lists"""
    if isinstance(_type, graphql.GraphQLList):
        return _unwrap_type(_type.of_type)
    return _type


def analyze_additions(change_set):
    breakage = []
    for change in change_set:
        has_description(change)

def run():
    change_set = build_change_set(ORIG_SCHEMA, NEW_SCHEMA)
    analyze_additions(change_set)


if __name__ == '__main__':
    run()
