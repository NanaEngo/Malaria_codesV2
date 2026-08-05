import json
import re
import sys

def parse_bib(path):
    entries = []
    with open(path, encoding="utf-8") as f:
        content = f.read()
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,]+),", content):
        kind, key = m.group(1).lower(), m.group(2).strip()
        start = m.end()
        depth = 1
        i = start
        while i < len(content) and depth:
            if content[i] == "{":
                depth += 1
            elif content[i] == "}":
                depth -= 1
            i += 1
        body = content[start : i - 1]
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*\{(.*?)\}", body, re.S):
            fields[fm.group(1).lower()] = " ".join(fm.group(2).split())
        entries.append({"key": key, "kind": kind, "fields": fields})
    return entries

def map_type(kind):
    return {
        "article": "journal_article",
        "book": "book",
        "inbook": "chapter",
        "incollection": "chapter",
        "inproceedings": "conference_paper",
        "conference": "conference_paper",
        "dataset": "dataset",
        "software": "software",
        "techreport": "report",
        "misc": "preprint",
        "unpublished": "preprint",
        "phdthesis": "other",
    }.get(kind, "other")

def build(entries):
    sources = []
    for idx, e in enumerate(entries, 1):
        f = e["fields"]
        identifiers = {}
        doi = f.get("doi", "")
        if doi:
            identifiers["doi"] = doi
        for k in ("pmid", "pmcid", "isbn", "url"):
            v = f.get(k, "")
            if v:
                identifiers[k] = v
        if e["kind"] in ("techreport", "misc") and not identifiers.get("url"):
            note = f.get("note", "")
            if "arxiv" in note.lower() or "http" in note:
                m = re.search(r"https?://\S+", note)
                if m:
                    identifiers["url"] = m.group(0).rstrip(".,;}")
        hp = f.get("howpublished", "")
        if not identifiers.get("url") and re.search(r"https?://", hp):
            m = re.search(r"https?://\S+", hp)
            identifiers["url"] = m.group(0).rstrip(".,;}")
        if not identifiers.get("url") and not identifiers.get("doi"):
            for kk in ("eprint", "archiveprefix"):
                pass
            epr = f.get("eprint", "")
            if epr:
                identifiers["url"] = f"https://arxiv.org/abs/{epr}"
        authors = f.get("author", "")
        author_list = [a.strip() for a in re.split(r"\s+and\s+", authors) if a.strip()] if authors else []
        sources.append({
            "evidence_id": f"E{idx:03d}",
            "authors": author_list,
            "title": f.get("title", ""),
            "source_type": map_type(e["kind"]),
            "identifiers": identifiers,
            "confidentiality": "public",
            "locator": "bib entry",
            "verification": {"status": "unverified", "source_opened": False, "verified_by": "", "verified_on": ""},
            "year": None,
        })
    return {"schema_version": "1.0", "sources": sources}

if __name__ == "__main__":
    entries = parse_bib(sys.argv[1])
    print(json.dumps(build(entries), indent=2))
