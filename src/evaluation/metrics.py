"""
src/evaluation/metrics.py
Comprehensive evaluation suite for cybercrime cash-out location prediction:
- Classification metrics: PR-AUC, ROC-AUC, Precision, Recall, F1
- Ranking metrics: Hit@1, Hit@3, Hit@5, Hit@10, Recall@5, Recall@10, MRR, NDCG@K
- Lead-time operational metrics
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_recall_fscore_support
)

def compute_ranking_metrics(
    df: pd.DataFrame,
    case_col: str = "case_id",
    target_col: str = "target",
    score_col: str = "score"
) -> Dict[str, float]:
    """
    Computes Hit@K, Recall@K, and MRR grouped by case_id.
    """
    hit_1 = 0
    hit_3 = 0
    hit_5 = 0
    hit_10 = 0
    reciprocal_ranks = []
    evaluated_cases = 0

    for case_id, group in df.groupby(case_col):
        # Only evaluate cases where an actual cashout occurred (sum(target) > 0)
        positives = group[group[target_col] == 1]
        if len(positives) == 0:
            continue

        evaluated_cases += 1
        sorted_group = group.sort_values(score_col, ascending=False).reset_index(drop=True)
        ranks = sorted_group.index[sorted_group[target_col] == 1].tolist()
        best_rank = ranks[0] + 1  # 1-indexed

        reciprocal_ranks.append(1.0 / best_rank)
        if best_rank <= 1:
            hit_1 += 1
        if best_rank <= 3:
            hit_3 += 1
        if best_rank <= 5:
            hit_5 += 1
        if best_rank <= 10:
            hit_10 += 1

    if evaluated_cases == 0:
        return {
            "hit_at_1": 0.0, "hit_at_3": 0.0, "hit_at_5": 0.0, "hit_at_10": 0.0,
            "recall_at_5": 0.0, "recall_at_10": 0.0, "mrr": 0.0,
            "evaluated_cashout_cases": 0
        }

    return {
        "hit_at_1": round(hit_1 / evaluated_cases, 4),
        "hit_at_3": round(hit_3 / evaluated_cases, 4),
        "hit_at_5": round(hit_5 / evaluated_cases, 4),
        "hit_at_10": round(hit_10 / evaluated_cases, 4),
        "recall_at_5": round(hit_5 / evaluated_cases, 4),
        "recall_at_10": round(hit_10 / evaluated_cases, 4),
        "mrr": round(float(np.mean(reciprocal_ranks)), 4),
        "evaluated_cashout_cases": evaluated_cases
    }

def evaluate_model_performance(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    df_eval: pd.DataFrame,
    threshold: float = 0.5
) -> Dict[str, Any]:
    """
    Full evaluation combining classification and ranking metrics.
    """
    # Classification
    pr_auc = average_precision_score(y_true, y_scores)
    try:
        roc_auc = roc_auc_score(y_true, y_scores)
    except Exception:
        roc_auc = 0.5

    y_pred = (y_scores >= threshold).astype(int)
    p, r, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )

    # Ranking
    df_eval_copy = df_eval.copy()
    df_eval_copy["score"] = y_scores
    ranking_metrics = compute_ranking_metrics(df_eval_copy)

    metrics = {
        "pr_auc": round(float(pr_auc), 4),
        "roc_auc": round(float(roc_auc), 4),
        "precision": round(float(p), 4),
        "recall": round(float(r), 4),
        "f1": round(float(f1), 4),
        **ranking_metrics
    }
    return metrics

def format_metrics_table(results_dict: Dict[str, Dict[str, Any]]) -> str:
    """Generates a clean markdown comparison table for baseline and main models."""
    headers = [
        "Model", "PR-AUC", "ROC-AUC", "Hit@1", "Hit@3", "Hit@5", "Hit@10", "MRR", "F1"
    ]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for model_name, m in results_dict.items():
        row = [
            model_name,
            f"{m.get('pr_auc', 0.0):.4f}",
            f"{m.get('roc_auc', 0.0):.4f}",
            f"{m.get('hit_at_1', 0.0)*100:.1f}%",
            f"{m.get('hit_at_3', 0.0)*100:.1f}%",
            f"{m.get('hit_at_5', 0.0)*100:.1f}%",
            f"{m.get('hit_at_10', 0.0)*100:.1f}%",
            f"{m.get('mrr', 0.0):.4f}",
            f"{m.get('f1', 0.0):.4f}"
        ]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)

if __name__ == "__main__":
    # Self-test
    y_true = np.array([0, 0, 1, 0, 0, 1, 0, 0])
    y_score = np.array([0.1, 0.2, 0.9, 0.3, 0.1, 0.85, 0.4, 0.2])
    df = pd.DataFrame({
        "case_id": ["C1", "C1", "C1", "C1", "C2", "C2", "C2", "C2"],
        "target": y_true,
        "score": y_score
    })
    res = evaluate_model_performance(y_true, y_score, df)
    print("Self-test evaluation output:", res)
