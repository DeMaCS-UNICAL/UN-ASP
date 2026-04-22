import ply.yacc as yacc

from .asp_lexer import ASPLexer
from .asp_nodes import *

# =============================================================================
# PARSER WITH AST BUILDER
# =============================================================================

class ASPParser:
    """Parser for ASP-Core-2 language"""

    tokens = ASPLexer.tokens

    # Important: arithmetic operators have higher precedence than comparison
    precedence = (
        ('left', 'EQUAL', 'UNEQUAL', 'LESS', 'GREATER', 'LESS_OR_EQ', 'GREATER_OR_EQ'),
        ('left', 'PLUS', 'DASH'),
        ('left', 'TIMES', 'SLASH', 'BACK_SLASH'),
        ('right', 'UMINUS'),  # Unary minus
    )

    def __init__(self):
        self.lexer = ASPLexer()
        self.lexer.build()
        self.parser = None
        self.query_found = False

        # AST building
        self.program = Program()
        self.current_rule = None
        self.current_head = []
        self.current_body = []
        self.current_atom = None
        self.current_terms = []
        self.term_stack = []

    def reset(self):
        """Reset parser state"""
        self.query_found = False
        self.program = Program()
        self.current_rule = None
        self.current_head = []
        self.current_body = []
        self.current_atom = None
        self.current_terms = []
        self.term_stack = []

    # Grammar rules
    def p_program_empty(self, p):
        'program : '
        pass

    def p_program_rules(self, p):
        'program : rules'
        pass

    def p_rules_single(self, p):
        'rules : rule'
        pass

    def p_rules_multiple(self, p):
        'rules : rules rule'
        pass

    def p_rule_simple(self, p):
        'rule : simple_rule'
        pass

    def p_rule_directive(self, p):
        'rule : directive'
        pass

    # Simple rules
    def p_simple_rule_fact(self, p):
        'simple_rule : head DOT'
        rule = Rule(head=self.current_head, body=[], rule_type="fact")
        self.program.rules.append(rule)
        self.current_head = []

    def p_simple_rule_empty_body(self, p):
        'simple_rule : head CONS DOT'
        rule = Rule(head=self.current_head, body=[], rule_type="rule")
        self.program.rules.append(rule)
        self.current_head = []

    def p_simple_rule_with_body(self, p):
        'simple_rule : head CONS body DOT'
        rule = Rule(head=self.current_head, body=self.current_body, rule_type="rule")
        self.program.rules.append(rule)
        self.current_head = []
        self.current_body = []

    def p_simple_rule_constraint(self, p):
        'simple_rule : CONS body DOT'
        rule = Rule(head=[], body=self.current_body, rule_type="constraint")
        self.program.rules.append(rule)
        self.current_body = []

    def p_simple_rule_query(self, p):
        'simple_rule : query'
        if self.query_found:
            raise SyntaxError("A query has already been found")
        self.query_found = True

    # Head
    def p_head(self, p):
        'head : disjunction'
        pass

    # Body
    def p_body(self, p):
        'body : conjunction'
        pass

    # Disjunction
    def p_disjunction_single(self, p):
        'disjunction : classic_literal'
        if self.current_atom:
            self.current_head.append(self.current_atom)
            self.current_atom = None

    def p_disjunction_multiple(self, p):
        'disjunction : disjunction VEL classic_literal'
        if self.current_atom:
            self.current_head.append(self.current_atom)
            self.current_atom = None

    # Conjunction
    def p_conjunction_single(self, p):
        'conjunction : naf_literal'
        pass

    def p_conjunction_multiple(self, p):
        'conjunction : conjunction COMMA naf_literal'
        pass

    # Literals
    def p_classic_literal_pos(self, p):
        'classic_literal : atom'
        pass

    def p_classic_literal_neg(self, p):
        'classic_literal : DASH atom'
        if self.current_atom:
            self.current_atom.negated = True

    def p_naf_literal_classic(self, p):
        'naf_literal : classic_literal'
        if self.current_atom:
            lit = Literal(atom=self.current_atom, naf=False)
            self.current_body.append(lit)
            self.current_atom = None

    def p_naf_literal_negated(self, p):
        'naf_literal : NAF classic_literal'
        if self.current_atom:
            lit = Literal(atom=self.current_atom, naf=True)
            self.current_body.append(lit)
            self.current_atom = None

    def p_naf_literal_builtin(self, p):
        'naf_literal : builtin_atom'
        pass

    # Builtin atoms
    def p_builtin_atom(self, p):
        '''builtin_atom : arith_term compareop arith_term'''
        if len(self.term_stack) >= 2:
            right = self.term_stack.pop()
            left = self.term_stack.pop()
            builtin = BuiltinAtom(left=left, operator=p[2], right=right)
            self.current_body.append(builtin)

    def p_compareop_equal(self, p):
        'compareop : EQUAL'
        p[0] = '='

    def p_compareop_unequal(self, p):
        'compareop : UNEQUAL'
        p[0] = '!='

    def p_compareop_less(self, p):
        'compareop : LESS'
        p[0] = '<'

    def p_compareop_greater(self, p):
        'compareop : GREATER'
        p[0] = '>'

    def p_compareop_less_eq(self, p):
        'compareop : LESS_OR_EQ'
        p[0] = '<='

    def p_compareop_greater_eq(self, p):
        'compareop : GREATER_OR_EQ'
        p[0] = '>='

    # Atoms
    def p_atom_predicate(self, p):
        'atom : SYMBOLIC_CONSTANT'
        self.current_atom = Atom(predicate=p[1], terms=[])

    def p_atom_with_terms(self, p):
        'atom : SYMBOLIC_CONSTANT PARAM_OPEN terms PARAM_CLOSE'
        self.current_atom = Atom(predicate=p[1], terms=self.current_terms[:])
        self.current_terms = []

    def p_atom_empty_params(self, p):
        'atom : SYMBOLIC_CONSTANT PARAM_OPEN PARAM_CLOSE'
        self.current_atom = Atom(predicate=p[1], terms=[])

    # Terms (base terms without arithmetic)
    def p_terms_single(self, p):
        'terms : term'
        if self.term_stack:
            self.current_terms.append(self.term_stack.pop())

    def p_terms_multiple(self, p):
        'terms : terms COMMA term'
        if self.term_stack:
            self.current_terms.append(self.term_stack.pop())

    # Base terms
    def p_term_constant(self, p):
        'term : SYMBOLIC_CONSTANT'
        self.term_stack.append(Constant(value=p[1]))

    def p_term_number(self, p):
        'term : NUMBER'
        self.term_stack.append(Number(value=p[1]))

    def p_term_float(self, p):
        'term : FLOAT_NUMBER'
        self.term_stack.append(Number(value=p[1]))

    def p_term_variable(self, p):
        'term : VARIABLE'
        self.term_stack.append(Variable(name=p[1]))

    def p_term_string(self, p):
        'term : STRING'
        self.term_stack.append(Constant(value=p[1]))

    def p_term_anon(self, p):
        'term : ANON_VAR'
        self.term_stack.append(AnonymousVariable())

    def p_term_function(self, p):
        'term : SYMBOLIC_CONSTANT PARAM_OPEN terms PARAM_CLOSE'
        args = self.current_terms[:]
        self.current_terms = []
        self.term_stack.append(FunctionTerm(functor=p[1], args=args))

    def p_term_paren(self, p):
        'term : PARAM_OPEN arith_term PARAM_CLOSE'
        pass  # arith_term already pushed to stack

    def p_term_range(self, p):
        'term : NUMBER DDOT NUMBER'
        self.term_stack.append(RangeTerm(start=str(p[1]), end=str(p[3])))

    # Arithmetic terms - separate from base terms
    def p_arith_term_base(self, p):
        'arith_term : term'
        pass  # term already pushed to stack

    def p_arith_term_plus(self, p):
        'arith_term : arith_term PLUS arith_term'
        if len(self.term_stack) >= 2:
            right = self.term_stack.pop()
            left = self.term_stack.pop()
            self.term_stack.append(ArithmeticTerm(operator='+', left=left, right=right))

    def p_arith_term_minus(self, p):
        'arith_term : arith_term DASH arith_term'
        if len(self.term_stack) >= 2:
            right = self.term_stack.pop()
            left = self.term_stack.pop()
            self.term_stack.append(ArithmeticTerm(operator='-', left=left, right=right))

    def p_arith_term_times(self, p):
        'arith_term : arith_term TIMES arith_term'
        if len(self.term_stack) >= 2:
            right = self.term_stack.pop()
            left = self.term_stack.pop()
            self.term_stack.append(ArithmeticTerm(operator='*', left=left, right=right))

    def p_arith_term_div(self, p):
        'arith_term : arith_term SLASH arith_term'
        if len(self.term_stack) >= 2:
            right = self.term_stack.pop()
            left = self.term_stack.pop()
            self.term_stack.append(ArithmeticTerm(operator='/', left=left, right=right))

    def p_arith_term_mod(self, p):
        'arith_term : arith_term BACK_SLASH arith_term'
        if len(self.term_stack) >= 2:
            right = self.term_stack.pop()
            left = self.term_stack.pop()
            self.term_stack.append(ArithmeticTerm(operator='\\', left=left, right=right))

    def p_arith_term_neg(self, p):
        'arith_term : DASH arith_term %prec UMINUS'
        if self.term_stack:
            t = self.term_stack.pop()
            self.term_stack.append(NegatedTerm(term=t))

    def p_arith_term_paren(self, p):
        'arith_term : PARAM_OPEN arith_term PARAM_CLOSE'
        pass  # arith_term already on stack

    # Query
    def p_query(self, p):
        'query : atom QUERY_MARK'
        if self.current_atom:
            query = Query(atom=self.current_atom)
            self.program.queries.append(query)
            self.current_atom = None

    # Directive
    def p_directive(self, p):
        'directive : DIRECTIVE_NAME DIRECTIVE_VALUE'
        directive = Directive(name=p[1], value=p[2])
        self.program.directives.append(directive)

    def p_error(self, p):
        if p:
            print(f"Syntax error at '{p.value}' (line {p.lineno})")
        else:
            print("Syntax error at EOF")

    def build(self, **kwargs):
        """Build the parser"""
        self.parser = yacc.yacc(module=self, **kwargs)
        return self.parser

    def parse(self, data):
        """Parse ASP code and return Program object"""
        self.reset()
        self.parser.parse(data, lexer=self.lexer.lexer)
        return self.program