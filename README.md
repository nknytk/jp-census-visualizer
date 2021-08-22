## これはなに

[地図で見る国勢調査](https://nknytk.github.io/presentations/demo/jp-census-visualizer/)を作るのに使ったコード


## setup

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
