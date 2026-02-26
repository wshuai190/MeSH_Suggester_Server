"""
MeSH Term Suggester — Gradio Application
=========================================
Run:  python app.py
      python app.py --port 7861 --share
"""

from __future__ import annotations

import os
import sys

# ── Path / cwd setup ──────────────────────────────────────────────────────────
# suggest_mesh_terms.py resolves model paths relative to os.getcwd(), so we
# must be inside server/ before importing it.
APP_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_DIR = os.path.join(APP_DIR, "server")
sys.path.insert(0, SERVER_DIR)
os.chdir(SERVER_DIR)

import gradio as gr

# ── Model loading ─────────────────────────────────────────────────────────────
_model_loaded = False
_model_error: str | None = None
_mesh_dict = _model = _tokenizer = _retriever = _look_up = _model_w2v = None

try:
    from suggest_mesh_terms import Suggest_MeSH_Terms_With_BERT, prepare_model
    from suggest_with_other import ATM_MeSH_Suggestion
    from query_parser import parse_boolean_query

    print("Loading models …", flush=True)
    _mesh_dict, _model, _tokenizer, _retriever, _look_up, _model_w2v = prepare_model()
    _model_loaded = True
    print("Models loaded successfully.", flush=True)
except Exception as _e:
    _model_error = str(_e)
    print(f"Warning: could not load BERT models — {_e}", flush=True)
    try:
        from suggest_with_other import ATM_MeSH_Suggestion
        from query_parser import parse_boolean_query
    except Exception as _e2:
        print(f"Error importing server modules: {_e2}", flush=True)

# ── Colour palette ────────────────────────────────────────────────────────────
_COLORS = [
    "#2563eb", "#16a34a", "#9333ea", "#ea580c",
    "#0891b2", "#db2777", "#7c3aed", "#0d9488",
    "#65a30d", "#ca8a04",
]


# ── Query parsing ─────────────────────────────────────────────────────────────
def _parse_query(text: str):
    if not text or not text.strip():
        return [], _empty_groups_html()

    groups = parse_boolean_query(text)
    if not groups:
        return [], (
            "<p style='margin:8px 0;color:#6b7280;font-size:14px'>"
            "No groups detected — try using AND / OR operators "
            "or enter comma-separated keywords.</p>"
        )

    html = "<div style='display:flex;flex-wrap:wrap;gap:10px;padding:4px 0'>"
    for i, group in enumerate(groups):
        c = _COLORS[i % len(_COLORS)]
        badges = "".join(
            f"<span style='"
            f"background:{c};color:#fff;"
            f"padding:3px 11px;border-radius:999px;"
            f"font-size:13px;font-weight:500;white-space:nowrap"
            f"'>{t}</span>"
            for t in group
        )
        html += (
            f"<div style='"
            f"background:#f8fafc;border:1px solid #e2e8f0;"
            f"border-left:3px solid {c};"
            f"border-radius:8px;padding:10px 14px;"
            f"min-width:160px'>"
            f"<div style='font-size:10px;font-weight:700;color:{c};"
            f"text-transform:uppercase;letter-spacing:.6px;"
            f"margin-bottom:7px'>Group {i + 1}</div>"
            f"<div style='display:flex;flex-wrap:wrap;gap:5px'>{badges}</div>"
            f"</div>"
        )
    html += "</div>"
    return groups, html


def _empty_groups_html():
    return (
        "<p style='margin:6px 0;color:#9ca3af;font-size:14px;font-style:italic'>"
        "Parsed keyword groups will appear here.</p>"
    )


# ── MeSH suggestion ───────────────────────────────────────────────────────────
def _suggest(groups: list, method: str):
    if not groups:
        return _placeholder_results(), []

    bert_methods = {"Semantic-BERT", "Fragment-BERT", "Atomic-BERT"}
    if method in bert_methods and not _model_loaded:
        msg = _model_error or "Model files not found."
        return (
            f"<div style='"
            f"padding:14px 18px;background:#fefce8;border:1px solid #fde047;"
            f"border-radius:10px;color:#854d0e;font-size:14px'>"
            f"<b>⚠ BERT models not loaded</b> — {msg}<br/>"
            f"<span style='font-size:13px'>Run <code>python download_models.py</code> "
            f"or switch to the <b>ATM</b> method.</span></div>",
            [],
        )

    type_map = {
        "Semantic-BERT": "Semantic",
        "Fragment-BERT": "Fragment",
        "Atomic-BERT": "Atomic",
        "ATM": "ATM",
    }
    mesh_type = type_map[method]
    all_results: list[dict] = []
    all_checkboxes: list[tuple[str, str]] = []

    try:
        for i, group in enumerate(groups):
            if mesh_type == "ATM":
                params = {"payload": {"Keywords": group, "Type": "ATM"}}
                suggestions = ATM_MeSH_Suggestion(params).suggest()
                terms: list[str] = []
                seen: set[str] = set()
                for item in suggestions:
                    for t in item.get("MeSH_Terms", {}).values():
                        if t not in seen:
                            seen.add(t)
                            terms.append(t)
            else:
                params = {
                    "payload": {"Keywords": group, "Type": mesh_type},
                    "mesh_dict": _mesh_dict,
                    "model": _model,
                    "tokenizer": _tokenizer,
                    "retriever": _retriever,
                    "look_up": _look_up,
                    "model_w2v": _model_w2v,
                }
                raw = Suggest_MeSH_Terms_With_BERT(params).suggest()
                terms = []
                seen = set()
                for r in raw:
                    for t in r.get("MeSH_Terms", {}).values():
                        if t not in seen:
                            seen.add(t)
                            terms.append(t)

            for t in terms:
                label = f"[G{i + 1}]  {t}"
                all_checkboxes.append((label, f"{i}::{t}"))
            all_results.append({"group_idx": i, "keywords": group, "terms": terms})

    except Exception as exc:
        return (
            f"<div style='"
            f"padding:14px 18px;background:#fef2f2;border:1px solid #fca5a5;"
            f"border-radius:10px;color:#991b1b;font-size:14px'>"
            f"❌ <b>Error:</b> {exc}</div>",
            [],
        )

    cards_html = _build_cards(all_results, groups)
    choices = [c[0] for c in all_checkboxes]
    return cards_html, gr.update(choices=choices, value=[]), all_checkboxes


def _build_cards(results: list[dict], groups: list[list[str]]) -> str:
    if not results:
        return _placeholder_results()

    html = "<div style='display:flex;flex-wrap:wrap;gap:14px;padding:4px 0'>"
    for r in results:
        i = r["group_idx"]
        c = _COLORS[i % len(_COLORS)]
        kw_chips = "".join(
            f"<span style='"
            f"background:{c}18;color:{c};"
            f"padding:2px 9px;border-radius:999px;font-size:12px;font-weight:600"
            f"'>{k}</span> "
            for k in r["keywords"]
        )
        if r["terms"]:
            rows = "".join(
                f"<div style='"
                f"padding:4px 0;border-bottom:1px solid #f1f5f9;"
                f"font-size:13px;color:#334155'>"
                f"<span style='color:{c};margin-right:6px'>▸</span>{t}</div>"
                for t in r["terms"]
            )
        else:
            rows = (
                "<div style='color:#94a3b8;font-size:13px;font-style:italic'>"
                "No terms found.</div>"
            )

        html += (
            f"<div style='"
            f"flex:1;min-width:200px;max-width:340px;"
            f"background:#fff;border-radius:10px;"
            f"border:1px solid #e2e8f0;border-top:3px solid {c};"
            f"padding:16px;box-shadow:0 1px 4px rgba(0,0,0,.06)'>"
            f"<div style='font-size:10px;font-weight:700;color:{c};"
            f"text-transform:uppercase;letter-spacing:.6px;"
            f"margin-bottom:8px'>Group {i + 1}</div>"
            f"<div style='display:flex;flex-wrap:wrap;gap:4px;"
            f"margin-bottom:10px'>{kw_chips}</div>"
            f"<hr style='border:none;border-top:1px solid #f1f5f9;margin:8px 0'/>"
            f"{rows}"
            f"</div>"
        )
    html += "</div>"
    return html


def _placeholder_results():
    return (
        "<p style='margin:6px 0;color:#9ca3af;font-size:14px;font-style:italic'>"
        "Suggested MeSH terms will appear here.</p>"
    )


# ── Query builder ─────────────────────────────────────────────────────────────
def _add_terms(
    selected: list[str],
    cb_state: list[tuple[str, str]],
    current: str,
) -> str:
    if not selected:
        return current or ""

    label_to_enc = {lbl: enc for lbl, enc in cb_state}
    by_group: dict[str, list[str]] = {}
    for lbl in selected:
        enc = label_to_enc.get(lbl)
        if enc and "::" in enc:
            grp, term = enc.split("::", 1)
            by_group.setdefault(grp, []).append(term)

    fragments: list[str] = []
    for grp in sorted(by_group, key=int):
        ts = by_group[grp]
        if len(ts) == 1:
            frag = f'"{ts[0]}"[MeSH Terms]'
        else:
            inner = " OR ".join(f'"{t}"[MeSH Terms]' for t in ts)
            frag = f"({inner})"
        fragments.append(frag)

    new_part = " AND ".join(fragments)
    base = (current or "").strip()
    return f"{base} AND {new_part}" if base else new_part


def _clear():
    return (
        "",                              # query_input
        [],                              # groups_state
        _empty_groups_html(),            # groups_html
        _placeholder_results(),          # results_html
        gr.update(choices=[], value=[]), # results_checkboxes
        [],                              # checkboxes_state
        "",                              # query_builder
    )


# ── Theme & CSS ───────────────────────────────────────────────────────────────
_theme = gr.themes.Soft(
    primary_hue="blue",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "sans-serif"],
)

_CSS = """
/* ── header ── */
.mesh-header {
    background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 100%);
    color: #fff;
    padding: 20px 28px;
    border-radius: 12px;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.mesh-header h1  { margin:0; font-size:24px; font-weight:700; letter-spacing:-.4px; }
.mesh-header p   { margin:4px 0 0; font-size:13px; opacity:.8; }
.mesh-header .tag {
    background: rgba(255,255,255,.18);
    padding: 5px 13px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: .4px;
    white-space: nowrap;
}
/* ── step labels ── */
.step-label {
    display: inline-block;
    background: #1d4ed8;
    color: #fff;
    font-size: 11px;
    font-weight: 700;
    padding: 2px 9px;
    border-radius: 999px;
    margin-bottom: 6px;
    letter-spacing: .4px;
}
/* hide the default Gradio label on components we label manually */
.no-label > label > span { display: none !important; }
"""

# ── App ───────────────────────────────────────────────────────────────────────
_METHODS = ["Semantic-BERT", "Fragment-BERT", "Atomic-BERT", "ATM"]

with gr.Blocks(theme=_theme, css=_CSS, title="MeSH Term Suggester") as demo:

    # Header
    gr.HTML("""
    <div class="mesh-header">
      <div>
        <h1>🔬 MeSH Term Suggester</h1>
        <p>AI-powered MeSH term suggestion for systematic review boolean queries</p>
      </div>
      <span class="tag">ielab · UQ</span>
    </div>
    """)

    if not _model_loaded:
        gr.HTML(
            f"<div style='padding:12px 16px;background:#fefce8;"
            f"border:1px solid #fde047;border-radius:10px;"
            f"color:#854d0e;font-size:13px;margin-bottom:4px'>"
            f"⚠ <b>BERT models not loaded</b>"
            f"{' — ' + _model_error if _model_error else ''}. "
            f"Run <code>python download_models.py</code> to download them. "
            f"<b>ATM</b> still works without local models.</div>"
        )

    # State
    groups_state = gr.State([])
    checkboxes_state = gr.State([])

    # ── Step 1 ────────────────────────────────────────────────────────────────
    gr.HTML("<div class='step-label'>STEP 1 — ENTER QUERY</div>")
    query_input = gr.Textbox(
        label="Boolean query or keywords",
        placeholder=(
            '("diabetes mellitus" OR insulin) AND ("heart attack" OR "myocardial infarction")\n'
            'or plain keywords: diabetes, insulin, heart attack'
        ),
        lines=3,
        max_lines=8,
    )
    parse_btn = gr.Button("🔍  Parse Query", variant="secondary", size="lg")

    gr.HTML("<div style='margin-top:14px'></div>")
    groups_html = gr.HTML(value=_empty_groups_html(), label="Detected keyword groups")

    # ── Step 2 ────────────────────────────────────────────────────────────────
    gr.HTML("<div class='step-label' style='margin-top:20px'>STEP 2 — SUGGEST MeSH TERMS</div>")
    with gr.Row(equal_height=True):
        method_dropdown = gr.Dropdown(
            choices=_METHODS,
            value="Semantic-BERT",
            label="Suggestion method",
            scale=3,
        )
        suggest_btn = gr.Button("✨  Suggest MeSH Terms", variant="primary", scale=1, size="lg")

    gr.HTML("<div style='margin-top:14px'></div>")
    results_html = gr.HTML(value=_placeholder_results(), label="Results")

    results_checkboxes = gr.CheckboxGroup(
        choices=[],
        value=[],
        label="Select terms to add to query builder",
    )
    add_btn = gr.Button("➕  Add selected to Query Builder", variant="secondary")

    # ── Step 3 ────────────────────────────────────────────────────────────────
    gr.HTML("<div class='step-label' style='margin-top:20px'>STEP 3 — QUERY BUILDER</div>")
    query_builder = gr.Textbox(
        label="MeSH query",
        placeholder='Selected MeSH terms will be assembled here. You can also type directly.',
        lines=3,
        interactive=True,
    )
    clear_btn = gr.Button("🗑  Clear all", variant="stop", size="sm")

    # ── Callbacks ─────────────────────────────────────────────────────────────
    parse_btn.click(
        fn=_parse_query,
        inputs=[query_input],
        outputs=[groups_state, groups_html],
    )

    suggest_btn.click(
        fn=_suggest,
        inputs=[groups_state, method_dropdown],
        outputs=[results_html, results_checkboxes, checkboxes_state],
    )

    add_btn.click(
        fn=_add_terms,
        inputs=[results_checkboxes, checkboxes_state, query_builder],
        outputs=[query_builder],
    )

    clear_btn.click(
        fn=_clear,
        inputs=[],
        outputs=[
            query_input, groups_state, groups_html,
            results_html, results_checkboxes, checkboxes_state, query_builder,
        ],
    )

# ── Launch ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MeSH Term Suggester")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument(
        "--port", type=int,
        default=int(os.environ.get("GRADIO_SERVER_PORT", 7860)),
    )
    parser.add_argument("--share", action="store_true")
    args = parser.parse_args()

    demo.launch(server_name=args.host, server_port=args.port, share=args.share)
