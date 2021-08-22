#!/bin/bash

set -e

mkdir -p data/original
cd data/original

# 地図で見る統計(統計GIS) データダウンロードページから、町丁目境界データを
# 世界測地系緯度経度 Shapefileで都道府県別にダウンロードする
# https://www.e-stat.go.jp/gis/statmap-search?page=1&type=2&aggregateUnitForBoundary=A&toukeiCode=00200521
#for year in 2000 2005 2010 2015; do
#  for pref in {01..47}; do
#    filename="${year}_${pref}.zip"
#    data_url="https://www.e-stat.go.jp/gis/statmap-search/data?dlserveyId=A00200521${year}&code=${pref}&coordSys=1&format=shape&downloadType=5&datum=2000"
#    wget -O ${filename} "${data_url}"
#    sleep 10
#    unzip ${filename}
#    rm ${filename}
#  done
#done

# 国勢調査の結果から、描画対象に使うファイルをダウンロードする
# https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00200521&tstat=000001080615

# 人口等基本集計（男女・年齢・配偶関係，世帯の構成，住居の状態など）/ 全国結果 からダウンロード
# https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00200521&tstat=000001080615&cycle=0&tclass1=000001089055&tclass2=000001089056&tclass3val=0
# 3-2 "年齢(各歳)，男女別人口，年齢別割合，平均年齢及び年齢中位数(総数及び日本人) － 全国※，全国市部・郡部，都道府県※，都道府県市部・郡部，市区町村※，平成12年市町村"
wget -O - "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000031473213&fileKind=1" | iconv -f cp932 -t utf8 > 3-2.csv
sleep 10
# 18-2 "住居の種類・住宅の所有の関係(6区分)別一般世帯数，一般世帯人員及び1世帯当たり人員 － 全国※，全国市部・郡部，都道府県※，都道府県市部・郡部，市区町村※，平成12年市町村" より "一般世帯数"
wget -O - "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000031473239&fileKind=1" | iconv -f cp932 -t utf8 > 18-2.csv
sleep 10

# 就業状態等基本集計（労働力状態，就業者の産業･職業など）/ 全国結果 からダウンロード
# https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00200521&tstat=000001080615&cycle=0&tclass1=000001095955&tclass2=000001100295&tclass3val=0
# 1-3 "労働力状態(8区分)，男女別15歳以上人口及び労働力率 － 全国，都道府県，市区町村"
wget -O - "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000031569352&fileKind=1" | iconv -f cp932 -t utf8 > 1-3.csv
sleep 10
# 6-3 "産業(大分類)，男女別15歳以上就業者数及び産業別割合 － 全国，都道府県，市区町村"
wget -O - "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000031569362&fileKind=1" | iconv -f cp932 -t utf8 > 6-3.csv
sleep 10
# 9-3 "職業(大分類)，男女別15歳以上就業者数及び職業別割合 － 全国，都道府県，市区町村"
wget -O - "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000031569368&fileKind=1" | iconv -f cp932 -t utf8 > 9-3.csv
sleep 10

# 従業地・通学地による人口・就業状態等集計（人口，就業者の産業（大分類）・職業（大分類）など）/ 全国結果 からダウンロード
# https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00200521&tstat=000001080615&cycle=0&tclass1=000001101935&tclass2=000001101936&tclass3val=0
# 1 "常住地又は従業地・通学地(27区分)による人口，就業者数及び通学者数(流出人口，流入人口，昼夜間人口比率－特掲) － 全国，都道府県，市区町村"
wget -O - "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000031586670&fileKind=1" | iconv -f cp932 -t utf8 > 1.csv
sleep 10

# 移動人口の男女・年齢等集計（人口の転出入状況）/ 全国結果 からダウンロード
# https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00200521&tstat=000001080615&cycle=0&tclass1=000001093875&tclass2=000001093876&tclass3val=0
# 3 "現住地又は5年前の常住地(10区分)による年齢(5歳階級)，男女別人口(転入・転出－特掲) － 全国，都道府県，市区町村"
wget -O - "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000031518572&fileKind=1" | iconv -f cp932 -t utf8 > 3.csv
