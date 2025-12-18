from __future__ import annotations

import pandas as pd

from eda_cli.core import (
    compute_quality_flags,
    correlation_matrix,
    flatten_summary_for_print,
    missing_table,
    summarize_dataset,
    top_categories,
)


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [10, 20, 30, None],
            "height": [140, 150, 160, 170],
            "city": ["A", "B", "A", None],
        }
    )


def test_summarize_dataset_basic():
    df = _sample_df()
    summary = summarize_dataset(df)

    assert summary.n_rows == 4
    assert summary.n_cols == 3
    assert any(c.name == "age" for c in summary.columns)
    assert any(c.name == "city" for c in summary.columns)

    summary_df = flatten_summary_for_print(summary)
    assert "name" in summary_df.columns
    assert "missing_share" in summary_df.columns


def test_missing_table_and_quality_flags():
    df = _sample_df()
    missing_df = missing_table(df)

    assert "missing_count" in missing_df.columns
    assert missing_df.loc["age", "missing_count"] == 1

    summary = summarize_dataset(df)
    flags = compute_quality_flags(summary, missing_df)
    assert 0.0 <= flags["quality_score"] <= 1.0


def test_correlation_and_top_categories():
    df = _sample_df()
    corr = correlation_matrix(df)
    # корреляция между age и height существует
    assert "age" in corr.columns or corr.empty is False

    top_cats = top_categories(df, max_columns=5, top_k=2)
    assert "city" in top_cats
    city_table = top_cats["city"]
    assert "value" in city_table.columns
    assert len(city_table) <= 2

def test_const_col_and_sus_dup():
    """Тест новых эвристик: константные колонки и дубликаты id."""
    
    # DataFrame с константной колонкой и дублирующимися id
    df = pd.DataFrame({
        "age": [10, 20, 30, 40],
        "constant_col": [5, 5, 5, 5],      # все значения одинаковые
        "user_id": [1, 1, 2, 3],           # дубликат user_id=1
        "clientId": [100, 200, 300, 400],  # нормальный id (уникальный)
        "city": ["A", "B", "A", "C"]
    })
    
    summary = summarize_dataset(df)
    missing_df = missing_table(df)  # пропусков нет
    
    flags = compute_quality_flags(summary, missing_df)
    
    # Проверяем новые флаги
    assert flags["has_constant_columns"] is True, "constant_col должна быть константной"
    assert flags["has_suspicious_id_duplicates"] is True, "user_id имеет дубликаты"
    
    expected_score = 1.0
    expected_score -= 0.0  # нет пропусков (max_missing_share)
    expected_score -= 0.2  # too_few_rows (5 < 100)
    expected_score -= 0.0  # (n_cols=5 <= 100, НЕ > 100)
    expected_score -= 0.5  # has_constant_columns
    expected_score -= 0.10 # has_suspicious_id_duplicates
    expected_score = max(0.0, min(1.0, expected_score))  # 0.2
    
    assert abs(flags["quality_score"] - expected_score) < 0.01, "Скор должен учитывать новые штрафы"
    
    # Дополнительный тест: чистые данные без проблем
    df_clean = pd.DataFrame({
        "age": [10, 20, 30, 40],
        "user_id": [1, 2, 3, 4],     # уникальные id
        "city": ["A", "B", "C", "D"]
    })
    
    summary_clean = summarize_dataset(df_clean)
    missing_clean = missing_table(df_clean)
    flags_clean = compute_quality_flags(summary_clean, missing_clean)
    
    assert flags_clean["has_constant_columns"] is False
    assert flags_clean["has_suspicious_id_duplicates"] is False
