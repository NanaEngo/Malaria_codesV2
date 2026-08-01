#!/usr/bin/env python3
"""
P5 — GNN architectures (M1.2). PyG-based compact models.

Models (all take Data with x, edge_index, edge_attr, y, plus optional
descriptor tensors attached at batch level):
  GCN, GIN, GAT                 — pure graph
  GIN-FP                        — graph + ECFP4 (2048)
  GIN-TFP                       — graph + TFP (78, topological)  [novel, P3]
  GIN-TNE                       — graph + TNE (192, tensor)      [novel, P3]
  Hybrid-All                    — graph + ECFP4 + TFP + TNE       [Q2]

All models share: 3 conv layers (hidden 128), global mean pool, 1-hidden MLP
head (128), dropout, single logit output. Fusion models concatenate the pooled
graph embedding with (scaled) descriptor vector before the head MLP.

Module-level MODEL_FACTORY maps name -> (build_fn, needs_features).

Usage:
    from p5_models import build_model
    model = build_model("GIN", n_descriptor_features=None, out_dim=1)
    model = build_model("GIN-TFP", n_descriptor_features=78, out_dim=1)
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, GINConv, GATConv, global_mean_pool


class _GraphBase(nn.Module):
    def __init__(self, in_dim: int, hidden: int = 128, out_dim: int = 1,
                 dropout: float = 0.1, edge_dim: int | None = None,
                 n_descriptor_features: int | None = None):
        super().__init__()
        self.hidden = hidden
        self.dropout = dropout
        self.n_desc = n_descriptor_features or 0
        self._build_convs(in_dim, hidden, edge_dim)
        head_in = hidden + self.n_desc
        self.head = nn.Sequential(
            nn.Linear(head_in, hidden), nn.BatchNorm1d(hidden), nn.ReLU(),
            nn.Dropout(dropout), nn.Linear(hidden, out_dim),
        )

    def _build_convs(self, in_dim, hidden, edge_dim):
        raise NotImplementedError

    def conv_out(self, x, edge_index, edge_attr):
        raise NotImplementedError

    def forward(self, x, edge_index, batch, edge_attr=None, desc=None):
        h = self.conv_out(x, edge_index, edge_attr)
        h = global_mean_pool(h, batch)
        if desc is not None:
            h = torch.cat([h, desc], dim=1)
        return self.head(h)


class GCN(_GraphBase):
    def _build_convs(self, in_dim, hidden, edge_dim):
        self.conv1 = GCNConv(in_dim, hidden)
        self.conv2 = GCNConv(hidden, hidden)
        self.conv3 = GCNConv(hidden, hidden)

    def conv_out(self, x, edge_index, edge_attr):
        x = F.relu(self.conv1(x, edge_index))
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = F.relu(self.conv2(x, edge_index))
        x = F.dropout(x, p=self.dropout, training=self.training)
        return self.conv3(x, edge_index)


class GIN(_GraphBase):
    def _build_convs(self, in_dim, hidden, edge_dim):
        def mlp(d_in, d_out):
            return nn.Sequential(nn.Linear(d_in, hidden), nn.BatchNorm1d(hidden),
                                 nn.ReLU(), nn.Linear(hidden, d_out))
        self.conv1 = GINConv(mlp(in_dim, hidden))
        self.conv2 = GINConv(mlp(hidden, hidden))
        self.conv3 = GINConv(mlp(hidden, hidden))

    def conv_out(self, x, edge_index, edge_attr):
        x = F.relu(self.conv1(x, edge_index))
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = F.relu(self.conv2(x, edge_index))
        x = F.dropout(x, p=self.dropout, training=self.training)
        return self.conv3(x, edge_index)


class GAT(_GraphBase):
    def _build_convs(self, in_dim, hidden, edge_dim):
        self.conv1 = GATConv(in_dim, hidden // 4, heads=4, edge_dim=edge_dim)
        self.conv2 = GATConv(hidden, hidden // 4, heads=4, edge_dim=edge_dim)
        self.conv3 = GATConv(hidden, hidden, heads=1, concat=False)

    def conv_out(self, x, edge_index, edge_attr):
        x = F.relu(self.conv1(x, edge_index, edge_attr=edge_attr))
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = F.relu(self.conv2(x, edge_index, edge_attr=edge_attr))
        x = F.dropout(x, p=self.dropout, training=self.training)
        return self.conv3(x, edge_index, edge_attr=edge_attr)


def _make_fusion(cls):
    def factory(**kw):
        return cls(**kw)
    return factory


class GINFP(GIN):
    pass


class GINTFP(GIN):
    pass


class GINTNE(GIN):
    pass


class HybridAll(GIN):
    pass


MODEL_FACTORY = {
    "GCN": {"fn": GCN, "needs_features": False},
    "GIN": {"fn": GIN, "needs_features": False},
    "GAT": {"fn": GAT, "needs_features": True},  # edge_dim used
    "GIN-FP": {"fn": GINFP, "needs_features": True, "n_desc": 2048},
    "GIN-TFP": {"fn": GINTFP, "needs_features": True, "n_desc": 78},
    "GIN-TNE": {"fn": GINTNE, "needs_features": True, "n_desc": 192},
    "Hybrid-All": {"fn": HybridAll, "needs_features": True, "n_desc": 2048 + 78 + 192},
}

FUSION_MODELS = {"GIN-FP", "GIN-TFP", "GIN-TNE", "Hybrid-All"}


def build_model(name: str, in_dim: int, hidden: int = 128, out_dim: int = 1,
                dropout: float = 0.1, edge_dim: int | None = None,
                n_descriptor_features: int | None = None) -> nn.Module:
    spec = MODEL_FACTORY[name]
    cls = spec["fn"]
    if name in FUSION_MODELS:
        if n_descriptor_features is None:
            n_descriptor_features = spec.get("n_desc")
        return cls(in_dim=in_dim, hidden=hidden, out_dim=out_dim,
                   dropout=dropout, edge_dim=edge_dim,
                   n_descriptor_features=n_descriptor_features)
    return cls(in_dim=in_dim, hidden=hidden, out_dim=out_dim,
               dropout=dropout, edge_dim=edge_dim)
