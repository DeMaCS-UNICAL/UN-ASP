import pytest
from src.parser.asp_lexer import ASPLexer
from src.parser.asp_parser import ASPParser
from src.parser.asp_nodes import *


class TestASPLexer:
    """Tests for ASPLexer"""

    @pytest.fixture
    def lexer(self):
        lex = ASPLexer()
        lex.build()
        return lex

    def test_basic_tokens(self, lexer):
        """Test basic token recognition"""
        lexer.lexer.input("pred(X, Y).")
        tokens = []
        while True:
            tok = lexer.lexer.token()
            if not tok:
                break
            tokens.append((tok.type, tok.value))

        assert ('SYMBOLIC_CONSTANT', 'pred') in tokens
        assert ('PARAM_OPEN', '(') in tokens
        assert ('VARIABLE', 'X') in tokens
        assert ('COMMA', ',') in tokens
        assert ('VARIABLE', 'Y') in tokens
        assert ('PARAM_CLOSE', ')') in tokens
        assert ('DOT', '.') in tokens

    def test_numbers(self, lexer):
        """Test number tokens"""
        lexer.lexer.input("42 3.14")
        tok1 = lexer.lexer.token()
        assert tok1.type == 'NUMBER'
        assert tok1.value == 42

        tok2 = lexer.lexer.token()
        assert tok2.type == 'FLOAT_NUMBER'
        assert tok2.value == 3.14

    def test_operators(self, lexer):
        """Test operator tokens"""
        lexer.lexer.input("+ - * / \\ = != < > <= >=")
        expected = [
            ('PLUS', '+'), ('DASH', '-'), ('TIMES', '*'),
            ('SLASH', '/'), ('BACK_SLASH', '\\'), ('EQUAL', '='),
            ('UNEQUAL', '!='), ('LESS', '<'), ('GREATER', '>'),
            ('LESS_OR_EQ', '<='), ('GREATER_OR_EQ', '>=')
        ]

        for exp_type, exp_val in expected:
            tok = lexer.lexer.token()
            assert tok.type == exp_type
            assert tok.value == exp_val

    def test_keywords(self, lexer):
        """Test keyword tokens"""
        lexer.lexer.input("not :- :~ \\E")

        tok1 = lexer.lexer.token()
        assert tok1.type == 'NAF'

        tok2 = lexer.lexer.token()
        assert tok2.type == 'CONS'

        tok3 = lexer.lexer.token()
        assert tok3.type == 'WCONS'

        tok4 = lexer.lexer.token()
        assert tok4.type == 'EXISTS'

    def test_aggregates(self, lexer):
        """Test aggregate tokens"""
        lexer.lexer.input("#count #max #min #sum")

        tok1 = lexer.lexer.token()
        assert tok1.type == 'AGGR_COUNT'

        tok2 = lexer.lexer.token()
        assert tok2.type == 'AGGR_MAX'

        tok3 = lexer.lexer.token()
        assert tok3.type == 'AGGR_MIN'

        tok4 = lexer.lexer.token()
        assert tok4.type == 'AGGR_SUM'

    def test_string(self, lexer):
        """Test string tokens"""
        lexer.lexer.input('"hello world"')
        tok = lexer.lexer.token()
        assert tok.type == 'STRING'
        assert tok.value == '"hello world"'

    def test_anonymous_variable(self, lexer):
        """Test anonymous variable"""
        lexer.lexer.input("_")
        tok = lexer.lexer.token()
        assert tok.type == 'ANON_VAR'

    def test_comments(self, lexer):
        """Test comment handling"""
        lexer.lexer.input("pred(X). % This is a comment\npred2(Y).")
        tokens = []
        while True:
            tok = lexer.lexer.token()
            if not tok:
                break
            tokens.append(tok.type)

        assert 'COMMENT' not in tokens
        assert tokens.count('SYMBOLIC_CONSTANT') == 2

    def test_newlines(self, lexer):
        """Test newline handling"""
        lexer.lexer.input("a.\nb.")
        lexer.lexer.token()  # 'a'
        lexer.lexer.token()  # '.'
        lexer.lexer.token()  # 'b'
        assert lexer.line_num == 2

    def test_directive(self, lexer):
        """Test directive parsing"""
        lexer.lexer.input("#show pred/2")
        tok1 = lexer.lexer.token()
        assert tok1.type == 'DIRECTIVE_NAME'
        assert tok1.value == '#show'

        tok2 = lexer.lexer.token()
        assert tok2.type == 'DIRECTIVE_VALUE'
        assert tok2.value == ' pred/2'

    def test_annotations(self, lexer):
        """Test annotation tokens"""
        lexer.lexer.input("%@rule_ordering @value")

        tok1 = lexer.lexer.token()
        assert tok1.type == 'ANNOTATION_RULE_ORDERING'

        tok2 = lexer.lexer.token()
        assert tok2.type == 'ANNOTATION_ORDERING_VALUE'

    def test_range(self, lexer):
        """Test range operator"""
        lexer.lexer.input("1..10")
        tok1 = lexer.lexer.token()
        assert tok1.type == 'NUMBER'
        tok2 = lexer.lexer.token()
        assert tok2.type == 'DDOT'
        tok3 = lexer.lexer.token()
        assert tok3.type == 'NUMBER'

    def test_error_handling(self, lexer, capsys):
        """Test error handling for illegal characters"""
        lexer.lexer.input("$$$")
        lexer.lexer.token()
        captured = capsys.readouterr()
        assert "Illegal character" in captured.out


class TestASPParser:
    """Tests for ASPParser"""

    @pytest.fixture
    def parser(self):
        p = ASPParser()
        p.build()
        return p

    def test_simple_fact(self, parser):
        """Test parsing a simple fact"""
        program = parser.parse("bird(tweety).")
        assert len(program.rules) == 1
        rule = program.rules[0]
        assert rule.is_fact()
        assert len(rule.head) == 1
        assert rule.head[0].predicate == "bird"
        assert len(rule.head[0].terms) == 1
        assert isinstance(rule.head[0].terms[0], Constant)

    def test_multiple_facts(self, parser):
        """Test parsing multiple facts"""
        program = parser.parse("bird(tweety). bird(polly).")
        assert len(program.rules) == 2
        assert all(r.is_fact() for r in program.rules)

    def test_rule_with_body(self, parser):
        """Test parsing a rule with body"""
        program = parser.parse("flies(X) :- bird(X).")
        assert len(program.rules) == 1
        rule = program.rules[0]
        assert not rule.is_fact()
        assert len(rule.head) == 1
        assert len(rule.body) == 1
        assert isinstance(rule.body[0], Literal)

    def test_rule_with_multiple_body_literals(self, parser):
        """Test parsing rule with multiple body literals"""
        program = parser.parse("flies(X) :- bird(X), not penguin(X).")
        rule = program.rules[0]
        assert len(rule.body) == 2
        assert not rule.body[0].is_naf()
        assert rule.body[1].is_naf()

    def test_constraint(self, parser):
        """Test parsing a constraint"""
        program = parser.parse(":- bird(X), penguin(X).")
        assert len(program.rules) == 1
        rule = program.rules[0]
        assert rule.is_constraint()
        assert len(rule.head) == 0
        assert len(rule.body) == 2

    def test_disjunctive_head(self, parser):
        """Test parsing disjunctive head"""
        program = parser.parse("a(X) | b(X) :- c(X).")
        rule = program.rules[0]
        assert len(rule.head) == 2
        assert rule.head[0].predicate == "a"
        assert rule.head[1].predicate == "b"

    def test_classical_negation(self, parser):
        """Test parsing classical negation"""
        program = parser.parse("-flies(tweety).")
        rule = program.rules[0]
        assert rule.head[0].is_negated()

    def test_builtin_atom(self, parser):
        """Test parsing builtin atoms"""
        program = parser.parse("result(X) :- X = 5.")
        rule = program.rules[0]
        assert len(rule.body) == 1
        assert isinstance(rule.body[0], BuiltinAtom)
        assert rule.body[0].operator == '='

    def test_comparison_operators(self, parser):
        """Test all comparison operators"""
        comparisons = ["!=", "<", ">", "<=", ">="]
        for op in comparisons:
            program = parser.parse(f"test(X) :- X {op} 5.")
            rule = program.rules[0]
            assert isinstance(rule.body[0], BuiltinAtom)

    def test_arithmetic_operations(self, parser):
        """Test arithmetic operations"""
        program = parser.parse("result(Z) :- X = 5, Y = 3, Z = X + Y.")
        rule = program.rules[0]
        assert len(rule.body) == 3
        last_builtin = rule.body[2]
        assert isinstance(last_builtin, BuiltinAtom)
        assert isinstance(last_builtin.right, ArithmeticTerm)
        assert last_builtin.right.operator == '+'

    def test_arithmetic_operators(self, parser):
        """Test all arithmetic operators"""
        operators = ['+', '-', '*', '/', '\\']
        for op in operators:
            program = parser.parse(f"result(Z) :- Z = 5 {op} 3.")
            rule = program.rules[0]
            builtin = rule.body[0]
            assert isinstance(builtin.right, ArithmeticTerm)

    def test_unary_minus(self, parser):
        """Test unary minus"""
        program = parser.parse("result(X) :- X = -5.")
        rule = program.rules[0]
        builtin = rule.body[0]
        assert isinstance(builtin.right, NegatedTerm)

    def test_variables_and_constants(self, parser):
        """Test variables and constants"""
        program = parser.parse("test(X, abc, 42).")
        rule = program.rules[0]
        terms = rule.head[0].terms
        assert isinstance(terms[0], Variable)
        assert isinstance(terms[1], Constant)
        assert isinstance(terms[2], Number)

    def test_anonymous_variable(self, parser):
        """Test anonymous variable"""
        program = parser.parse("test(_).")
        rule = program.rules[0]
        assert isinstance(rule.head[0].terms[0], AnonymousVariable)

    def test_function_terms(self, parser):
        """Test function terms"""
        program = parser.parse("test(f(a, b)).")
        rule = program.rules[0]
        term = rule.head[0].terms[0]
        assert isinstance(term, FunctionTerm)
        assert term.functor == "f"
        assert len(term.args) == 2

    def test_range_term(self, parser):
        """Test range terms"""
        program = parser.parse("test(X) :- X = 1..10.")
        rule = program.rules[0]
        builtin = rule.body[0]
        assert isinstance(builtin.right, RangeTerm)

    def test_query(self, parser):
        """Test query parsing"""
        program = parser.parse("bird(tweety)?")
        assert len(program.queries) == 1
        query = program.queries[0]
        assert query.get_predicate() == "bird"

    def test_directive(self, parser):
        """Test directive parsing"""
        program = parser.parse("#show bird/1")
        assert len(program.directives) == 1
        directive = program.directives[0]
        assert directive.name == "#show"

    def test_empty_program(self, parser):
        """Test parsing empty program"""
        program = parser.parse("")
        assert len(program.rules) == 0
        assert len(program.queries) == 0

    def test_parser_reset(self, parser):
        """Test parser reset functionality"""
        parser.parse("a.")
        assert len(parser.program.rules) == 1
        parser.reset()
        assert len(parser.program.rules) == 0
        assert parser.query_found == False

    def test_query_multiple_terms(self, parser):
        """Test query with multiple terms"""
        program = parser.parse("test(X, Y)?")
        assert len(program.queries) == 1
        query = program.queries[0]
        assert len(query.get_terms()) == 2

    def test_string_term(self, parser):
        """Test string terms"""
        program = parser.parse('test("hello").')
        rule = program.rules[0]
        term = rule.head[0].terms[0]
        assert isinstance(term, Constant)
        assert term.value == '"hello"'

    def test_float_number(self, parser):
        """Test float numbers"""
        program = parser.parse("test(3.14).")
        rule = program.rules[0]
        term = rule.head[0].terms[0]
        assert isinstance(term, Number)
        assert term.value == 3.14

    def test_parenthesized_arithmetic(self, parser):
        """Test parenthesized arithmetic expressions"""
        program = parser.parse("result(Z) :- Z = (5 + 3) * 2.")
        rule = program.rules[0]
        assert isinstance(rule.body[0], BuiltinAtom)

    def test_empty_body_rule(self, parser):
        """Test rule with empty body"""
        program = parser.parse("a :- .")
        assert len(program.rules) == 1
        rule = program.rules[0]
        assert len(rule.body) == 0


class TestASTNodes:
    """Tests for AST Node classes"""

    def test_constant_str(self):
        """Test Constant string representation"""
        c = Constant(value="test")
        assert str(c) == "test"

    def test_variable_str(self):
        """Test Variable string representation"""
        v = Variable(name="X")
        assert str(v) == "X"

    def test_number_str(self):
        """Test Number string representation"""
        n = Number(value=42)
        assert str(n) == "42"

    def test_anonymous_variable_str(self):
        """Test AnonymousVariable string representation"""
        av = AnonymousVariable()
        assert str(av) == "_"

    def test_function_term_str(self):
        """Test FunctionTerm string representation"""
        f = FunctionTerm(functor="f", args=[Constant("a"), Variable("X")])
        assert str(f) == "f(a,X)"

    def test_function_term_no_args(self):
        """Test FunctionTerm with no arguments"""
        f = FunctionTerm(functor="f", args=[])
        assert str(f) == "f"

    def test_arithmetic_term_str(self):
        """Test ArithmeticTerm string representation"""
        at = ArithmeticTerm(operator="+", left=Number(5), right=Number(3))
        assert str(at) == "(5+3)"

    def test_range_term_str(self):
        """Test RangeTerm string representation"""
        rt = RangeTerm(start="1", end="10")
        assert str(rt) == "1..10"

    def test_negated_term_str(self):
        """Test NegatedTerm string representation"""
        nt = NegatedTerm(term=Number(5))
        assert str(nt) == "-5"

    def test_atom_methods(self):
        """Test Atom methods"""
        atom = Atom(predicate="test", terms=[Variable("X"), Constant("a")])
        assert atom.get_predicate() == "test"
        assert atom.get_arity() == 2
        assert len(atom.get_terms()) == 2
        assert not atom.is_negated()

    def test_atom_str(self):
        """Test Atom string representation"""
        atom = Atom(predicate="bird", terms=[Constant("tweety")])
        assert str(atom) == "bird(tweety)"

    def test_atom_str_no_terms(self):
        """Test Atom string representation with no terms"""
        atom = Atom(predicate="test", terms=[])
        assert str(atom) == "test"

    def test_atom_str_negated(self):
        """Test negated Atom string representation"""
        atom = Atom(predicate="test", terms=[], negated=True)
        assert str(atom) == "-test"

    def test_literal_methods(self):
        """Test Literal methods"""
        atom = Atom(predicate="bird", terms=[Variable("X")])
        lit = Literal(atom=atom, naf=True)
        assert lit.get_atom() == atom
        assert lit.is_naf()
        assert lit.get_predicate() == "bird"
        assert len(lit.get_terms()) == 1

    def test_literal_str(self):
        """Test Literal string representation"""
        atom = Atom(predicate="test", terms=[])
        lit = Literal(atom=atom, naf=False)
        assert str(lit) == "test"

        lit_naf = Literal(atom=atom, naf=True)
        assert str(lit_naf) == "not test"

    def test_builtin_atom_str(self):
        """Test BuiltinAtom string representation"""
        ba = BuiltinAtom(left=Variable("X"), operator="=", right=Number(5))
        assert str(ba) == "X = 5"

    def test_rule_methods(self):
        """Test Rule methods"""
        atom1 = Atom(predicate="a", terms=[Variable("X")])
        atom2 = Atom(predicate="b", terms=[Variable("X")])
        lit = Literal(atom=atom2, naf=False)

        rule = Rule(head=[atom1], body=[lit], rule_type="rule")

        assert rule.get_head() == [atom1]
        assert rule.get_body() == [lit]
        assert rule.get_head_atoms() == [atom1]
        assert rule.get_body_literals() == [lit]
        assert not rule.is_fact()
        assert not rule.is_constraint()
        assert not rule.is_weak_constraint()
        assert rule.get_head_predicates() == ["a"]
        assert rule.get_body_predicates() == ["b"]
        assert set(rule.get_all_predicates()) == {"a", "b"}

    def test_rule_get_variables(self):
        """Test Rule get_variables method"""
        atom = Atom(predicate="test", terms=[Variable("X"), Variable("Y")])
        rule = Rule(head=[atom], body=[], rule_type="fact")
        vars = rule.get_variables()
        assert set(vars) == {"X", "Y"}

    def test_rule_get_constants(self):
        """Test Rule get_constants method"""
        atom = Atom(predicate="test", terms=[Constant("a"), Constant("b")])
        rule = Rule(head=[atom], body=[], rule_type="fact")
        consts = rule.get_constants()
        assert set(consts) == {"a", "b"}

    def test_rule_get_variables_complex(self):
        """Test get_variables with complex terms"""
        func_term = FunctionTerm(functor="f", args=[Variable("X")])
        atom = Atom(predicate="test", terms=[func_term])
        rule = Rule(head=[atom], body=[], rule_type="fact")
        vars = rule.get_variables()
        assert "X" in vars

    def test_rule_get_variables_arithmetic(self):
        """Test get_variables with arithmetic terms"""
        arith_term = ArithmeticTerm(operator="+", left=Variable("X"), right=Variable("Y"))
        builtin = BuiltinAtom(left=Variable("Z"), operator="=", right=arith_term)
        rule = Rule(head=[], body=[builtin], rule_type="rule")
        vars = rule.get_variables()
        assert set(vars) == {"X", "Y", "Z"}

    def test_rule_get_constants_complex(self):
        """Test get_constants with complex terms"""
        func_term = FunctionTerm(functor="f", args=[Constant("a")])
        atom = Atom(predicate="test", terms=[func_term])
        rule = Rule(head=[atom], body=[], rule_type="fact")
        consts = rule.get_constants()
        assert "a" in consts

    def test_rule_str_constraint(self):
        """Test constraint string representation"""
        lit = Literal(atom=Atom(predicate="test", terms=[]), naf=False)
        rule = Rule(head=[], body=[lit], rule_type="constraint")
        assert str(rule) == ":- test."

    def test_rule_str_fact(self):
        """Test fact string representation"""
        atom = Atom(predicate="test", terms=[])
        rule = Rule(head=[atom], body=[], rule_type="fact")
        assert str(rule) == "test."

    def test_rule_str_rule(self):
        """Test rule string representation"""
        atom = Atom(predicate="a", terms=[])
        lit = Literal(atom=Atom(predicate="b", terms=[]), naf=False)
        rule = Rule(head=[atom], body=[lit], rule_type="rule")
        assert str(rule) == "a :- b."

    def test_rule_get_all_atoms(self):
        """Test get_all_atoms method"""
        atom1 = Atom(predicate="a", terms=[])
        atom2 = Atom(predicate="b", terms=[])
        lit = Literal(atom=atom2, naf=False)
        rule = Rule(head=[atom1], body=[lit], rule_type="rule")
        atoms = rule.get_all_atoms()
        assert len(atoms) == 2

    def test_query_methods(self):
        """Test Query methods"""
        atom = Atom(predicate="test", terms=[Variable("X")])
        query = Query(atom=atom)
        assert query.get_atom() == atom
        assert query.get_predicate() == "test"
        assert len(query.get_terms()) == 1
        assert str(query) == "test(X)?"

    def test_directive_str(self):
        """Test Directive string representation"""
        directive = Directive(name="#show", value="test/1")
        assert str(directive) == "#show test/1"

    def test_program_methods(self):
        """Test Program methods"""
        atom1 = Atom(predicate="a", terms=[])
        atom2 = Atom(predicate="b", terms=[])
        fact = Rule(head=[atom1], body=[], rule_type="fact")
        constraint = Rule(head=[], body=[Literal(atom=atom2)], rule_type="constraint")
        query = Query(atom=atom1)
        directive = Directive(name="#show", value="test")

        program = Program(rules=[fact, constraint], queries=[query], directives=[directive])

        assert len(program.get_rules()) == 2
        assert len(program.get_facts()) == 1
        assert len(program.get_constraints()) == 1
        assert len(program.get_queries()) == 1
        assert len(program.get_directives()) == 1
        assert "a" in program.get_predicates()
        assert "b" in program.get_predicates()

    def test_program_get_rules_by_predicate(self):
        """Test get_rules_by_predicate method"""
        atom1 = Atom(predicate="test", terms=[])
        atom2 = Atom(predicate="other", terms=[])
        rule1 = Rule(head=[atom1], body=[], rule_type="fact")
        rule2 = Rule(head=[atom2], body=[], rule_type="fact")

        program = Program(rules=[rule1, rule2])
        test_rules = program.get_rules_by_predicate("test")
        assert len(test_rules) == 1
        assert test_rules[0] == rule1

    def test_program_get_atoms(self):
        """Test get_atoms method"""
        atom1 = Atom(predicate="a", terms=[])
        atom2 = Atom(predicate="b", terms=[])
        rule = Rule(head=[atom1], body=[Literal(atom=atom2)], rule_type="rule")
        program = Program(rules=[rule])
        atoms = program.get_atoms()
        assert len(atoms) == 2

    def test_program_str(self):
        """Test Program string representation"""
        atom = Atom(predicate="test", terms=[])
        rule = Rule(head=[atom], body=[], rule_type="fact")
        program = Program(rules=[rule])
        assert "test." in str(program)


class TestComplexScenarios:
    """Tests for complex parsing scenarios"""

    @pytest.fixture
    def parser(self):
        p = ASPParser()
        p.build()
        return p

    def test_complex_rule(self, parser):
        """Test parsing a complex rule"""
        code = """
        reachable(X, Y) :- edge(X, Y).
        reachable(X, Z) :- edge(X, Y), reachable(Y, Z).
        """
        program = parser.parse(code)
        assert len(program.rules) == 2

    def test_choice_rule(self, parser):
        """Test parsing choice-like structures"""
        code = "selected(X) | not_selected(X) :- item(X)."
        program = parser.parse(code)
        rule = program.rules[0]
        assert len(rule.head) == 2

    def test_nested_functions(self, parser):
        """Test nested function terms"""
        code = "test(f(g(a)))."
        program = parser.parse(code)
        rule = program.rules[0]
        term = rule.head[0].terms[0]
        assert isinstance(term, FunctionTerm)
        assert isinstance(term.args[0], FunctionTerm)

    def test_mixed_literals(self, parser):
        """Test mixed positive and negative literals"""
        code = "result(X) :- a(X), not b(X), -c(X)."
        program = parser.parse(code)
        rule = program.rules[0]
        assert len(rule.body) == 3
        assert not rule.body[0].is_naf()
        assert rule.body[1].is_naf()
        assert rule.body[2].atom.is_negated()

    def test_complex_arithmetic(self, parser):
        """Test complex arithmetic expressions"""
        code = "result(Z) :- Z = (X + Y) * (X - Y)."
        program = parser.parse(code)
        rule = program.rules[0]
        assert isinstance(rule.body[0], BuiltinAtom)

    def test_multiple_predicates(self, parser):
        """Test program with multiple predicates"""
        code = """
        bird(tweety).
        bird(polly).
        penguin(tux).
        flies(X) :- bird(X), not penguin(X).
        """
        program = parser.parse(code)
        predicates = program.get_predicates()
        assert "bird" in predicates
        assert "penguin" in predicates
        assert "flies" in predicates


"""
Add these test classes to your test_parser.py file
"""


class TestMultilineRules:
    """Tests for multi-line rule parsing"""

    @pytest.fixture
    def parser(self):
        p = ASPParser()
        p.build()
        return p

    def test_rule_head_body_separate_lines(self, parser):
        """Test rule with head and body on separate lines"""
        code = "a(X) :-\nb(X)."
        program = parser.parse(code)
        assert len(program.rules) == 1
        rule = program.rules[0]
        assert len(rule.head) == 1
        assert rule.head[0].predicate == "a"
        assert len(rule.body) == 1
        assert rule.body[0].atom.predicate == "b"

    def test_rule_body_split_multiple_lines(self, parser):
        """Test rule with body split across multiple lines"""
        code = "a(X) :- b(X),\nc(X)."
        program = parser.parse(code)
        assert len(program.rules) == 1
        rule = program.rules[0]
        assert len(rule.body) == 2

    def test_rule_three_lines_indented(self, parser):
        """Test rule on three lines with indentation"""
        code = "a(X) :-\n    b(X),\n    c(X)."
        program = parser.parse(code)
        assert len(program.rules) == 1
        rule = program.rules[0]
        assert len(rule.body) == 2
        assert rule.body[0].atom.predicate == "b"
        assert rule.body[1].atom.predicate == "c"

    def test_rule_with_tabs_and_spaces(self, parser):
        """Test rule with mixed tabs and spaces"""
        code = "a(X) :-\n\tb(X),\n\t\tc(X)."
        program = parser.parse(code)
        assert len(program.rules) == 1
        rule = program.rules[0]
        assert len(rule.body) == 2

    def test_multiple_multiline_rules(self, parser):
        """Test multiple multi-line rules in sequence"""
        code = """a(X) :-
    b(X).
c(Y) :-
    d(Y)."""
        program = parser.parse(code)
        assert len(program.rules) == 2
        assert program.rules[0].head[0].predicate == "a"
        assert program.rules[1].head[0].predicate == "c"

    def test_multiline_with_negation(self, parser):
        """Test multi-line rule with negation"""
        code = """safe(X) :-
    person(X),
    not criminal(X)."""
        program = parser.parse(code)
        assert len(program.rules) == 1
        rule = program.rules[0]
        assert len(rule.body) == 2
        assert not rule.body[0].is_naf()
        assert rule.body[1].is_naf()

    def test_multiline_with_arithmetic(self, parser):
        """Test multi-line rule with arithmetic"""
        code = """result(Z) :-
    X = 5,
    Y = 3,
    Z = X + Y."""
        program = parser.parse(code)
        assert len(program.rules) == 1
        rule = program.rules[0]
        assert len(rule.body) == 3

    def test_multiline_constraint(self, parser):
        """Test multi-line constraint"""
        code = """:- edge(X, Y),
    edge(Y, X),
    X != Y."""
        program = parser.parse(code)
        assert len(program.rules) == 1
        rule = program.rules[0]
        assert rule.is_constraint()
        assert len(rule.body) == 3

    def test_multiline_disjunctive_head(self, parser):
        """Test multi-line rule with disjunctive head"""
        code = """red(X) | blue(X) :-
    node(X)."""
        program = parser.parse(code)
        assert len(program.rules) == 1
        rule = program.rules[0]
        assert len(rule.head) == 2

    def test_multiline_complex_terms(self, parser):
        """Test multi-line rule with complex terms"""
        code = """path(f(X, Y), Z) :-
    edge(f(X, Y), Z),
    node(X),
    node(Y)."""
        program = parser.parse(code)
        assert len(program.rules) == 1
        rule = program.rules[0]
        assert isinstance(rule.head[0].terms[0], FunctionTerm)

    def test_empty_line_in_rule(self, parser):
        """Test rule with empty line in middle (should work)"""
        code = """a(X) :-

    b(X)."""
        program = parser.parse(code)
        assert len(program.rules) == 1

    def test_comment_between_lines(self, parser):
        """Test rule with comment between lines"""
        code = """a(X) :-
    % This is a comment
    b(X)."""
        program = parser.parse(code)
        assert len(program.rules) == 1
        rule = program.rules[0]
        assert len(rule.body) == 1

    def test_multiline_very_long_body(self, parser):
        """Test rule with very long body across many lines"""
        code = """result(X) :-
    a(X),
    b(X),
    c(X),
    d(X),
    e(X)."""
        program = parser.parse(code)
        assert len(program.rules) == 1
        rule = program.rules[0]
        assert len(rule.body) == 5

    def test_multiline_mixed_with_single_line(self, parser):
        """Test mixing multi-line and single-line rules"""
        code = """a(X) :- b(X).
c(Y) :-
    d(Y),
    e(Y).
f(Z) :- g(Z)."""
        program = parser.parse(code)
        assert len(program.rules) == 3
        assert len(program.rules[0].body) == 1
        assert len(program.rules[1].body) == 2
        assert len(program.rules[2].body) == 1


class TestRewriterMergeFunction:
    """Tests for the _merge_multiline_rules function"""

    def _merge_multiline_rules(self, lines):
        """
        Merge multi-line rules into complete statements.
        Returns list of (merged_rule, [original_line_indices])
        """
        merged = []
        current_rule = ""
        current_indices = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Skip empty lines and comments
            if not stripped or stripped.startswith('%'):
                if current_rule:
                    # We have an incomplete rule, keep accumulating
                    current_rule += line
                    current_indices.append(i)
                else:
                    # Standalone comment/empty line
                    merged.append((line, [i]))
                continue

            # Skip annotation lines
            if stripped.startswith('#'):
                if current_rule:
                    # Flush current rule first
                    merged.append((current_rule, current_indices))
                    current_rule = ""
                    current_indices = []
                merged.append((line, [i]))
                continue

            # Accumulate the line
            current_rule += line
            current_indices.append(i)

            # Check if rule is complete (ends with '.')
            if stripped.endswith('.'):
                merged.append((current_rule, current_indices))
                current_rule = ""
                current_indices = []

        # Flush any remaining rule
        if current_rule:
            merged.append((current_rule, current_indices))

        return merged

    def test_merge_simple_multiline(self):
        """Test merging simple multi-line rule"""
        lines = ["a(X) :-\n", "b(X).\n"]
        merged = self._merge_multiline_rules(lines)
        assert len(merged) == 1
        assert merged[0][0] == "a(X) :-\nb(X).\n"
        assert merged[0][1] == [0, 1]

    def test_merge_multiple_rules(self):
        """Test merging multiple rules"""
        lines = ["a(X) :- b(X).\n", "c(Y) :-\n", "d(Y).\n"]
        merged = self._merge_multiline_rules(lines)
        assert len(merged) == 2
        assert merged[0][1] == [0]
        assert merged[1][1] == [1, 2]

    def test_merge_with_comments(self):
        """Test merging with standalone comments"""
        lines = ["% Comment\n", "a(X) :-\n", "b(X).\n"]
        merged = self._merge_multiline_rules(lines)
        assert len(merged) == 2
        assert merged[0][0] == "% Comment\n"
        assert merged[1][0] == "a(X) :-\nb(X).\n"

    def test_merge_with_empty_lines(self):
        """Test merging with empty lines"""
        lines = ["\n", "a(X) :- b(X).\n", "\n"]
        merged = self._merge_multiline_rules(lines)
        assert len(merged) == 3

    def test_merge_with_annotations(self):
        """Test merging with annotation lines"""
        lines = ["#uncertain test/2, 1.\n", "a(X) :-\n", "b(X).\n"]
        merged = self._merge_multiline_rules(lines)
        assert len(merged) == 2
        assert merged[0][0] == "#uncertain test/2, 1.\n"
        assert merged[1][0] == "a(X) :-\nb(X).\n"

    def test_merge_incomplete_rule(self):
        """Test merging incomplete rule at end of file"""
        lines = ["a(X) :-\n", "b(X)"]  # No final period
        merged = self._merge_multiline_rules(lines)
        assert len(merged) == 1
        assert merged[0][0] == "a(X) :-\nb(X)"

    def test_merge_three_line_rule(self):
        """Test merging three-line rule"""
        lines = ["a(X) :-\n", "    b(X),\n", "    c(X).\n"]
        merged = self._merge_multiline_rules(lines)
        assert len(merged) == 1
        assert merged[0][1] == [0, 1, 2]

    def test_merge_preserves_whitespace(self):
        """Test that merging preserves whitespace"""
        lines = ["a(X) :-\n", "    b(X).\n"]
        merged = self._merge_multiline_rules(lines)
        assert "    " in merged[0][0]

    def test_merge_comment_in_middle(self):
        """Test comment in middle of multi-line rule"""
        lines = ["a(X) :-\n", "    % comment\n", "    b(X).\n"]
        merged = self._merge_multiline_rules(lines)
        assert len(merged) == 1
        assert "% comment" in merged[0][0]

    def test_merge_multiple_facts(self):
        """Test merging multiple facts"""
        lines = ["a(1).\n", "a(2).\n", "a(3).\n"]
        merged = self._merge_multiline_rules(lines)
        assert len(merged) == 3
        assert all(len(indices) == 1 for _, indices in merged)


class TestArithmeticInMultiline:
    """Tests for arithmetic expressions in multi-line rules"""

    @pytest.fixture
    def parser(self):
        p = ASPParser()
        p.build()
        return p

    def test_arithmetic_split_across_lines(self, parser):
        """Test arithmetic expression split across lines"""
        code = """result(Z) :-
    X = 5,
    Y = 3,
    Z = X + Y."""
        program = parser.parse(code)
        rule = program.rules[0]
        last_builtin = rule.body[2]
        assert isinstance(last_builtin, BuiltinAtom)
        assert isinstance(last_builtin.right, ArithmeticTerm)

    def test_complex_arithmetic_multiline(self, parser):
        """Test complex arithmetic on multiple lines"""
        code = """calc(Result) :-
    A = 10,
    B = 5,
    C = 2,
    Result = (A + B) * C."""
        program = parser.parse(code)
        rule = program.rules[0]
        assert len(rule.body) == 4

    def test_comparison_multiline(self, parser):
        """Test comparison operators on multiple lines"""
        code = """valid(X, Y) :-
    value(X, V1),
    value(Y, V2),
    V1 > V2."""
        program = parser.parse(code)
        rule = program.rules[0]
        assert len(rule.body) == 3
        assert isinstance(rule.body[2], BuiltinAtom)
        assert rule.body[2].operator == '>'