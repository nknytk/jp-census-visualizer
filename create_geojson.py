import json
import os
import sqlite3
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import cascaded_union
import parse_csv

DATA_DIR = 'data'
DEPLOY_DIR = 'deployment'
LATEST_YEAR = 2015
SIMPLIFY_TOLERANCE = 0.0003
CITY_SIMPLIFY_TOLERANCE = 0.001


def main():
    additional_data = parse_csv.read_census_csvs()
    db = sqlite3.connect(os.path.join(DATA_DIR, 'data.db'))
    cur = db.cursor()

    try:
        city_summaries = []
        cur.execute('SELECT * FROM areas ORDER BY pref ASC, city ASC, year DESC')
        columns = [d[0] for d in cur.description]
        city_key = ''
        city_rows = []

        for row in cur:
            row_dic = dict(zip(columns, row))
            new_city_key = row_dic['pref'] + row_dic['city']
            if new_city_key != city_key:
                if len(city_rows) > 0:
                    city_info = merge_city(city_rows)
                    if city_info is not None:
                        enrich_city_info(city_info, additional_data)
                        to_geojson([city_info], os.path.join(DEPLOY_DIR, 'detailed_areas', f'{city_key}.json'))
                        city_summaries.append(summarize(city_info))
                city_key = new_city_key
                city_rows = []
            city_rows.append(row_dic)

        city_info = merge_city(city_rows)
        if city_info is not None:
            enrich_city_info(city_info, additional_data)
            to_geojson([city_info], os.path.join(DEPLOY_DIR, 'detailed_areas', f'{city_key}.json'))
            city_summaries.append(summarize(city_info))
        to_geojson(city_summaries, os.path.join(DEPLOY_DIR, 'japan_cities.json'), 6)

    finally:
        db.close()


def merge_city(rows: list) -> dict:
    """ 町丁目単位のレコードを市区町村にまとめる """
    current_year = rows[0]['year']
    if current_year != LATEST_YEAR:
        return None

    print(rows[0]['pref_name'] + rows[0]['city_name'])
    merged_city_info = {
        'pref': rows[0]['pref'],
        'city': rows[0]['city'],
        'pref_name': rows[0]['pref_name'],
        'city_name': rows[0]['city_name'],
        # 人口、世帯数、面積は過去の国勢調査実施年ごとの履歴も保持
        'year': [],
        'population': [],
        'num_of_households': [],
        'area': [],
    }

    population_sum = 0
    num_of_households_sum = 0
    area_sum = 0
    polygons = []
    for row in rows:
        if row['year'] != current_year:
            merged_city_info['year'].append(current_year)
            merged_city_info['population'].append(population_sum)
            merged_city_info['num_of_households'].append(num_of_households_sum)
            merged_city_info['area'].append(area_sum)

            current_year = row['year']
            population_sum = 0
            num_of_households_sum = 0
            area_sum = 0

        population_sum += row['population']
        num_of_households_sum += row['num_of_households']
        area_sum += row['area']

        if current_year == LATEST_YEAR:
            for shape in json.loads(row['shape']):
                polygons.append(Polygon(shape))

    merged_city_info['year'].append(current_year)
    merged_city_info['population'].append(population_sum)
    merged_city_info['num_of_households'].append(num_of_households_sum)
    merged_city_info['area'].append(area_sum)

    # 町丁目境界をマージして市区町村境界を作る
    merged_city_info['shape'] = cascaded_union(polygons)
    merged_city_info['coordinates'] = simplify(merged_city_info['shape'], SIMPLIFY_TOLERANCE)
    return merged_city_info


def enrich_city_info(city_info: dict, additional_data: dict):
    area_code = city_info['pref'] + city_info['city']

    population_data = additional_data['population'].get(area_code)
    if population_data:
        city_info['avg_age'] = population_data['0101']['avg_age']
        city_info['u15_ratio'] = population_data['0101']['u15_ratio']
        city_info['a65_ratio'] = population_data['0101']['a65_ratio']
        city_info['female_ages'] = []
        city_info['male_ages'] = []
        for i in range(10):  # 10歳刻みにまとめる
            female_cnt = 0
            male_cnt = 0
            for age in range(i * 10, (i + 1) * 10):
                female_cnt += population_data['0301'][f'age_{age}']
                male_cnt += population_data['0201'][f'age_{age}']
            city_info['female_ages'].append(female_cnt)
            city_info['male_ages'].append(male_cnt)
        city_info['female_ages'].append(population_data['0301']['age_100'])
        city_info['male_ages'].append(population_data['0201']['age_100'])

    housing_data = additional_data['housing'].get(area_code)
    if housing_data:
        city_info['housing'] = housing_data['01']

    move_data = additional_data['move'].get(area_code)
    if move_data:
        city_info.update(move_data['01'])

    workforce_data = additional_data['workforce'].get(area_code)
    if workforce_data and workforce_data['']['workable_people'] and workforce_data['']['unemployed']:
        city_info['unemployment_rate'] = workforce_data['']['unemployed'] / workforce_data['']['workable_people'] * 100

    commuting_data = additional_data['commuting'].get(area_code)
    if commuting_data:
        city_info['daytime_population'] = commuting_data['']['daytime_population']
        city_info['nighttime_population'] = commuting_data['']['nighttime_population']
        city_info['commute_in'] = commuting_data['']['commute_in']
        city_info['commute_out'] = commuting_data['']['commute_out']

    industry_data = additional_data['industry'].get(area_code)
    if industry_data:
        city_info['primary_industry'] = industry_data['']['primary_industry']
        city_info['secondary_industry'] = industry_data['']['secondary_industry']
        city_info['tertiary_industry'] = industry_data['']['tertiary_industry']


def summarize(city_info: dict) -> dict:
    population_growth_rate = None
    if len(city_info['population']) > 1:
        population_growth_rate = round((city_info['population'][0] - city_info['population'][1]) / city_info['population'][1] * 100, 3)
    household_growth_rate = None
    if len(city_info['num_of_households']) > 1:
        household_growth_rate = round((city_info['num_of_households'][0] - city_info['num_of_households'][1]) / city_info['num_of_households'][1] * 100, 3)
    people_per_household = None
    if city_info['num_of_households'][0] > 0:
        people_per_household = round(city_info['population'][0] / city_info['num_of_households'][0], 4)
    day_night_population_ratio = None
    if city_info.get('nighttime_population'):
        day_night_population_ratio = round(city_info['daytime_population'] / city_info['nighttime_population'] * 100, 3)
    unemployment_rate = None if 'unemployment_rate' not in city_info else round(city_info['unemployment_rate'], 3)

    summary = {
        'area_code': city_info['pref'] + city_info['city'],
        'area_name': city_info['pref_name'] + city_info['city_name'],
        'values': [
            # 0 人口
            city_info['population'][0],
            # 1 世帯数
            city_info['num_of_households'][0],
            # 2 面積
            int(round(city_info['area'][0] / 1000000)),
            # 3 人口増加率
            population_growth_rate,
            # 4 世帯数増加率
            household_growth_rate,
            # 5 人口密度
            int(round(city_info['population'][0] / city_info['area'][0] * 1000000)),
            # 6 世帯あたり人数
            people_per_household,
            # 7 平均年齢
            round(city_info['avg_age'], 3),
            # 8 高齢者率
            round(city_info['a65_ratio'], 3),
            # 9 完全失業率
            unemployment_rate,
            # 10 昼夜間人口比率
            day_night_population_ratio
        ],
        'coordinates': simplify(city_info['shape'], CITY_SIMPLIFY_TOLERANCE)
    }
    return summary


def simplify(city_polygon, tolerance):
    if isinstance(city_polygon, Polygon):
        return [[list(city_polygon.simplify(tolerance).exterior.coords)]]
    else:
        return [[list(p.simplify(tolerance).exterior.coords)] for p in city_polygon]


def to_geojson(objs: list, dump_path: str, location_precision=7):
    features = []
    for obj in objs:
        obj_copy = obj.copy()
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'MultiPolygon',
                # データ量削減のため、小数は丸める
                'coordinates': round_recursive(obj_copy['coordinates'], location_precision)
            }
        }
        if 'shape' in obj_copy:
            del(obj_copy['shape'])
        del(obj_copy['coordinates'])
        feature['properties'] = obj_copy
        features.append(feature)

    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }

    dump_dir = os.path.dirname(dump_path)
    os.makedirs(dump_dir, exist_ok=True)
    with open(dump_path, mode='w') as fp:
        fp.write(json.dumps(geojson, ensure_ascii=False, separators=(',', ':')))

def round_recursive(v, r):
    if isinstance(v, float):
        return round(v, r)
    elif isinstance(v, tuple) or isinstance(v, list):
        return [round_recursive(vv, r) for vv in v]


if __name__ == '__main__':
    main()
