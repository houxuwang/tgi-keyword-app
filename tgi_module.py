import pandas as pd
import numpy as np

def generate_tgi_dual_outputs(
    df,
    base_column,
    threshold,
    tgi_threshold,
    share_threshold,
    seg_start_col,
    seg_end_col,
    tgi_start_col,
    tgi_end_col
):
    """
    自定义列区间进行两阶段筛选：output1基于SEG阈值，output2基于TGI+baseline，最终合并

    参数：
        df: 原始数据 DataFrame
        base_column: baseline占比列名
        threshold: SEG原始筛选阈值
        tgi_threshold: TGI筛选阈值
        share_threshold: baseline占比筛选阈值
        seg_start_col: SEG列起始索引
        seg_end_col: SEG列结束索引
        tgi_start_col: TGI列起始索引
        tgi_end_col: TGI列结束索引

    返回：
        合并后的 标签类型 x SEG 标签字符串 DataFrame
    """
    
    seg_names = df.columns[seg_start_col:seg_end_col + 1].tolist()
    tgi_names = df.columns[tgi_start_col:tgi_end_col + 1].tolist()
    label_types = df['标签类型'].dropna().unique().tolist()

    # ---------- output1 ----------
    output1 = pd.DataFrame(index=label_types, columns=seg_names)
    for seg in seg_names:
        df_seg = df[df[seg] > threshold]
        for label_type in label_types:
            tags = df_seg[df_seg['标签类型'] == label_type]['标签'].dropna().astype(str).tolist()
            output1.loc[label_type, seg] = ", ".join(tags) if tags else ""
    output1.fillna("", inplace=True)

    # ---------- output2 ----------
    output2 = pd.DataFrame(index=label_types, columns=seg_names)
    for seg_col, tgi_col in zip(seg_names, tgi_names):
        if tgi_col not in df.columns or base_column not in df.columns:
            continue

        mask = (df[tgi_col] >= tgi_threshold) & (df[base_column] > share_threshold)
        df_selected = df[mask]

        for label_type in label_types:
            tags = df_selected[df_selected['标签类型'] == label_type]['标签'].dropna().astype(str).tolist()
            output2.loc[label_type, seg_col] = ", ".join(tags) if tags else ""
    output2.fillna("", inplace=True)

    # ---------- 合并 ----------
    def merge_cells(x, y):
        parts = []
        for v in [x, y]:
            if pd.notna(v) and v != "":
                parts.extend([i.strip() for i in str(v).split(",") if i.strip()])
        return ", ".join(sorted(set(parts)))

    combined = pd.DataFrame(index=label_types, columns=seg_names)
    for row in label_types:
        for col in seg_names:
            combined.loc[row, col] = merge_cells(output1.loc[row, col], output2.loc[row, col])

    return combined.fillna("")