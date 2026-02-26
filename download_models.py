#!/usr/bin/env python3
"""
Download model files required by MeSH Suggester.

Models:
  1. BERT checkpoint  -- ielabgroup/mesh_term_suggestion_biobert  (HF Hub)
     → server/Model/checkpoint-80000/
  2. PubMed-w2v.bin   -- HF Hub (preferred) OR Google Drive direct file (fallback)
     → server/Model/PubMed-w2v.bin

Run from the repository root:
    python download_models.py
"""

import os
import sys


# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(ROOT_DIR, "server", "Model")
BERT_DEST = os.path.join(MODEL_DIR, "checkpoint-80000")
W2V_DEST = os.path.join(MODEL_DIR, "PubMed-w2v.bin")

# ── Sources ────────────────────────────────────────────────────────────────────
HF_REPO_ID = "ielabgroup/mesh_term_suggestion_biobert"
# Direct Google Drive file ID for PubMed-w2v.bin (fallback)
GDRIVE_FILE_ID = "1nqb-jSsjoqLlLd9glnTS62AwVqiUOFAN"


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


# ── BERT checkpoint ────────────────────────────────────────────────────────────
def download_bert_checkpoint() -> None:
    """Download the fine-tuned BioBERT checkpoint from Hugging Face Hub."""
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("ERROR: huggingface_hub not installed. Run: pip install huggingface_hub>=0.16")
        sys.exit(1)

    _ensure_dir(BERT_DEST)
    print(f"[1/2] Downloading BERT checkpoint from HF Hub ({HF_REPO_ID}) …")
    snapshot_download(
        repo_id=HF_REPO_ID,
        local_dir=BERT_DEST,
        local_dir_use_symlinks=False,   # copy real files, not symlinks to HF cache
        ignore_patterns=["*.gitattributes", "README.md", ".gitattributes"],
    )
    print(f"      ✓ Saved to {BERT_DEST}")


# ── PubMed-w2v.bin ────────────────────────────────────────────────────────────
def download_w2v() -> None:
    """
    Download PubMed-w2v.bin.

    Strategy:
      1. Try HF Hub (fast CDN, works best on HF Spaces) — only if the file
         has been uploaded to the repo.
      2. Fall back to the direct Google Drive file ID via gdown.
    """
    from huggingface_hub import hf_hub_download
    from huggingface_hub.utils import EntryNotFoundError, RepositoryNotFoundError

    _ensure_dir(MODEL_DIR)
    print("[2/2] Downloading PubMed-w2v.bin …")

    # ── attempt 1: HF Hub ──────────────────────────────────────────────────
    try:
        print("      Trying HF Hub …")
        path = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename="PubMed-w2v.bin",
            local_dir=MODEL_DIR,
            local_dir_use_symlinks=False,   # copy real file, not a symlink
        )
        print(f"      ✓ Downloaded from HF Hub → {path}")
        return
    except (EntryNotFoundError, RepositoryNotFoundError):
        print("      Not found on HF Hub — falling back to Google Drive.")
    except Exception as e:
        print(f"      HF Hub attempt failed ({e}) — falling back to Google Drive.")

    # ── attempt 2: Google Drive (direct file ID) ───────────────────────────
    try:
        import gdown
    except ImportError:
        print("ERROR: gdown not installed. Run: pip install gdown>=4.7")
        sys.exit(1)

    print("      Downloading from Google Drive (this may take a while) …")
    result = gdown.download(
        id=GDRIVE_FILE_ID,
        output=W2V_DEST,
        quiet=False,
        fuzzy=True,      # handles Google's virus-scan redirect for large files
    )
    if not result or not os.path.exists(W2V_DEST):
        print("ERROR: gdown download failed.")
        print(f"       Download manually: https://drive.google.com/file/d/{GDRIVE_FILE_ID}/view")
        sys.exit(1)

    print(f"      ✓ Saved to {W2V_DEST}")


# ── Entry point ────────────────────────────────────────────────────────────────
def main() -> None:
    _ensure_dir(MODEL_DIR)

    # 1. BERT checkpoint
    bert_marker = os.path.join(BERT_DEST, "pytorch_model.bin")
    if os.path.exists(bert_marker):
        print(f"[1/2] BERT checkpoint already present — skipping.")
    else:
        download_bert_checkpoint()

    # 2. PubMed word2vec
    if os.path.exists(W2V_DEST):
        print(f"[2/2] PubMed-w2v.bin already present — skipping.")
    else:
        download_w2v()

    print("\n✅ All models ready.")
    print(f"   {BERT_DEST}")
    print(f"   {W2V_DEST}")


if __name__ == "__main__":
    main()
