"""
src/evaluation/metrics.py
Comprehensive evaluation suite for cybercrime cash-out location prediction:
- Classification metrics: PR-AUC, ROC-AUC, Precision, Recall, F1
- Ranking metrics: Hit@1, Hit@3, Hit@5, Hit@10, Recall@3, Recall@5, Recall@10, MRR, NDCG@3, NDCG@5, NDCG@10
- Candidate generator coverage
- Lead-time operational metrics
"""

import os
import sys
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
    Computes Hit@K, Recall@K, MRR, and NDCG@K grouped by case_id.
    """
    hit_1 = 0
    hit_3 = 0
    hit_5 = 0
    hit_10 = 0
    ndcg_3_list = []
    ndcg_5_list = []
    ndcg_10_list = []
    reciprocal_ranks = []
    evaluated_cases = 0

    for case_id, group in df.groupby(case_col, sort=False):
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
            ndcg_3_list.append(1.0 / np.log2(best_rank + 1))
        else:
            ndcg_3_list.append(0.0)

        if best_rank <= 5:
            hit_5 += 1
            ndcg_5_list.append(1.0 / np.log2(best_rank + 1))
        else:
            ndcg_5_list.append(0.0)

        if best_rank <= 10:
            hit_10 += 1
            ndcg_10_list.append(1.0 / np.log2(best_rank + 1))
        else:
            ndcg_10_list.append(0.0)

    if evaluated_cases == 0:
        return {
            "hit_at_1": 0.0, "hit_at_3": 0.0, "hit_at_5": 0.0, "hit_at_10": 0.0,
            "recall_at_3": 0.0, "recall_at_5": 0.0, "recall_at_10": 0.0,
            "mrr": 0.0, "ndcg_at_3": 0.0, "ndcg_at_5": 0.0, "ndcg_at_10": 0.0,
            "evaluated_cashout_cases": 0
        }

    return {
        "hit_at_1": round(hit_1 / evaluated_cases, 4),
        "hit_at_3": round(hit_3 / evaluated_cases, 4),
        "hit_at_5": round(hit_5 / evaluated_cases, 4),
        "hit_at_10": round(hit_10 / evaluated_cases, 4),
        "recall_at_3": round(hit_3 / evaluated_cases, 4),
        "recall_at_5": round(hit_5 / evaluated_cases, 4),
        "recall_at_10": round(hit_10 / evaluated_cases, 4),
        "mrr": round(float(np.mean(reciprocal_ranks)), 4),
        "ndcg_at_3": round(float(np.mean(ndcg_3_list)), 4),
        "ndcg_at_5": round(float(np.mean(ndcg_5_list)), 4),
        "ndcg_at_10": round(float(np.mean(ndcg_10_list)), 4),
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
    pr_auc = average_precision_score(y_true, y_scores)
    try:
        roc_auc = roc_auc_score(y_true, y_scores)
    except Exception:
        roc_auc = 0.5

    y_pred = (y_scores >= threshold).astype(int)
    p, r, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )

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

def compute_lead_time_metrics(withdrawals_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes summary distribution of lead times (actual cashout time - prediction snapshot time T).
    """
    lead_times = withdrawals_df["lead_time_hours"].dropna().values.astype(float)
    if len(lead_times) == 0:
        return {"mean_lead_time_hours": 0.0, "median_lead_time_hours": 0.0}

    return {
        "mean_lead_time_hours": round(float(np.mean(lead_times)), 2),
        "median_lead_time_hours": round(float(np.median(lead_times)), 2),
        "p25_lead_time_hours": round(float(np.percentile(lead_times, 25)), 2),
        "p75_lead_time_hours": round(float(np.percentile(lead_times, 75)), 2),
        "min_lead_time_hours": round(float(np.min(lead_times)), 2),
        "max_lead_time_hours": round(float(np.max(lead_times)), 2),
        "sample_size": len(lead_times)
    }

def format_metrics_table(results_dict: Dict[str, Dict[str, Any]]) -> str:
    """Generates a clean markdown comparison table for baseline and main models."""
    headers = [
        "Model", "Hit@1", "Hit@3", "Hit@5", "Hit@10", "MRR", "NDCG@5", "PR-AUC", "ROC-AUC"
    ]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for model_name, m in results_dict.items():
        row = [
            model_name,
            f"{m.get('hit_at_1', 0.0)*100:.1f}%",
            f"{m.get('hit_at_3', 0.0)*100:.1f}%",
            f"{m.get('hit_at_5', 0.0)*100:.1f}%",
            f"{m.get('hit_at_10', 0.0)*100:.1f}%",
            f"{m.get('mrr', 0.0):.4f}",
            f"{m.get('ndcg_at_5', 0.0):.4f}",
            f"{m.get('pr_auc', 0.0):.4f}",
            f"{m.get('roc_auc', 0.0):.4f}"
        ]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)
