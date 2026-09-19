"""Build prompt x01 (phase B, OWL 2 + SHACL-AF arm) from p16 by swapping the Datalog
RULES/FACTS section for the ontology. Everything else (questions, output format) is
byte-identical to p16. The decision header C1-C5 is carried over verbatim as Turtle comments."""
import pathlib, re
here = pathlib.Path(__file__).resolve().parent
root = here.parents[1]
p16 = (root / "prompts/p16-B-datalog.txt").read_text()
head, rest = p16.split("RULES -- the policy as a Datalog program", 1)
rules_part, tail = rest.split("QUESTIONS", 1)
decisions = "\n".join("# " + l.lstrip("%").strip() for l in rules_part.strip().splitlines() if l.startswith("%") and "--" in l)
body = (f"RULES -- the policy as an OWL 2 ontology with SHACL-AF rules (Turtle)\n\n"
        f"# Decisions taken when this ontology was written, one per commitment:\n{decisions}\n\n"
        f"# ---------- schema.ttl ----------\n{(here / 'schema.ttl').read_text()}\n"
        f"# ---------- rules.ttl ----------\n{(here / 'rules.ttl').read_text()}\n"
        f"FACTS\n\n# ---------- data.ttl ----------\n{(here / 'data.ttl').read_text()}\n")
out = root / "prompts/x01-B-owl+shacl.txt"
out.write_text(head + body + "QUESTIONS" + tail)
print(out, len(out.read_text()))
