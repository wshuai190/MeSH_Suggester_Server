---
title: MeSH Suggester
emoji: 🔬
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# MeSH Term Suggester

AI-powered MeSH term suggestion for systematic review boolean query construction.
Built with **Gradio** (pure Python — no Node/npm required).

---

## Quick Start (local, pip)

```bash
# 1. Create environment
conda create --prefix ./envs python=3.9
conda activate ./envs

# 2. Install dependencies
pip install -r requirement.txt

# 3. Install tevatron (Dense retrieval library)
git clone https://github.com/texttron/tevatron
pip install -e tevatron/

# 4. Download model files  (~433 MB BERT + PubMed-w2v.bin)
python download_models.py

# 5. Launch the app
python app.py
# → open http://localhost:7860
```

---

## Quick Start (Docker)

```bash
# First run — builds image and downloads models into a named volume (~2 GB, once only)
docker compose up --build

# → open http://localhost:7860
```

After the first run, models are stored in a Docker named volume (`mesh_models`).
**Code changes** don't require a rebuild — just:

```bash
docker compose restart
```

**Dependency changes** (`requirement.txt`) do need a rebuild, but models are still
in the named volume so they won't be re-downloaded.

---

## Model files

| File | Source | Destination |
|------|--------|-------------|
| BERT checkpoint | [ielabgroup/mesh_term_suggestion_biobert](https://huggingface.co/ielabgroup/mesh_term_suggestion_biobert) | `server/Model/checkpoint-80000/` |
| PubMed-w2v.bin | [Google Drive](https://drive.google.com/drive/folders/1VF5yeYgHnFtaspWGZNAsUIp-kQyHUzsI) | `server/Model/PubMed-w2v.bin` |

`download_models.py` handles both automatically.

---

## Hugging Face Spaces deployment

HF Spaces has no persistent volumes, so models must be baked into the image.

```bash
# Push to your Space remote (HF Spaces uses git)
git remote add space https://huggingface.co/spaces/ielabgroup/mesh-suggester
git push space main
```

HF Spaces will build the Dockerfile with `BAKE_MODELS=true` (set this in Space settings
under **Secrets / Variables** → add `BAKE_MODELS=true` as a build argument, or pass it
via the Dockerfile default). Models are downloaded once at build time and baked in.

Alternatively, add this to your Space's `README.md` build config:
```
build_args:
  BAKE_MODELS: "true"
```

---

## Suggestion methods

| Method | Description |
|--------|-------------|
| **Semantic-BERT** | Groups semantically similar keywords via word2vec, then queries the BERT retriever per group |
| **Fragment-BERT** | Treats all keywords as a single query fragment |
| **Atomic-BERT** | Runs the BERT retriever independently for each keyword |
| **ATM** | Uses the NCBI Entrez API (no local model required) |

---

## Use of UMLS and MetaMAP (optional)

To use UMLS or MetaMAP suggestion, you need to deploy the respective services locally.
See [elastic-umls](https://github.com/ielab/elastic-umls) and the
[MetaMAP installation guide](https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/documentation/Installation.html).

---

## Citing

If you use MeSH Suggester in your research, please cite:

```bibtex
@inproceedings{wang2023mesh,
  title={Mesh Suggester: A Library and System for Mesh Term Suggestion for Systematic Review Boolean Query Construction},
  author={Wang, Shuai and Li, Hang and Zuccon, Guido},
  booktitle={Proceedings of the Sixteenth ACM International Conference on Web Search and Data Mining},
  pages={1176--1179},
  year={2023}
}
```

---

## License

[![CC BY-NC-ND 4.0][cc-by-nc-nd-shield]][cc-by-nc-nd]

This work is licensed under a
[Creative Commons Attribution-NonCommercial-NoDerivs 4.0 International License][cc-by-nc-nd].

[![CC BY-NC-ND 4.0][cc-by-nc-nd-image]][cc-by-nc-nd]

[cc-by-nc-nd]: http://creativecommons.org/licenses/by-nc-nd/4.0/
[cc-by-nc-nd-image]: https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png
[cc-by-nc-nd-shield]: https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg
