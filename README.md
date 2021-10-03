# 「地図で見る国勢調査」について

https://nknytk.github.io/presentations/demo/jp-census-visualizer/  
市区町村別の人口、平均年齢などを地図上に分かりやすく表示するページ

## 制作目的

* LeafletとPlotlyの備忘録
* 技術力アピール

## 制約

* 極力メンテナンス不要な手段で公開すること
    - お金がかからないこと
    - セキュリティ対応が楽であること
    
## 構成

* github pagesを使用して静的ファイルで公開
* 市区町村の形状と統計情報はjson(geojson)形式のファイルで保持
* ページ全体のスタイルはBootstrap、地図はOpenStreetMapとLeaflet、グラフはPlotlyで作成

## 制作上の工夫

### データ量の圧縮

表示に利用するデータを単純にgeojson形式に変換すると300MBを超え、転送と描画が行えないほど大きなファイルになってしまう。データ読み込みと描画の待ち時間なく快適に利用できるよう、データサイズを小さくするための工夫を行っている。

* ファイルを2種類に分割し、一度に読み込むデータ量を削減
    1. 全市区町村に関して、少数の項目だけを1つにまとめたファイル  
全国地図と一覧表の描画に使用するため、ページ初期化の際に1度だけ読み込む
    2. 市区町村ごとの詳細なデータを市区町村別に分割したファイル  
市区町村の詳細表示を行う際、該当市区町村のファイルだけをその都度読み込む
* 小数の桁数削減
    - 東京周辺では緯度経度1度が約100kmの距離に相当する
    - 小数は6桁までとし、実用上問題ない範囲の誤差でデータを削減
* 市区町村形状の単純化
    - 市区町村の形状を表すポリゴンは多数の点で構成されている
    - 地図上の見た目を損なわない範囲で点を間引く
    - 拡大率が低い状態で見る全国地図用のポリゴンは、市区町村詳細で使用するポリゴンと比べより積極的に間引く

データ量圧縮の効果

| データ圧縮 | 全国地図用geosjonファイルサイズ | 市区町村別geojson合計ファイルサイズ |
| --- | --- | --- |
| なし | 334MB | 339MB |
| 小数の桁数削減 | 196MB | 218MB | 
| 小数の桁数削減 + 形状単純化 | 6.8MB | 24MB |

## 環境構築

### python environment

```
$ python3 -m venv .venv
$ . .venv/bin/activate
(.venv) $ pip install --upgrade pip wheel
(.venv) $ pip install pyshp shapely
```

### download Japanese census data

```
$ ./get_data.sh
```

### process data

```
(.venv) $ python parse_shape.py
(.venv) $ python create_geojson.py
```

`deployment` can be distributed as static file.

