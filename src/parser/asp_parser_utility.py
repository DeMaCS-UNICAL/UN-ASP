from .asp_parser import ASPParser
from .asp_nodes import Literal, BuiltinAtom


def extract_head_and_body(rule_str):
    """Extracts head and body atoms from an ASP rule."""
    parser = ASPParser()
    parser.build()
    program = parser.parse(rule_str)

    head_atoms = []
    body_atoms = []

    for rule in program.rules:
        # Extract head atoms
        for atom in rule.head:
            head_atoms.append(str(atom))

        # Extract body literals
        for item in rule.body:
            if isinstance(item, Literal):
                sign = "not " if item.naf else ""
                body_atoms.append(sign + str(item.atom))
            if isinstance(item, BuiltinAtom):
                body_atoms.append(str(item))

    return head_atoms, body_atoms


def extract_predicate_info(rule_line: str):
    """Extract predicate information from an ASP rule."""
    parser = ASPParser()
    parser.build()
    program = parser.parse(rule_line)

    predicates = {}  # dict[str, list[tuple[int, str]]]

    for rule in program.rules:
        # Process head atoms
        for atom in rule.head:
            pred = atom.predicate
            arity = atom.get_arity()
            atom_str = str(atom)

            if pred not in predicates:
                predicates[pred] = []

            predicates[pred].append((arity, atom_str))

        # Process body literals
        for item in rule.body:
            if isinstance(item, Literal):
                atom = item.atom
                pred = atom.predicate
                arity = atom.get_arity()

                # Include NAF in the string representation if present
                atom_str = str(item)

                if pred not in predicates:
                    predicates[pred] = []

                predicates[pred].append((arity, atom_str))

    return predicates