"""Read mode: the layer's material in context, one question per call, a typed JSON answer.

The prompt names the five statuses but never the layers: a model at L0 is not told that more
material exists, only that it must not answer beyond what it was given.
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
import sys; sys.path.insert(0, str(ROOT))
from render.common import material_dir      # noqa: E402
FILES = {"text": "text.md", "structured": "structured.yaml", "formal": "formal.pl"}
STATUSES = ("ANSWER", "AMBIGUOUS", "CONFLICT", "UNDERDETERMINED", "OUT_OF_SCOPE")
ALIASES = {"UNDETERMINED": "UNDERDETERMINED"}     # unambiguous misspellings seen in replies; counted by score.py
TYPE_HINT = {
    "bool": "true or false",
    "int": "a single integer",
    "sym": "a single identifier or value, as it appears in the material",
    "set": "a list of identifiers (possibly empty), as they appear in the material",
}
FORMAT_NOTE = {
    "text": "The material is a set of Markdown tables, one per kind of record.",
    "structured": "The material is a YAML document with one entry per kind of record.",
    "formal": "The material is a Prolog program: schema facts, then one predicate per kind of record. "
              "Dates in it are integers YYYYMMDD; questions write them as YYYY-MM-DD.",
}
# Added from L1 on; the L0 notes above stay as they were for the M2 run.
RULES_NOTE = {
    "text": " After the tables come the terms, the definitions (each with a rule id) and the questions of interpretation.",
    "structured": " After the relations come the concepts, the rules (each with an id) and the questions of interpretation.",
    "formal": " After the facts come the concept, fork and rule facts and the clauses of the derived predicates.",
}

INSTRUCTIONS = """You answer questions about the records of a procurement organisation, using only the material below.
{format_note}

Answer from the material alone. Do not rely on outside knowledge or usual business practice, and do not
assume definitions, rules or data that the material does not give. Classify your answer with one status:

- ANSWER: the material settles the question. Give the value.
- AMBIGUOUS: the question has more than one reading that the material allows, and the readings give
  different answers. Give each reading and its value.
- CONFLICT: the material contradicts itself on this question and nothing in it says which side prevails.
- UNDERDETERMINED: the question is about something the material covers, but answering needs a definition,
  rule or data that the material does not give. Say what is missing.
- OUT_OF_SCOPE: the question is about something the material has no notion of at all.

{assume_note}Think as long as you need, then end your reply with one line holding a JSON object, and nothing after it:
{{"status": "<one of the five>", "value": <the answer, or null>, "readings": {{"<reading>": <value>}} or null, "missing": "<what is missing>" or null{assume_field}}}

<material>
{material}
</material>"""

# Prompt variants. base: the M2 prompt, unchanged. assume: the same, plus a required assumptions list,
# to see whether answers that go beyond the material state what they assumed.
PROMPTS = {
    "base": {"assume_note": "", "assume_field": ""},
    "assume": {"assume_note": "Whatever the status, list in assumptions every assumption your reply depends on that the material\n"
                              "does not state: a reading of a term, a definition, a rule or a fact. The list is required; leave it\n"
                              "empty only if the reply follows from the material alone.\n\n",
               "assume_field": ', "assumptions": ["<assumption>", ...]'},
}

QUESTION = """Question: {text}
Expected value if the status is ANSWER: {hint}."""


def material(world_dir, layer, rep, cfg="decided"):
    return (pathlib.Path(world_dir) / material_dir(layer, cfg) / FILES[rep]).read_text()


def messages(world_dir, layer, rep, q, cfg="decided", prompt="base"):
    note = FORMAT_NOTE[rep] + (RULES_NOTE[rep] if layer >= 1 else "")
    sys_ = INSTRUCTIONS.format(format_note=note, material=material(world_dir, layer, rep, cfg).rstrip(), **PROMPTS[prompt])
    return [{"role": "system", "content": sys_},
            {"role": "user", "content": QUESTION.format(text=q["text"], hint=TYPE_HINT[q["type"]])}]


# ---------- parsing ----------
def _last_json(text):
    """The last top-level JSON object in text that has a status field."""
    for m in reversed(list(re.finditer(r"\{", text))):
        s, depth, inq, esc = m.start(), 0, False, False
        for i in range(s, len(text)):
            ch = text[i]
            if inq:
                esc = (ch == "\\") and not esc
                if ch == '"' and not esc:
                    inq = False
                continue
            if ch == '"':
                inq = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        o = json.loads(text[s:i + 1])
                    except json.JSONDecodeError:
                        break
                    if isinstance(o, dict) and "status" in o:
                        return o
                    break
    return None


def norm_value(v, typ):
    """Coerce a model value to the key's type; None if it cannot be."""
    if v is None:
        return None
    if typ == "bool":
        if isinstance(v, bool):
            return v
        s = str(v).strip().lower()
        return True if s in ("true", "yes") else False if s in ("false", "no") else None
    if typ == "int":
        if isinstance(v, bool):
            return None
        if isinstance(v, (int, float)):
            return int(v) if float(v).is_integer() else None
        s = re.sub(r"[,_\s€$]", "", str(v))
        return int(s) if re.fullmatch(r"-?\d+", s) else None
    if typ == "sym":
        if isinstance(v, list) and len(v) == 1:
            v = v[0]
        return str(v).strip().strip("`'\"").lower() if not isinstance(v, (list, dict)) else None
    if typ == "set":
        if isinstance(v, str):
            v = [x for x in re.split(r"[,\s]+", v) if x]
        if not isinstance(v, list):
            return None
        return sorted({str(x).strip().strip("`'\"").lower() for x in v})
    return None


def parse(content, typ):
    o = _last_json(content)
    if o is None:
        return {"status": None, "value": None, "alias": False, "parse_error": "no JSON object with a status field"}
    st = str(o.get("status", "")).strip().upper().replace(" ", "_")
    alias = st in ALIASES
    st = ALIASES.get(st, st)
    out = {"alias": alias, "status": st if st in STATUSES else None, "value": None, "readings": o.get("readings"),
           "missing": o.get("missing"), "parse_error": None if st in STATUSES else f"unknown status {st!r}"}
    if "assumptions" in o:      # assume prompt: None = field absent, [] = stated as none
        a = o["assumptions"]
        out["assumptions"] = [str(x) for x in a if str(x).strip()] if isinstance(a, list) else ([str(a)] if a else [])
    if st == "AMBIGUOUS" and isinstance(o.get("readings"), dict):
        out["reading_values"] = sorted({json.dumps(norm_value(v, typ)) for v in o["readings"].values()})
    if st == "ANSWER":
        out["value"] = norm_value(o.get("value"), typ)
        if out["value"] is None:
            out["parse_error"] = f"value {o.get('value')!r} is not a {typ}"
    return out
