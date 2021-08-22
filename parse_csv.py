import csv


def read_census_csvs():
    data = {}

    # 年齢別人口
    idx2col = {8 + i: f'age_{i}' for i in range(101)}
    idx2col.update({110: 'avg_age', 138: 'u15_ratio', 139: '15-64_ratio', 140: 'a65_ratio'})
    data['population'] = read_csv('data/original/3-2.csv', 12, idx2col)

    # 住居の種類
    idx2col = {
        10: 'owned_house',          # 持ち家
        11: 'public_rented_house',  # 公営・都市再生機構・公社の借家
        12: 'private_rented_house', # 民間の借家
        13: 'salary_housing',       # 給与住宅(社宅、寄宿舎など)
        14: 'room_renting',         # 間借り
        15: 'facilities',           # 住宅以外に住む一般世帯
        16: 'other'                 # 住居の種類「不詳」
    }
    data['housing'] = read_csv('data/original/18-2.csv', 8, idx2col)

    # 労働力状態
    idx2col = {
        6: 'workable_people',     # 労働力人口
        7: 'working_people',      # 就業者
        8: 'work_only',           # 主に仕事
        9: 'housework_and_work',  # 家事のほか仕事
        10: 'school_and_work',    # 通学のかたわら仕事
        11: 'leave',              # 休業者
        12: 'unemployed',         # 完全失業者
        13: 'unworkable_people',  # 非労働力人口
        14: 'housework_only',     # 家事
        15: 'school',             # 通学
        16: 'other',              # その他
        17: 'unknown',            # 労働状態不詳
        18: 'working_ratio'       # 労働力率(%) = 労働力人口/15歳以上人口 * 100
    }
    data['workforce'] = read_csv('data/original/1-3.csv', 11, idx2col)

    # 産業
    idx2col = {
        5: 'all',                           # 総数
        6: 'agriculture_and_foresty',       # A 農業, 林業
        8: 'fishing',                       # B 漁業
        9: 'mining',                        # C 鉱業，採石業，砂利採取業
        10: 'construction',                 # D 建設業
        11: 'manufacturing',                # E 製造業
        12: 'lifeline',                     # F 電気・ガス・熱供給・水道業
        13: 'telecommunication',            # G 情報通信業
        14: 'transportation',               # H 運輸業，郵便業
        15: 'wholesale_and_retail',         # I 卸売業，小売業
        16: 'finance_and_insurance',        # J 金融業，保険業
        17: 'real_estate_and_leasing',      # K 不動産業，物品賃貸業
        18: 'academic_and_professional',    # L 学術研究，専門・技術サービス業
        19: 'hotel_and_restaurant',         # M 宿泊業，飲食サービス業
        20: 'lifestyle_and_entertainment',  # N 生活関連サービス業，娯楽業
        21: 'education',                    # O 教育，学習支援業
        22: 'medical_care_and_welfare',     # P 医療, 福祉
        23: 'complex_service',              # Q 複合サービス事業
        24: 'other_service',                # R サービス業（他に分類されないもの）
        25: 'government',                   # S 公務（他に分類されるものを除く）
        26: 'unclassifiable',               # T 分類不能の産業
        27: 'primary_industry',             # 第1次産業 A, B
        28: 'secondary_industry',           # 第2次産業 C ~ E
        29: 'tertiary_industry',            # 第3次産業 F ~ T
    }
    data['industry'] = read_csv('data/original/6-3.csv', 11, idx2col)

    # 職業
    idx2col = {
        5: 'all',
        6: 'management',           # A 管理的職業従事者
        7: 'tech_professional',    # B 専門的・技術的職業従事者
        8: 'office_worker',        # C 事務従事者
        9: 'sales',                # D 販売従事者
        10: 'service',             # E サービス職業従事者
        11: 'security',            # F 保安職業従事者
        12: 'primary_intdustry',   # G 農林漁業従事者
        13: 'production_process',  # H 生産工程従事者
        14: 'driver',              # I 輸送・機械運転従事者
        15: 'constructor',         # J 建設・採掘従事者
        16: 'cleaning_packageing', # K 運搬・清掃・包装等従事者
        17: 'other'
    }            
    data['job'] = read_csv('data/original/9-3.csv', 10, idx2col)

    # 通勤通学
    idx2col = {
        5: 'nighttime_population',   # 夜間人口
        6: 'non_commuter',           # 従業も通学もしていない 
        7: 'work_at_home',           # 自宅で従業
        8: 'commute_to_same_city',   # 自宅外の自市区町村で従業・通学
        9: 'commute_to_other_city',  # 他市区町村で従業・通学 
        15: 'daytime_population',    # 昼間人口
        19: 'commute_out',           # 流出
        20: 'commute_in'             # 流入
    }
    data['commuting'] = read_csv('data/original/1.csv', 14, idx2col)

    # 転出、転入
    idx2col = {19: 'move_in', 20: 'move_out'}
    data['move'] = read_csv('data/original/3.csv', 26, idx2col)

    return data


def read_csv(file_path: str, n_header_rows: int, idx2col: dict) -> dict:
    """ 国勢調査のCSVファイルからidx2colに指定されたカラムのデータを取り出す """
    with open(file_path) as fp:
        # ヘッダ部は捨てる
        for i in range(n_header_rows):
            fp.readline()

        records = {}
        csv_reader = csv.reader(fp)
        for row in csv_reader:

            record_category = row[1]
            area_cd = row[2]
            area_category = row[3]
            # 市区町村単位以外のレコードはスキップ
            if len(area_cd) != 5 or not area_category.isdigit(): 
                continue

            if area_cd not in records:
                records[area_cd] = {}

            # 取得済み市区町村はスキップ。同一市区町村が複数行登場する場合、2行目以降は合併前の地域を
            # 基準として集計した値となっており、合併を扱いながら複数年の調査結果を追うにはここを修正する必要がある
            if area_cd in records and record_category in records[area_cd]:
                continue
            records[area_cd][record_category] = {idx2col[idx]: format_number(row[idx]) for idx in idx2col}

    return records


def format_number(val: str):
    """ 文字列を数値型に変換する """
    if val == '-':
        return 0
    elif val.find('.') == -1:
        return int(val)
    else:
        return float(val)


if __name__ == '__main__':
    read_census_csvs()
