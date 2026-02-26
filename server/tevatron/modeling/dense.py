"""DenseModel + DenseOutput — shim for tevatron.modeling.dense

Implements the same CLS-pooling dense encoder that the original tevatron
DenseModel used, loaded directly via HuggingFace AutoModel.
No tevatron installation required.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import torch
import torch.nn as nn
from transformers import AutoModel, PreTrainedModel


@dataclass
class DenseOutput:
    q_reps: Optional[torch.Tensor] = None
    p_reps: Optional[torch.Tensor] = None


class DenseModel(nn.Module):
    """
    Thin wrapper around a HuggingFace encoder that returns CLS-token
    representations, matching the tevatron DenseModel API used in
    suggest_mesh_terms.py.
    """

    def __init__(self, encoder: PreTrainedModel):
        super().__init__()
        self.encoder = encoder

    # ── loading ──────────────────────────────────────────────────────────────
    @classmethod
    def load(cls, model_name_or_path: str, config, **hf_kwargs) -> "DenseModel":
        encoder = AutoModel.from_pretrained(
            model_name_or_path, config=config, **hf_kwargs
        )
        model = cls(encoder)
        model.eval()
        return model

    # ── forward ──────────────────────────────────────────────────────────────
    def forward(self, query=None, passage=None) -> DenseOutput:
        """
        Called as model(tokenised_dict) — first positional arg is `query`.
        Returns DenseOutput with .q_reps of shape (batch, hidden_dim).
        """
        if query is not None:
            out = self.encoder(**query, return_dict=True)
            q_reps = out.last_hidden_state[:, 0]  # CLS pooling
            return DenseOutput(q_reps=q_reps)

        if passage is not None:
            out = self.encoder(**passage, return_dict=True)
            p_reps = out.last_hidden_state[:, 0]
            return DenseOutput(p_reps=p_reps)

        return DenseOutput()
