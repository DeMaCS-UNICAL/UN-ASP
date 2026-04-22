import pytest
from unittest.mock import mock_open, patch

from src.rewriter import ASPRewriter, UncertainPredicate, main

# ---------------------------------------------------------------------------
# parse_annotations
# ---------------------------------------------------------------------------

def test_parse_annotations_naive_base_case():
    mock_file_data = "#naive-based semantics\n#uncertain log/2, 2.\n"

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.parse_annotations()

        assert rewriter.config.semantics == "naive"
        assert rewriter.config.quantifier1 == "any"
        assert rewriter.config.quantifier2 == "any"
        assert rewriter.config.uncertain_predicates == [
            UncertainPredicate(predicate="log", arity=2, uncertain_position=2)
        ]


def test_parse_annotations_set_base_case():
    mock_file_data = "#set-based semantics\n#uncertain log/2, 2.\n"

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.parse_annotations()

        assert rewriter.config.semantics == "set"
        assert rewriter.config.quantifier1 == "any"
        assert rewriter.config.quantifier2 == "any"
        assert rewriter.config.uncertain_predicates == [
            UncertainPredicate(predicate="log", arity=2, uncertain_position=2)
        ]


def test_parse_annotations_set_sigma_rho():
    mock_file_data = "#set-based semantics\n#uncertain time/1, 1. rho=10, sigma=10\n"

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.parse_annotations()

        assert rewriter.config.semantics == "set"
        assert rewriter.config.uncertain_predicates == [
            UncertainPredicate(
                predicate="time",
                arity=1,
                uncertain_position=1,
                rho="10",
                sigma="10",
            )
        ]


def test_parse_annotations_set_quantifier():
    mock_file_data = (
        "#set-based semantics\n"
        "#uncertain time/1, 1. rho=10, sigma=10\n"
        "#operators = forall, exists\n"
    )

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.parse_annotations()

        assert rewriter.config.semantics == "set"
        assert rewriter.config.quantifier1 == "all"
        assert rewriter.config.quantifier2 == "any"
        assert rewriter.config.uncertain_predicates == [
            UncertainPredicate(
                predicate="time",
                arity=1,
                uncertain_position=1,
                rho="10",
                sigma="10",
            )
        ]


def test_parse_annotations_several_uncertain():
    mock_file_data = (
        "#uncertain time/1, 1. rho=10, sigma=10\n"
        "#uncertain log/2, 2. rho=20, sigma=10\n"
        "#uncertain meters/3, 1. rho=5, sigma=5\n"
        "#operators = forall,forall\n"
    )

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.parse_annotations()

        # Default semantics is naive, so operators should not affect rewriting behavior,
        # but the parser only applies #operators in set semantics anyway.
        assert rewriter.config.semantics == "naive"
        assert rewriter.config.quantifier1 == "any"
        assert rewriter.config.quantifier2 == "any"
        assert rewriter.config.uncertain_predicates == [
            UncertainPredicate(
                predicate="time",
                arity=1,
                uncertain_position=1,
                rho="10",
                sigma="10",
            ),
            UncertainPredicate(
                predicate="log",
                arity=2,
                uncertain_position=2,
                rho="20",
                sigma="10",
            ),
            UncertainPredicate(
                predicate="meters",
                arity=3,
                uncertain_position=1,
                rho="5",
                sigma="5",
            ),
        ]


def test_parse_annotations_invalid_uncertain_annotation():
    mock_file_data = "#uncertain vessel/2.\n"

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        rewriter = ASPRewriter("file_asp.asp")

        with pytest.raises(ValueError, match="Invalid uncertain annotation"):
            rewriter.parse_annotations()


def test_parse_annotations_operators_ignored_in_naive_semantics():
    mock_file_data = (
        "#naive-based semantics\n"
        "#uncertain log/2, 2.\n"
        "#operators = forall, forall\n"
    )

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.parse_annotations()

        # quantifiers must stay at their defaults
        assert rewriter.config.quantifier1 == "any"
        assert rewriter.config.quantifier2 == "any"

# ---------------------------------------------------------------------------
# get_uncertain_predicate_names
# ---------------------------------------------------------------------------

def test_get_uncertain_predicate_names():
    mock_file_data = (
        "#uncertain log/2, 2.\n"
        "#uncertain time/1, 1.\n"
    )

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.parse_annotations()

        assert rewriter.get_uncertain_predicate_names() == {("log",2), ("time",1)}

# ---------------------------------------------------------------------------
# generate_abstract_rules
# ---------------------------------------------------------------------------

def test_generate_abstract_rules_single_uncertain_set():
    mock_file_data = "#set-based semantics\n#uncertain log/2, 2.\n"

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.parse_annotations()

        assert rewriter.generate_abstract_rules() == [
            "log_r(X1, N) :- log(X1, N1), &split_number_set(N1;N).\n"
        ]


def test_generate_abstract_rules_with_sigma_rho():
    mock_file_data = "#set-based semantics\n#uncertain time/1, 1. rho=10, sigma=10\n"

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.parse_annotations()

        assert rewriter.generate_abstract_rules() == [
            "time_r(N) :- time(N1), &split_number_set(N1,10,10;N).\n"
        ]


def test_generate_abstract_rules_double_uncertain_term():
    mock_file_data = "#uncertain log/2, 2.\n#uncertain log/2, 1.\n"

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.parse_annotations()

        assert rewriter.generate_abstract_rules() == [
            "log_r(N, M) :- log(N1, M1), &split_number_naive(N1;N), &split_number_naive(M1;M).\n"
        ]


def test_generate_abstract_rules_float_branch():
    mock_file_data = "#uncertain vessel/2, 2. rho=0.5, sigma=0.5\n"

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.parse_annotations()

        assert rewriter.generate_abstract_rules() == [
            "vessel_r(X1, N) :- vessel(X1, N1), &split_number_naive(N1,0.5,0.5;N).\n"
        ]


def test_generate_abstract_rules_two_distinct_predicates():
    mock_file_data = (
        "#uncertain log/2, 2.\n"
        "#uncertain time/1, 1.\n"
    )

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.parse_annotations()

        rules = rewriter.generate_abstract_rules()
        assert len(rules) == 2
        assert "log_r(X1, N) :- log(X1, N1), &split_number_naive(N1;N).\n" in rules
        assert "time_r(N) :- time(N1), &split_number_naive(N1;N).\n" in rules


def test_generate_abstract_rules_high_arity_fallback_variable_names():
    """Positions beyond the 8 entries of PARAM_NAMES must use U9, U10, …"""
    # predicate/9 with all 9 positions uncertain
    lines = "\n".join(
        f"#uncertain big/9, {i}." for i in range(1, 10)
    ) + "\n"

    with patch("builtins.open", mock_open(read_data=lines)):
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.parse_annotations()

        rules = rewriter.generate_abstract_rules()
        assert len(rules) == 1
        # The 9th uncertain position must be named U9
        assert "U9" in rules[0]

# ---------------------------------------------------------------------------
# rewrite_program – integration tests
# ---------------------------------------------------------------------------

def test_rewrite_program_correct_insertion_points():
    mock_file_data_input = (
        "log(a,1198).\n"
        "log(b,1204).\n"
        "log(c,1200).\n"
        "#set-based semantics\n"
        "#operators = exists, exists\n"
        "#uncertain log/2, 2.\n"
        "#show suspect/1.\n"
        "#show culprit/1."
    )

    expected_output = [
        "log(a,1198).\n",
        "log(b,1204).\n",
        "log(c,1200).\n",
        "",
        "",
        "",
        "log_r(X1, N) :- log(X1, N1), &split_number_set(N1;N).\n",
        "#show suspect/1.\n",
        "#show culprit/1.",
    ]

    with patch("builtins.open", mock_open(read_data=mock_file_data_input)) as mocked_open:
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.rewrite_program()

        file_handle = mocked_open.return_value
        file_handle.writelines.assert_called_once_with(expected_output)


def test_rewrite_program_comparison_operators_and_uncertain_predicates():
    mock_file_data_input = (
        "log(c,1200).\n"
        "#set-based semantics\n"
        "#operators = exists, exists\n"
        "#uncertain log/2, 2.\n"
        "#uncertain time/1, 1.\n"
        "#show suspect/1.\n"
        "time(X) :- step(Y), X = 1100 + Y*10.\n"
        "inRoom(X,T_1) :- time(T_1), door(X), log(X,T_2), T_2 <= T_1.\n"
    )

    expected_output = [
        "log(c,1200).\n",
        "",
        "",
        "",
        "",
        "log_r(X1, N) :- log(X1, N1), &split_number_set(N1;N).\n",
        "time_r(N) :- time(N1), &split_number_set(N1;N).\n",
        "#show suspect/1.\n",
        "time(X) :- step(Y), X = (1100+(Y*10)).\n",
        "inRoom(X,T_1) :- time_r(T_1), door(X), log_r(X,T_2), &compareset(T_2,T_1,le,any,any).\n",
    ]

    with patch("builtins.open", mock_open(read_data=mock_file_data_input)) as mocked_open:
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.rewrite_program()

        file_handle = mocked_open.return_value
        file_handle.writelines.assert_called_once_with(expected_output)


def test_rewrite_program_double_uncertain_term():
    mock_file_data_input = (
        "log(1100,1200).\n"
        "#uncertain log/2, 2.\n"
        "#uncertain log/2, 1.\n"
        "#show suspect/1.\n"
        "time(X) :- step(Y), X = 1100 + Y*10.\n"
        "inRoom(X,T_1) :- time(T_1), door(X), log(X,T_2), T_2 <= T_1.\n"
    )

    expected_output = [
        "log(1100,1200).\n",
        "",
        "",
        "log_r(N, M) :- log(N1, M1), &split_number_naive(N1;N), &split_number_naive(M1;M).\n",
        "#show suspect/1.\n",
        "time(X) :- step(Y), X = (1100+(Y*10)).\n",
        "inRoom(X,T_1) :- time(T_1), door(X), log_r(X,T_2), T_2 <= T_1.\n",
    ]

    with patch("builtins.open", mock_open(read_data=mock_file_data_input)) as mocked_open:
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.rewrite_program()

        file_handle = mocked_open.return_value
        file_handle.writelines.assert_called_once_with(expected_output)


def test_rewrite_program_float_branch():
    mock_file_data_input = (
        "vessel(a, 415357).\n"
        "#uncertain vessel/2, 2. rho=0.5, sigma=0.5\n"
        "shift(X, NEW_POS) :- vessel(X, POS), NEW_POS = POS+10.\n"
        ":- shift(X, 5000).\n"
        ":- shift(X, 50).\n"
    )

    expected_output = [
        "vessel(a, 415357).\n",
        "",
        "vessel_r(X1, N) :- vessel(X1, N1), &split_number_naive(N1,0.5,0.5;N).\n",
        "shift(X,NEW_POS) :- vessel_r(X,POS), NEW_POS = (POS+10).\n",
        ":- shift(X,5000).\n",
        ":- shift(X,50).\n",
    ]

    with patch("builtins.open", mock_open(read_data=mock_file_data_input)) as mocked_open:
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.rewrite_program()

        file_handle = mocked_open.return_value
        file_handle.writelines.assert_called_once_with(expected_output)


def test_rewrite_program_keeps_original_line_if_parser_fails():
    mock_file_data_input = (
        "#uncertain log/2, 2.\n"
        "this is not valid asp syntax\n"
    )

    expected_output = [
        "",
        "log_r(X1, N) :- log(X1, N1), &split_number_naive(N1;N).\n",
        "this is not valid asp syntax\n",
    ]

    with patch("builtins.open", mock_open(read_data=mock_file_data_input)) as mocked_open:
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.rewrite_program()

        file_handle = mocked_open.return_value
        file_handle.writelines.assert_called_once_with(expected_output)


def test_rewrite_program_exception_handling():
    mock_file_data = "#uncertain log/2, 2.\n"

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        rewriter = ASPRewriter("file_asp.asp")

        with patch.object(rewriter, "parse_annotations", side_effect=Exception("Test exception")):
            with patch("builtins.print") as mock_print:
                with patch("traceback.print_exc") as mock_tb:
                    rewriter.rewrite_program()
                    mock_print.assert_any_call("An error occurred: Test exception")
                    mock_tb.assert_called_once()


def test_rewrite_program_output_file_path():
    """The output file must be named rewritten_<input> in the same directory."""
    mock_file_data = "#uncertain log/2, 2.\n"

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        rewriter = ASPRewriter("file_asp.asp")
        assert rewriter.output_file.endswith("rewritten_file_asp.asp")


def test_rewrite_program_output_file_path_with_directory():
    import os
    mock_file_data = "#uncertain log/2, 2.\n"

    with patch("builtins.open", mock_open(read_data=mock_file_data)):
        rewriter = ASPRewriter("/some/dir/prog.lp")
        expected = os.path.join("/some/dir", "rewritten_prog.lp")
        assert rewriter.output_file == expected


def test_rewrite_program_no_uncertain_predicates():
    mock_file_data_input = (
        "fact(a).\n"
        "rule(X) :- fact(X).\n"
    )

    expected_output = [
        "fact(a).\n",
        "rule(X) :- fact(X).\n",
    ]

    with patch("builtins.open", mock_open(read_data=mock_file_data_input)) as mocked_open:
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.rewrite_program()

        file_handle = mocked_open.return_value
        file_handle.writelines.assert_called_once_with(expected_output)


def test_rewrite_program_empty_input():
    with patch("builtins.open", mock_open(read_data="")) as mocked_open:
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.rewrite_program()

        file_handle = mocked_open.return_value
        file_handle.writelines.assert_called_once_with([])

# ---------------------------------------------------------------------------
# _rewrite_builtin_comparison – unit tests
# ---------------------------------------------------------------------------

def _make_rewriter(mock_data="#uncertain log/2, 2.\n"):
    with patch("builtins.open", mock_open(read_data=mock_data)):
        return ASPRewriter("file_asp.asp")


def test_rewrite_builtin_comparison_assignment_unchanged():
    rewriter = _make_rewriter("#set-based semantics\n#uncertain log/2, 2.\n")
    rewriter.parse_annotations()

    from src.parser.asp_nodes import BuiltinAtom
    builtin = BuiltinAtom(left="X", operator="=", right="1")
    result = rewriter._rewrite_builtin_comparison(builtin)

    assert result is builtin


def test_rewrite_builtin_comparison_known_operator():
    rewriter = _make_rewriter("#set-based semantics\n#uncertain log/2, 2.\n")
    rewriter.parse_annotations()

    from src.parser.asp_nodes import BuiltinAtom, Literal
    builtin = BuiltinAtom(left="T2", operator="<=", right="T1")
    result = rewriter._rewrite_builtin_comparison(builtin)

    assert isinstance(result, Literal)
    assert "&compareset" in str(result)
    assert "le" in str(result)


def test_rewrite_builtin_comparison_unknown_operator():
    rewriter = _make_rewriter("#set-based semantics\n#uncertain log/2, 2.\n")
    rewriter.parse_annotations()

    from src.parser.asp_nodes import BuiltinAtom
    builtin = BuiltinAtom(left="X", operator="??", right="Y")
    result = rewriter._rewrite_builtin_comparison(builtin)

    assert result is builtin


# ---------------------------------------------------------------------------
# Multiple facts on the same line
# ---------------------------------------------------------------------------

def test_rewrite_program_multiple_facts_on_same_line():
    mock_file_data_input = (
        "#uncertain vessel/4, 2.\n"
        "halfLon(228051000, 4). halfLat(228051000, 14).\n"
    )

    expected_output = [
        "",
        "vessel_r(X1, N, X3, X4) :- vessel(X1, N1, X3, X4), &split_number_naive(N1;N).\n",
        "halfLon(228051000,4).\nhalfLat(228051000,14).\n",
    ]

    with patch("builtins.open", mock_open(read_data=mock_file_data_input)) as mocked_open:
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.rewrite_program()

        file_handle = mocked_open.return_value
        file_handle.writelines.assert_called_once_with(expected_output)


def test_rewrite_program_multiple_uncertain_facts_on_same_line():
    mock_file_data_input = (
        "#uncertain vessel/4, 2.\n"
        "vessel(228051000, 38311, 42402, 1443650684). vessel(228017700, 38265, 42375, 1443650684).\n"
    )

    expected_output = [
        "",
        "vessel_r(X1, N, X3, X4) :- vessel(X1, N1, X3, X4), &split_number_naive(N1;N).\n",
        "vessel(228051000,38311,42402,1443650684).\nvessel(228017700,38265,42375,1443650684).\n",
    ]

    with patch("builtins.open", mock_open(read_data=mock_file_data_input)) as mocked_open:
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.rewrite_program()

        file_handle = mocked_open.return_value
        file_handle.writelines.assert_called_once_with(expected_output)


def test_rewrite_program_mixed_facts_on_same_line():
    mock_file_data_input = (
        "#uncertain vessel/4, 2.\n"
        "vessel(228051000, 38311, 42402, 1443650684). halfLon(228051000, 4).\n"
    )

    expected_output = [
        "",
        "vessel_r(X1, N, X3, X4) :- vessel(X1, N1, X3, X4), &split_number_naive(N1;N).\n",
        "vessel(228051000,38311,42402,1443650684).\nhalfLon(228051000,4).\n",
    ]

    with patch("builtins.open", mock_open(read_data=mock_file_data_input)) as mocked_open:
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.rewrite_program()

        file_handle = mocked_open.return_value
        file_handle.writelines.assert_called_once_with(expected_output)


def test_rewrite_program_realistic_multiline_facts():
    mock_file_data_input = (
        "#uncertain vessel/4, 2.\n"
        "vessel(228051000, 38311, 42402, 1443650684).\n"
        "vessel(228017700, 38265, 42375, 1443650684).\n"
        "halfLon(228051000, 4). halfLat(228051000, 14).\n"
        "halfLon(228017700, 5). halfLat(228017700, 22).\n"
    )

    expected_output = [
        "",
        "vessel_r(X1, N, X3, X4) :- vessel(X1, N1, X3, X4), &split_number_naive(N1;N).\n",
        "vessel(228051000,38311,42402,1443650684).\n",
        "vessel(228017700,38265,42375,1443650684).\n",
        "halfLon(228051000,4).\nhalfLat(228051000,14).\n",
        "halfLon(228017700,5).\nhalfLat(228017700,22).\n",
    ]

    with patch("builtins.open", mock_open(read_data=mock_file_data_input)) as mocked_open:
        rewriter = ASPRewriter("file_asp.asp")
        rewriter.rewrite_program()

        file_handle = mocked_open.return_value
        file_handle.writelines.assert_called_once_with(expected_output)


# ---------------------------------------------------------------------------
# Constructor / main
# ---------------------------------------------------------------------------


def test_constructor_invalid_file_extension():
    with pytest.raises(SystemExit, match=r"Please provide a file with a \.lp or \.asp extension\."):
        ASPRewriter("file_asp.txt")


def test_main_no_arguments():
    with patch("sys.argv", ["test_script.py"]):
        with pytest.raises(SystemExit, match="Please provide a filename as an argument."):
            main()


def test_main_calls_rewrite_program():
    with patch("sys.argv", ["test_script.py", "file_asp.asp"]):
        with patch("builtins.open", mock_open(read_data="")):
            with patch.object(ASPRewriter, "rewrite_program") as mock_rewrite:
                main()
                mock_rewrite.assert_called_once()