"""
ASP-Core-2 Parser Implementation in Python
Using PLY (Python Lex-Yacc)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Union


# =============================================================================
# AST NODE CLASSES
# =============================================================================

@dataclass
class Term:
    """Represents a term in ASP"""
    pass


@dataclass
class Constant(Term):
    """Constant term"""
    value: str

    def __str__(self):
        return self.value


@dataclass
class Variable(Term):
    """Variable term"""
    name: str

    def __str__(self):
        return self.name


@dataclass
class Number(Term):
    """Numeric term"""
    value: Union[int, float]

    def __str__(self):
        return str(self.value)


@dataclass
class AnonymousVariable(Term):
    """Anonymous variable (_)"""

    def __str__(self):
        return "_"


@dataclass
class FunctionTerm(Term):
    """Function term"""
    functor: str
    args: List[Term] = field(default_factory=list)

    def __str__(self):
        if not self.args:
            return self.functor
        return f"{self.functor}({','.join(str(a) for a in self.args)})"


@dataclass
class ArithmeticTerm(Term):
    """Arithmetic expression"""
    operator: str
    left: Term
    right: Term

    def __str__(self):
        return f"({self.left}{self.operator}{self.right})"


@dataclass
class RangeTerm(Term):
    """Range term (e.g., 1..10)"""
    start: str
    end: str

    def __str__(self):
        return f"{self.start}..{self.end}"


@dataclass
class NegatedTerm(Term):
    """Negated term"""
    term: Term

    def __str__(self):
        return f"-{self.term}"


@dataclass
class Atom:
    """Represents an atom"""
    predicate: str
    terms: List[Term] = field(default_factory=list)
    negated: bool = False  # Classical negation (-)

    def __str__(self):
        neg = "-" if self.negated else ""
        if not self.terms:
            return f"{neg}{self.predicate}"
        terms_str = ",".join(str(t) for t in self.terms)
        return f"{neg}{self.predicate}({terms_str})"

    def get_predicate(self):
        """Get predicate name"""
        return self.predicate

    def get_terms(self):
        """Get list of terms"""
        return self.terms

    def get_arity(self):
        """Get arity (number of terms)"""
        return len(self.terms)

    def is_negated(self):
        """Check if classically negated"""
        return self.negated


@dataclass
class Literal:
    """Represents a literal (atom with possible NAF)"""
    atom: Atom
    naf: bool = False  # Default negation (not)

    def __str__(self):
        naf = "not " if self.naf else ""
        return f"{naf}{self.atom}"

    def get_atom(self):
        """Get the atom"""
        return self.atom

    def is_naf(self):
        """Check if negated by default negation"""
        return self.naf

    def get_predicate(self):
        """Get predicate name"""
        return self.atom.predicate

    def get_terms(self):
        """Get terms"""
        return self.atom.terms


@dataclass
class BuiltinAtom:
    """Represents a builtin atom (comparison)"""
    left: Term
    operator: str
    right: Term

    def __str__(self):
        return f"{self.left} {self.operator} {self.right}"


@dataclass
class Rule:
    """Represents a rule"""
    head: List[Atom] = field(default_factory=list)
    body: List[Union[Literal, BuiltinAtom]] = field(default_factory=list)
    rule_type: str = "rule"  # "rule", "constraint", "weak_constraint", "fact"

    def __str__(self):
        if self.rule_type == "constraint":
            body_str = ", ".join(str(l) for l in self.body)
            return f":- {body_str}."

        head_str = " | ".join(str(a) for a in self.head) if self.head else ""

        if not self.body:
            return f"{head_str}."

        body_str = ", ".join(str(l) for l in self.body)
        return f"{head_str} :- {body_str}."

    def get_head(self):
        """Get head atoms"""
        return self.head

    def get_body(self):
        """Get body literals"""
        return self.body

    def get_head_atoms(self):
        """Get head atoms (alias for get_head)"""
        return self.head

    def get_body_literals(self):
        """Get body literals (alias for get_body)"""
        return self.body

    def is_fact(self):
        """Check if rule is a fact"""
        return len(self.body) == 0 and len(self.head) > 0

    def is_constraint(self):
        """Check if rule is a constraint"""
        return self.rule_type == "constraint"

    def is_weak_constraint(self):
        """Check if rule is a weak constraint"""
        return self.rule_type == "weak_constraint"

    def get_head_predicates(self):
        """Get list of head predicate names"""
        return [atom.predicate for atom in self.head]

    def get_body_predicates(self):
        """Get list of body predicate names"""
        predicates = []
        for lit in self.body:
            if isinstance(lit, Literal):
                predicates.append(lit.atom.predicate)
        return predicates

    def get_all_predicates(self):
        """Get all predicates (head and body)"""
        return self.get_head_predicates() + self.get_body_predicates()

    def get_all_atoms(self):
        """Get all atoms (head and body)"""
        atoms = list(self.head)
        for lit in self.body:
            if isinstance(lit, Literal):
                atoms.append(lit.atom)
        return atoms

    def get_variables(self):
        """Get all variables in the rule"""
        variables = set()

        def extract_vars(term):
            if isinstance(term, Variable):
                variables.add(term.name)
            elif isinstance(term, FunctionTerm):
                for arg in term.args:
                    extract_vars(arg)
            elif isinstance(term, (ArithmeticTerm, NegatedTerm)):
                if hasattr(term, 'left'):
                    extract_vars(term.left)
                if hasattr(term, 'right'):
                    extract_vars(term.right)
                if hasattr(term, 'term'):
                    extract_vars(term.term)

        for atom in self.head:
            for term in atom.terms:
                extract_vars(term)

        for lit in self.body:
            if isinstance(lit, Literal):
                for term in lit.atom.terms:
                    extract_vars(term)
            elif isinstance(lit, BuiltinAtom):
                extract_vars(lit.left)
                extract_vars(lit.right)

        return list(variables)

    def get_constants(self):
        """Get all constants in the rule"""
        constants = set()

        def extract_constants(term):
            if isinstance(term, Constant):
                constants.add(term.value)
            elif isinstance(term, FunctionTerm):
                for arg in term.args:
                    extract_constants(arg)
            elif isinstance(term, (ArithmeticTerm, NegatedTerm)):
                if hasattr(term, 'left'):
                    extract_constants(term.left)
                if hasattr(term, 'right'):
                    extract_constants(term.right)
                if hasattr(term, 'term'):
                    extract_constants(term.term)

        for atom in self.head:
            for term in atom.terms:
                extract_constants(term)

        for lit in self.body:
            if isinstance(lit, Literal):
                for term in lit.atom.terms:
                    extract_constants(term)
            elif isinstance(lit, BuiltinAtom):
                extract_constants(lit.left)
                extract_constants(lit.right)

        return list(constants)


@dataclass
class Query:
    """Represents a query"""
    atom: Atom

    def __str__(self):
        return f"{self.atom}?"

    def get_atom(self):
        """Get the query atom"""
        return self.atom

    def get_predicate(self):
        """Get predicate name"""
        return self.atom.predicate

    def get_terms(self):
        """Get terms"""
        return self.atom.terms


@dataclass
class Directive:
    """Represents a directive"""
    name: str
    value: str

    def __str__(self):
        return f"{self.name} {self.value}"


@dataclass
class Program:
    """Represents an ASP program"""
    rules: List[Rule] = field(default_factory=list)
    queries: List[Query] = field(default_factory=list)
    directives: List[Directive] = field(default_factory=list)

    def __str__(self):
        lines = []
        for rule in self.rules:
            lines.append(str(rule))
        for query in self.queries:
            lines.append(str(query))
        for directive in self.directives:
            lines.append(str(directive))
        return "\n".join(lines)

    def get_rules(self):
        """Get all rules"""
        return self.rules

    def get_facts(self):
        """Get all facts"""
        return [r for r in self.rules if r.is_fact()]

    def get_constraints(self):
        """Get all constraints"""
        return [r for r in self.rules if r.is_constraint()]

    def get_queries(self):
        """Get all queries"""
        return self.queries

    def get_directives(self):
        """Get all directives"""
        return self.directives

    def get_predicates(self):
        """Get all predicates in the program"""
        predicates = set()
        for rule in self.rules:
            predicates.update(rule.get_all_predicates())
        return list(predicates)

    def get_rules_by_predicate(self, predicate):
        """Get all rules that have the predicate in head"""
        return [r for r in self.rules if predicate in r.get_head_predicates()]

    def get_atoms(self):
        """Get all atoms in the program"""
        atoms = []
        for rule in self.rules:
            atoms.extend(rule.get_all_atoms())
        return atoms