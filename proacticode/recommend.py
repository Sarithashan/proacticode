"""Phase 3 - explainable, rule-template recommendations.

Every finding is turned into: where it is, which indicator it affects,
why it matters and what to do. Nothing here is applied automatically;
refactor.py applies only the subset that Ruff can fix mechanically.
"""

RUFF_ADVICE = {
    "F401": ("Unused import", "Delete the import; unused imports add noise and hide real dependencies."),
    "F841": ("Unused variable", "Remove the assignment, or use the value; dead variables suggest leftover logic."),
    "E711": ("Comparison to None", "Use `is None` / `is not None`; `==` can call a custom __eq__."),
    "E712": ("Comparison to True/False", "Use the value directly (`if x:`) instead of comparing to a boolean."),
    "E722": ("Bare except", "Catch specific exceptions; a bare except also hides KeyboardInterrupt and real bugs."),
    "B006": ("Mutable default argument", "Default to None and create the list/dict inside the function; defaults are shared across calls."),
    "SIM102": ("Nested if", "Merge nested ifs with `and` to reduce nesting depth."),
    "SIM103": ("Needless bool", "Return the condition directly instead of if/else returning True/False."),
    "SIM108": ("If/else assignment", "Use a conditional expression for a simple assignment."),
    "SIM110": ("Manual any/all", "Replace the loop with any() or all()."),
    "SIM118": ("dict.keys() in loop", "Iterate over the dict directly."),
    "RET505": ("Else after return", "Drop the else; the early return already ends the branch."),
    "PERF401": ("Loop that builds a list", "Use a list comprehension."),
    "C901": ("Function too complex", "Split into smaller helpers and flatten nested conditions with early returns."),
    "PLR0911": ("Too many returns", "Use a lookup table or split the function."),
    "PLR0912": ("Too many branches", "Split the function by responsibility or use a lookup table."),
    "PLR0915": ("Too many statements", "Split the function into smaller steps."),
    "PLR0913": ("Too many arguments", "Group related arguments into an object."),
}

BANDIT_ADVICE = {
    "B101": "assert is removed with -O; do not rely on it for validation.",
    "B105": "Hard-coded password: read secrets from environment variables or a secret store.",
    "B106": "Hard-coded password argument: load it from configuration, not source code.",
    "B107": "Hard-coded password default: remove the default.",
    "B307": "eval() runs arbitrary code; use ast.literal_eval or a real parser.",
    "B324": "MD5/SHA1 are broken for passwords; use hashlib.scrypt/pbkdf2 or the bcrypt/argon2 libraries.",
    "B404": "Importing subprocess is fine, but review every call for injection risks.",
    "B602": "shell=True with a built string allows command injection; pass an argument list and shell=False.",
    "B603": "Check that subprocess arguments are not attacker-controlled.",
    "B608": "Building SQL with string concatenation allows SQL injection; use parameterised queries.",
}

INDICATOR_OF = {"ruff": "warnings", "bandit": "security", "radon": "complexity", "dup": "duplication"}
SEV_ORDER = {"high": 0, "medium": 1, "low": 2}


def _suggest(f):
    if f["source"] == "ruff":
        title, text = RUFF_ADVICE.get(f["code"], ("Style / quality warning", "See the Ruff rule documentation."))
        return title, text
    if f["source"] == "bandit":
        return "Security finding", BANDIT_ADVICE.get(f["code"], "Review this pattern against the Bandit documentation.")
    if f["source"] == "radon":
        return "High complexity", ("Split the function into smaller helpers, flatten nested "
                                   "conditionals with early returns, or replace long if/elif chains with a lookup table.")
    return "Duplicated code", "Extract the repeated block into one helper function and call it from each place."


def recommend(findings):
    """Return recommendation dicts sorted by severity then location."""
    recs = []
    for f in findings:
        title, suggestion = _suggest(f)
        recs.append({
            "file": f["file"], "line": f["line"], "function": f.get("function"),
            "indicator": INDICATOR_OF[f["source"]], "rule": f["code"], "severity": f["severity"],
            "issue": title, "reason": f["message"], "suggestion": suggestion,
            "auto_fixable": bool(f.get("auto_fixable")),
        })
    recs.sort(key=lambda r: (SEV_ORDER.get(r["severity"], 3), r["file"], r["line"]))
    return recs
