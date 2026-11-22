import sys
sys.path.insert(0, '.')
from backend.routes.predict import predict_sample_by_index

for idx in [0, 10, 50, 100, 200]:
    res = predict_sample_by_index(idx)
    b = res.class_breakdown
    c1 = b['class_1']
    c2 = b['class_2']
    c3 = b['class_3']
    c4 = b['class_4']
    c5 = b['class_5']
    c6 = b['class_6']
    c7 = b['class_7']

    veg = c2.percentage + c3.percentage + c4.percentage
    unbuilt_ha = 40.96 - c6.area_hectares
    unbuilt_pct = (unbuilt_ha / 40.96) * 100
    cultivable_pct = c4.percentage + c5.percentage
    cultivable_ha = cultivable_pct * 40.96 / 100

    farm_score = round((c4.percentage * 1.5) + (c5.percentage * 0.75) + (veg * 0.4) - (c6.percentage * 1.2))
    if 0.5 <= c1.percentage <= 4.0: farm_score += 5
    farm_score = max(20, min(95, farm_score))
    farm_rating = 'Prime Agrarian Farmland' if farm_score >= 80 else ('Favorable Agricultural Land' if farm_score >= 65 else 'Moderate / Mixed Fringe')

    const_score = round((unbuilt_pct * 0.55) + 20 + (15 if c1.area_hectares < 0.5 else (10 if c1.area_hectares < 1.5 else 5)) + (5 if 3 < c6.percentage < 20 else 0))
    const_score = max(30, min(96, const_score))
    const_rating = 'High Greenfield Readiness' if const_score >= 85 else ('Favorable Development Footprint' if const_score >= 70 else 'Transitional / Infill Development')

    print(f"Sample {idx:03d} ({res.sample_name}):")
    print(f"  Farming: {farm_score}/100 ({farm_rating})")
    print(f"  Construction: {const_score}/100 ({const_rating})")
    print(f"  Veg: {veg:.1f}% ({veg*40.96/100:.2f} ha), Built: {c6.percentage:.1f}% ({c6.area_hectares} ha), Water: {c1.percentage:.1f}% ({c1.area_hectares} ha)")
