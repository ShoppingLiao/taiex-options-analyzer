"""
歷史結算資料分析腳本
從累積的 settlement_reviews 計算校準參數，輸出 calibration.json
讓預測器使用真實歷史數據來動態調整區間寬度與情境機率
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime


REVIEWS_DIR = Path("data/ai_learning/settlement_reviews")
CALIBRATION_FILE = Path("data/ai_learning/calibration.json")


def load_all_reviews() -> list[dict]:
    """載入所有結算審核記錄"""
    reviews = []
    for f in sorted(REVIEWS_DIR.glob("settlement_review_*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            reviews.append(data)
        except Exception as e:
            print(f"  跳過 {f.name}: {e}")
    return reviews


def analyze_by_weekday(reviews: list[dict]) -> dict:
    """分析週三 vs 週五的誤差分布"""
    groups = {"wednesday": [], "friday": []}

    for r in reviews:
        wday = r.get("weekday", "").lower()
        acc = r.get("accuracy", {})
        pred = r.get("prediction", {})
        actual = r.get("actual_result", {})

        if wday not in groups:
            continue

        price_error = acc.get("price_error")
        direction_correct = acc.get("direction_correct")
        in_range = acc.get("in_predicted_range")
        pc_ratio = None

        # 取預測當下的 PC Ratio（歷史數據第2天）
        hist = pred.get("historical_data", [])
        if hist:
            pc_ratio = hist[-1].get("pc_ratio")

        predicted_price = acc.get("predicted_price") or pred.get("settlement_price_prediction", {}).get("predicted_price")
        actual_price = acc.get("actual_price") or actual.get("settlement_price")

        if price_error is None or actual_price is None:
            continue

        groups[wday].append({
            "date": r.get("settlement_date"),
            "price_error": abs(price_error),
            "direction_correct": direction_correct,
            "in_range": in_range,
            "pc_ratio": pc_ratio,
            "predicted_price": predicted_price,
            "actual_price": actual_price,
            "overall_accuracy": r.get("accuracy", {}).get("overall_accuracy", 0),
        })

    result = {}
    for wday, records in groups.items():
        if not records:
            result[wday] = {"count": 0}
            continue

        errors = [r["price_error"] for r in records]
        direction_hits = [r for r in records if r["direction_correct"]]
        range_hits = [r for r in records if r["in_range"]]
        accuracies = [r["overall_accuracy"] for r in records]

        # 建議區間半徑：使用 P75 誤差（讓 75% 的案例都能命中）
        p75 = float(np.percentile(errors, 75))
        p90 = float(np.percentile(errors, 90))
        # 取整到 50 點，至少 150 點
        recommended_half_range = max(150, int(np.ceil(p75 / 50) * 50))

        result[wday] = {
            "count": len(records),
            "records": records,  # 保留明細供後續分析
            "error_stats": {
                "mean": round(float(np.mean(errors)), 1),
                "median": round(float(np.median(errors)), 1),
                "std": round(float(np.std(errors)), 1),
                "p75": round(p75, 1),
                "p90": round(p90, 1),
                "max": round(float(np.max(errors)), 1),
            },
            "direction_accuracy": round(len(direction_hits) / len(records) * 100, 1),
            "interval_hit_rate": round(len(range_hits) / len(records) * 100, 1),
            "avg_accuracy": round(float(np.mean(accuracies)), 1),
            "recommended_half_range": recommended_half_range,
        }

    return result


def analyze_pc_ratio_vs_direction(reviews: list[dict]) -> dict:
    """分析 PC Ratio 與結算方向的實際對應關係"""
    records = []

    for r in reviews:
        pred = r.get("prediction", {})
        actual = r.get("actual_result", {})
        acc = r.get("accuracy", {})

        hist = pred.get("historical_data", [])
        if not hist:
            continue

        last_hist = hist[-1]
        pc_ratio = last_hist.get("pc_ratio")
        prev_close = last_hist.get("tx_close")
        actual_price = actual.get("settlement_price") or acc.get("actual_price")

        if pc_ratio is None or prev_close is None or actual_price is None:
            continue

        # 結算相對前一收盤的方向
        actual_direction = "up" if actual_price > prev_close else "down" if actual_price < prev_close else "flat"

        records.append({
            "date": r.get("settlement_date"),
            "weekday": r.get("weekday"),
            "pc_ratio": pc_ratio,
            "prev_close": prev_close,
            "actual_price": actual_price,
            "actual_direction": actual_direction,
            "price_change": actual_price - prev_close,
            "price_change_pct": round((actual_price - prev_close) / prev_close * 100, 2),
        })

    # 按 PC Ratio 分組（使用適合台指選擇權的區間）
    # 台指週選的 PC Ratio 範圍通常較廣（0.5 ~ 3.0+）
    bins = {
        "pc_lt_0.8": {"label": "極度看多 (<0.8)", "records": []},
        "pc_0.8_1.2": {"label": "中性 (0.8-1.2)", "records": []},
        "pc_1.2_1.8": {"label": "偏空 (1.2-1.8)", "records": []},
        "pc_gt_1.8": {"label": "極度看空 (>1.8)", "records": []},
    }

    for rec in records:
        pc = rec["pc_ratio"]
        if pc < 0.8:
            bins["pc_lt_0.8"]["records"].append(rec)
        elif pc < 1.2:
            bins["pc_0.8_1.2"]["records"].append(rec)
        elif pc < 1.8:
            bins["pc_1.2_1.8"]["records"].append(rec)
        else:
            bins["pc_gt_1.8"]["records"].append(rec)

    result = {}
    for key, info in bins.items():
        recs = info["records"]
        if not recs:
            result[key] = {"label": info["label"], "count": 0}
            continue

        up_count = sum(1 for r in recs if r["actual_direction"] == "up")
        down_count = sum(1 for r in recs if r["actual_direction"] == "down")
        avg_change = float(np.mean([r["price_change"] for r in recs]))

        result[key] = {
            "label": info["label"],
            "count": len(recs),
            "up_rate": round(up_count / len(recs) * 100, 1),
            "down_rate": round(down_count / len(recs) * 100, 1),
            "avg_price_change": round(avg_change, 0),
            "dates": [r["date"] for r in recs],
        }

    return result


def compute_scenario_probabilities(weekday_stats: dict) -> dict:
    """
    根據歷史數據計算情境機率（取代固定的 60/20/20）
    目前樣本小，保守地混合歷史觀察與先驗機率
    """
    priors = {"in_range": 60.0, "breakout_up": 20.0, "breakout_down": 20.0}

    result = {}
    for wday, stats in weekday_stats.items():
        if stats.get("count", 0) < 3:
            result[wday] = priors.copy()
            continue

        # 歷史命中率
        hit_rate = stats["interval_hit_rate"]  # 0-100

        # 方向分布（從 PC 分析推算）
        direction_acc = stats["direction_accuracy"]  # 0-100

        # 混合：歷史數據 40% + 先驗 60%（樣本太小，保守混合）
        blended_in_range = hit_rate * 0.4 + priors["in_range"] * 0.6
        remaining = 100 - blended_in_range

        result[wday] = {
            "in_range": round(blended_in_range, 1),
            "breakout_up": round(remaining / 2, 1),
            "breakout_down": round(remaining / 2, 1),
            "note": f"基於 {stats['count']} 筆歷史記錄（混合先驗）",
        }

    return result


def print_report(weekday_stats: dict, pc_analysis: dict, scenario_probs: dict):
    """列印分析報告"""
    print("\n" + "=" * 60)
    print("📊 結算歷史分析報告")
    print("=" * 60)

    for wday in ["wednesday", "friday"]:
        stats = weekday_stats.get(wday, {})
        wday_zh = "週三" if wday == "wednesday" else "週五"
        print(f"\n【{wday_zh}結算】共 {stats.get('count', 0)} 筆")

        if stats.get("count", 0) == 0:
            print("  (無資料)")
            continue

        err = stats["error_stats"]
        print(f"  誤差統計：平均 {err['mean']:.0f}點 | 中位數 {err['median']:.0f}點 | P75={err['p75']:.0f}點 | 最大={err['max']:.0f}點")
        print(f"  方向準確率：{stats['direction_accuracy']}%")
        print(f"  區間命中率：{stats['interval_hit_rate']}%（目前固定±100點）")
        print(f"  平均準確度：{stats['avg_accuracy']}%")
        print(f"  ▶ 建議半徑：±{stats['recommended_half_range']} 點（原±100點）")

        prob = scenario_probs.get(wday, {})
        print(f"  情境機率：區間內={prob.get('in_range', '?')}%  突破上方={prob.get('breakout_up', '?')}%  跌破下方={prob.get('breakout_down', '?')}%")

    print(f"\n【PC Ratio 與結算方向對應】")
    for key, data in pc_analysis.items():
        if data.get("count", 0) == 0:
            continue
        print(f"  {data['label']}：{data['count']}筆 | 上漲={data['up_rate']}% | 下跌={data['down_rate']}% | 平均變化={data['avg_price_change']:+.0f}點")


def main():
    print("載入結算審核記錄...")
    reviews = load_all_reviews()
    print(f"  共載入 {len(reviews)} 筆")

    if len(reviews) == 0:
        print("無資料可分析")
        return

    print("\n分析週三/週五誤差分布...")
    weekday_stats = analyze_by_weekday(reviews)

    print("分析 PC Ratio 與方向對應...")
    pc_analysis = analyze_pc_ratio_vs_direction(reviews)

    print("計算情境機率...")
    scenario_probs = compute_scenario_probabilities(weekday_stats)

    # 輸出報告
    print_report(weekday_stats, pc_analysis, scenario_probs)

    # 整理輸出（去除 records 明細，避免 calibration 檔案過大）
    calibration = {
        "generated_at": datetime.now().isoformat(),
        "source_count": len(reviews),
        "weekday": {
            wday: {k: v for k, v in stats.items() if k != "records"}
            for wday, stats in weekday_stats.items()
        },
        "pc_ratio_direction": pc_analysis,
        "scenario_probabilities": scenario_probs,
    }

    CALIBRATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    CALIBRATION_FILE.write_text(
        json.dumps(calibration, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\n✅ 校準參數已寫入：{CALIBRATION_FILE}")
    print("\n接下來可執行預測時，系統將自動載入這份校準數據。")


if __name__ == "__main__":
    main()
