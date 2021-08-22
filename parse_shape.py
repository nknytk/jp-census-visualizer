import json
import os
import re
import unicodedata
import sqlite3
import shapefile

DATA_DIR = 'data'
CHOUMOKU_PATTERN = re.compile('^(.*[^一二三四五六七八九十])([一二三四五六七八九十]+)(丁目.*)$')
KANSUJI = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}


def main():
    db = prepare_db(DATA_DIR + '/data.db')
    try:
        shapefiles_to_db(db)
    finally:
        db.close()


def prepare_db(dbfile_path: str) -> sqlite3.Connection:
    """ SQLite3のDBファイルとデータ取り込み用テーブルを作成する """
    db = sqlite3.connect(dbfile_path)
    cur = db.cursor()
    # ダウンロードしたshapefileの情報をそのまま入れるテーブル
    # TODO: 後段の利用方法に合わせてindexをつける
    cur.execute('DROP TABLE IF EXISTS areas')
    cur.execute("""
      CREATE TABLE areas (
        keycode TEXT,               -- 図形と集計データのリンクコード(KEY_CODE)
        pref TEXT,                  -- 都道府県番号(PREF)
        city TEXT,                  -- 市区町村番号(CITY)
        areacd TEXT,                -- 町字コード+丁目、字などの番号(S_AREA)
        pref_name TEXT,             -- 都道府県名(PREF_NAME)
        city_name TEXT,             -- 市区町村名(GST_NAME + CSS_NAME)
        area_name TEXT,             -- 町丁・字等名称(S_NAME)
        area REAL,                  -- 面積(㎡)(AREA)
        population INTEGER,         -- 人口(JINKO)
        num_of_households INTEGER,  -- 世帯数(SETAI)
        year INTEGER,               -- 調査年
        bbox TEXT,                  -- 外接矩形
        shape TEXT                  -- 地域形状
      )
    """)
    return db


def shapefiles_to_db(db: sqlite3.Connection):
    """ 町丁目境界のshapefileの内容をDBに取り込む """
    cur = db.cursor()
    for year in range(2000, 2020, 5):
        heisei = year - 1988
        for pref in range(1, 48):
            original_file = f'{DATA_DIR}/original/h{heisei}ka{pref:02d}.shp'
            print(original_file)

            shp = shapefile.Reader(original_file, encoding='cp932')
            for shape, record in zip(shp.shapes(), shp.records()):
                if record.HCODE != 8101:  # 水面調査区等はスキップ
                    continue
                splits = list(shape.parts)
                splits.append(len(shape.points))
                polygons = []
                for i in range(len(splits) - 1):
                    polygons.append(shape.points[splits[i]:splits[i+1]])
                city_name = record.CITY_NAME
                if record.GST_NAME != record.CITY_NAME and not record.GST_NAME.endswith('郡'):
                    city_name = record.GST_NAME + city_name
                values = (
                    record.KEY_CODE,
                    record.PREF,
                    record.CITY,
                    record.S_AREA,
                    record.PREF_NAME,
                    city_name,
                    normalize_choumoku(record.S_NAME),
                    record.AREA,
                    record.JINKO,
                    record.SETAI,
                    year,
                    json.dumps(list(shape.bbox)),
                    json.dumps(list(polygons))
                )
                placeholders = ','.join('?' for i in range(len(values)))
                cur.execute(f'INSERT INTO areas VALUES ({placeholders})', values)

    db.commit()


def normalize_choumoku(text: str) -> str:
    """ 丁目の表記を半角アラビア数字に統一する """
    text = unicodedata.normalize('NFKC', text)
    m = CHOUMOKU_PATTERN.match(text)
    if not m:
        return text
    prefix, choumoku, suffix = m.groups()
    c1, c2, c3 = choumoku.partition('十')
    if c3:
        if c1:
            choumoku = 10 * KANSUJI[c1] + KANSUJI[c3]
        else:
            choumoku = 10 + KANSUJI[c3]
    elif c2:
        choumoku = 10
    else:
        choumoku = KANSUJI[c1]
    return prefix + str(choumoku) + suffix


if __name__ == '__main__':
    main()
