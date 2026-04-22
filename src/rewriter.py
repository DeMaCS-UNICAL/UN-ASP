import os
import sys
from dataclasses import dataclass
from typing import Dict, Set, Tuple, Optional

from .parser.asp_parser import ASPParser
from .parser.asp_nodes import *
from src.parser.asp_nodes import Literal, BuiltinAtom


@dataclass
class UncertainPredicate:
    """Represents an uncertain predicate annotation"""
    predicate: str
    arity: int
    uncertain_position: int
    rho: Optional[int] | Optional[float]= None
    sigma: Optional[int] | Optional[float]= None


class RewriterConfig:
    """Configuration for the rewriter"""

    def __init__(self):
        self.semantics = "naive"  # or "set"
        self.quantifier1 = "any"
        self.quantifier2 = "any"
        self.uncertain_predicates: List[UncertainPredicate] = []

    OP_DICT = {"<": "lt", "<=": "le", ">": "gt", ">=": "ge", "==": "eq", "=": "eq", "!=": "ne"}
    QUANTIFIERS = {"forall": "all", "exists": "any"}
    PARAM_NAMES = ["N", "M", "K", "P", "Q", "R", "S", "T"]


class ASPRewriter:
    """ASP rewriter using the parser instead of regex"""

    def __init__(self, input_file: str):
        if not input_file.endswith('.asp') and not input_file.endswith('.lp'):
            sys.exit("Please provide a file with a .lp or .asp extension.")

        self.input_file = input_file
        self.input_lines = open(input_file).readlines()
        self.output_file = os.path.join(
            os.path.dirname(input_file),
            f"rewritten_{os.path.basename(input_file)}"
        )

        self.parser = ASPParser()
        self.parser.build()
        self.config = RewriterConfig()

    def parse_annotations(self):
        """Parse all annotation lines (#uncertain, #set-based, etc.)"""
        for line in self.input_lines:
            line = line.strip()

            # Check for semantics
            if "#set-based semantics" in line:
                self.config.semantics = "set"
            elif "#naive-based semantics" in line:
                self.config.semantics = "naive"

            # Parse uncertain predicate annotations
            if line.startswith("#uncertain"):
                uncertain = self._parse_uncertain_annotation(line)
                if uncertain:
                    self.config.uncertain_predicates.append(uncertain)

            # Parse operators for set semantics
            if "#operators" in line and self.config.semantics == "set":
                self._parse_operators(line)

    def _parse_uncertain_annotation(self, line: str) -> Optional[UncertainPredicate]:
        """Parse a single #uncertain annotation line"""
        import re

        # Pattern: #uncertain predicate/arity, position.
        match = re.search(r'#uncertain\s+([\w_]+)/(\d+)\s*,\s*(\d+)\.', line)
        if not match:
            raise ValueError(f"Invalid uncertain annotation: {line}")

        predicate = match.group(1)
        arity = int(match.group(2))
        position = int(match.group(3))

        uncertain = UncertainPredicate(
            predicate=predicate,
            arity=arity,
            uncertain_position=position
        )

        # Parse optional rho and sigma
        rs_match = re.search(r'rho\s*=\s*(\d+(?:\.\d+)?),\s*sigma\s*=\s*(\d+(?:\.\d+)?)', line)
        if rs_match:
            uncertain.rho = rs_match.group(1)
            uncertain.sigma = rs_match.group(2)

        return uncertain

    def _parse_operators(self, line: str):
        """Parse operator quantifiers for set semantics"""
        import re
        match = re.search(r'(exists|forall)\s*,\s*(exists|forall)', line)
        if match:
            self.config.quantifier1 = RewriterConfig.QUANTIFIERS[match.group(1)]
            self.config.quantifier2 = RewriterConfig.QUANTIFIERS[match.group(2)]

    def get_uncertain_predicate_names(self) -> Set[Tuple[str, int]]:
        """Get set of all uncertain predicate names"""
        return {(up.predicate, up.arity) for up in self.config.uncertain_predicates}

    def generate_abstract_rules(self) -> List[str]:
        """Generate abstract rules for uncertain predicates"""
        rules = []
        processed = set()

        # Group uncertain predicates by (name, arity)
        uncertain_by_pred: Dict[Tuple[str, int], List[UncertainPredicate]] = {}
        for up in self.config.uncertain_predicates:
            key = (up.predicate, up.arity)
            if key not in uncertain_by_pred:
                uncertain_by_pred[key] = []
            uncertain_by_pred[key].append(up)

        # Generate one abstract rule per (predicate, arity) pair
        for (pred_name, arity), uncertain_list in uncertain_by_pred.items():
            rule = self._generate_single_abstract_rule(pred_name, arity, uncertain_list)
            rules.append(rule)

        return rules

    def _generate_single_abstract_rule(
            self,
            pred_name: str,
            arity: int,
            uncertain_list: List[UncertainPredicate]
    ) -> str:
        """Generate a single abstract rule for a predicate"""

        # Map position -> UncertainPredicate
        pos_to_uncertain = {up.uncertain_position: up for up in uncertain_list}
        uncertain_positions = sorted(pos_to_uncertain.keys())

        # Assign variable names to uncertain positions
        pos_to_varname = {}
        for i, pos in enumerate(uncertain_positions):
            if i < len(RewriterConfig.PARAM_NAMES):
                pos_to_varname[pos] = RewriterConfig.PARAM_NAMES[i]
            else:
                pos_to_varname[pos] = f"U{i + 1}"

        # Build head and body terms
        head_terms = []
        body_terms = []
        split_literals = []

        for pos in range(1, arity + 1):
            if pos in pos_to_varname:
                # Uncertain position
                var_name = pos_to_varname[pos]
                head_terms.append(var_name)
                body_terms.append(f"{var_name}1")

                # Generate split literal
                uncertain = pos_to_uncertain[pos]
                split_lit = self._generate_split_literal(
                    var_name,
                    uncertain,
                    self.config.semantics
                )
                split_literals.append(split_lit)
            else:
                # Certain position
                var_name = f"X{pos}"
                head_terms.append(var_name)
                body_terms.append(var_name)

        # Construct the rule
        head = f"{pred_name}_r({', '.join(head_terms)})"
        body_parts = [f"{pred_name}({', '.join(body_terms)})"]
        body_parts.extend(split_literals)
        body = ", ".join(body_parts)

        return f"{head} :- {body}.\n"

    def _generate_split_literal(
            self,
            var_name: str,
            uncertain: UncertainPredicate,
            semantics: str
    ) -> str:
        """Generate a split literal for an uncertain position"""

        if uncertain.rho is not None:
            return f'&split_number_{semantics}({var_name}1,{uncertain.rho},{uncertain.sigma};{var_name})'
        else:
            return f'&split_number_{semantics}({var_name}1;{var_name})'

    def rewrite_rule(self, rule: Rule) -> str:
        """Rewrite a single rule, replacing uncertain predicates in body only"""
        if rule.rule_type == "fact":
            return str(rule)

        uncertain_names = {(up.predicate, up.arity) for up in self.config.uncertain_predicates}

        # Rewrite body literals
        new_body = []
        for item in rule.body:
            if isinstance(item, Literal):
                predicate_key = (item.atom.predicate, len(item.atom.terms))
                if predicate_key in uncertain_names:
                    new_atom = Atom(
                        predicate=f"{item.atom.predicate}_r",
                        terms=item.atom.terms,
                        negated=item.atom.negated
                    )
                    new_body.append(Literal(atom=new_atom, naf=item.naf))
                else:
                    new_body.append(item)
            elif isinstance(item, BuiltinAtom):
                if self.config.semantics == "set":
                    new_body.append(self._rewrite_builtin_comparison(item))
                else:
                    new_body.append(item)
            else:
                new_body.append(item)

        new_rule = Rule(head=rule.head, body=new_body, rule_type=rule.rule_type)
        return str(new_rule)

    def _rewrite_builtin_comparison(self, builtin: BuiltinAtom) -> Literal | BuiltinAtom:
        """Rewrite a builtin comparison to use &compareset"""

        op = builtin.operator

        # Do not rewrite arithmetic assignments like X = 1100 + Y
        if op == "=":
            return builtin

        if op in RewriterConfig.OP_DICT:
            op_name = RewriterConfig.OP_DICT[op]

            # Create &compareset atom
            compare_atom = Atom(
                predicate="&compareset",
                terms=[
                    builtin.left,
                    builtin.right,
                    Constant(value=op_name),
                    Constant(value=self.config.quantifier1),
                    Constant(value=self.config.quantifier2)
                ]
            )

            return Literal(atom=compare_atom, naf=False)
        return builtin

    def rewrite_program(self):
        """Main rewriting logic"""
        try:
            # Step 1: Parse annotations
            self.parse_annotations()

            # Step 2: Generate abstract rules
            abstract_rules = self.generate_abstract_rules()

            # Step 3: Process each line
            output_lines = []
            uncertain_found = False
            rule_insertion_point = None

            for i, line in enumerate(self.input_lines):
                stripped = line.strip()

                # Skip annotation lines
                if any(x in line for x in ["#set-based semantics", "#naive-based semantics", "#operators"]):
                    output_lines.append("")
                    continue

                # Mark uncertain section
                if "#uncertain" in line:
                    uncertain_found = True
                    rule_insertion_point = len(output_lines) + 1
                    output_lines.append("")
                    continue

                # Skip comments and empty lines from processing
                if not stripped or stripped.startswith('%'):
                    output_lines.append(line)
                    continue

                # Try to parse as ASP rule
                try:
                    program = self.parser.parse(line)

                    if program.rules and uncertain_found:
                        rewritten_rules = [self.rewrite_rule(r) for r in program.rules]
                        combined = "".join(
                            r + '\n' if not r.endswith('\n') else r for r in rewritten_rules
                        )
                        output_lines.append(combined)
                    else:
                        output_lines.append(line)

                except:
                    # If parsing fails, keep original line
                    output_lines.append(line)

            # Step 4: Insert abstract rules at the marked point
            if rule_insertion_point is not None:
                for rule in abstract_rules:
                    output_lines.insert(rule_insertion_point, rule)
                    rule_insertion_point += 1

            # Step 5: Write output
            with open(self.output_file, 'w') as f:
                f.writelines(output_lines)

            print(f"File processed successfully. Rewritten program saved in: {self.output_file}")

        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()


def main():
    if len(sys.argv) < 2:
        sys.exit("Please provide a filename as an argument.")

    rewriter = ASPRewriter(sys.argv[1])
    rewriter.rewrite_program()


if __name__ == "__main__":
    main()