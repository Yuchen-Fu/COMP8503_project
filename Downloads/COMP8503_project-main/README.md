
# COMP8503 Final Project

This project contains a simple implementation for paper entitled “[Edge-Path Bundling: A Less Ambiguous Edge Bundling Approach](https://www.computer.org/csdl/journal/tg/2022/01/09552919/1xibXgJW32U)” (Wallinger et al., IEEE Transactions on Visualization & Computer Graphics 2022)  and applies it to a world-wide airline network.

The focus is on the main mechanism:

- Represent airline routes as a graph of airports (nodes) and flights (edges) with geographic coordinates.
- For each edge, search for an alternative route along existing edges using shortest paths.
- Only accept detours that are not too long, and bend edges along these accepted paths.
- Turn the resulting paths into smooth Bézier curves to obtain bundled edges.

This implementation was evaluated on two datasets. The first, Migrations, is the same example used in the authors’ original repository ([source](https://github.com/mwallinger-tu/edge-path-bundling/blob/master/data/migrations.json)), allowing a direct comparison against their results. The second dataset is a global airline network built from two Kaggle collections: airport locations and flight routes ([airports](https://www.kaggle.com/datasets/open-flights/airports-train-stations-and-ferry-terminals), [flights](https://www.kaggle.com/datasets/open-flights/flight-route-database)). Together, these files list 12,100 airports and 59,036 routes. After basic cleaning—removing null entries, airports without any connecting flights, and routes referencing missing airports—the final graph consists of 10,669 airports (nodes) and 19,080 flights (edges).

---

## Features

This simplified implementation includes:

- A path-based bundling algorithm that:
  - temporarily removes an edge,
  - runs Dijkstra’s algorithm between its endpoints,
  - checks a detour-length constraint,
  - and locks accepted detour edges for reuse.
- Bézier control point generation with simple midpoint smoothing.
- 2D rendering of the bundled network.
- A small command-line interface to adjust key parameters (`d`, `k`, smoothing, sampling).

---

## Environment

Tested with:

- Python 3.9–3.11
- `numpy`
- `matplotlib`
- `pandas`
- `tqdm`

- packages for drawing a world map background (`geopandas`, `shapely`).

---

## Project Structure

```text
code/
    main.py           # Command-line entry point and bundling loop
    model.py          # Node/Edge classes and distance helpers
    dijkstra.py       # Shortest path routine with skip/lock support
    airports.py       # Data loader for world airline network
    migrations.py     # Secondary toy dataset (not central to the report)
    drawing.py        # Plot rendering
    bezier/
        control_points.py  # Control point calculation and smoothing
        bezier.py          # Bézier curve evaluation (2D and spherical)

assets/							# CSVs and other data files
    ...                

output/
    ...                
````

---

## How to Run

From the repository root:

```python
pip install -r code/requirements.txt
```

Then run the bundling on the airline network:

```python
python code/main.py --dataset airports --d 2.0 --k 1.0 --samples 120 --smoothing 2
python code/main.py --dataset airports --d 2.0 --k 1.5 --samples 120 --smoothing 2
python code/main.py --dataset airports --d 2.0 --k 2.0 --samples 120 --smoothing 2
python code/main.py --dataset airports --plot-3d --d 2 --k 1.5 --smoothing 1 --step-size-3d 20 --tag 3d
```

---

## Output

| Type                                                         | Graph                                                        |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| 2D plotting, `k=1`                                           | <img src="/output/bundled_2d_d1_0.png" alt="bundled_2d_d1_0" style="zoom:24%;" /> |
| 2D plotting, `k=1.5`                                         | <img src="/output/bundled_2d_d1_5.png" alt="bundled_2d_d1_5" style="zoom:24%;" /> |
| 2D plotting, `k=2`                                           | <img src="/output/bundled_2d_d2_0.png" alt="bundled_2d_d2_0" style="zoom:24%;" /> |
| 2D plotting, `k=2`. Blue edges represent flights that failed the detour-length test and thus stay unbundled, helping separate true main corridors (red) from isolated or sparse connections. | <img src="/output/spherical_texture_3d.png" alt="spherical_texture_3d" style="zoom:25%;" /> |

---

## Citation

The project relies on the author's [javascript implementation of the edge-path bundling algorithm](https://github.com/mwallinger-tu/edge-path-bundling
). 

```
M. Wallinger, mwallinger-tu/edge-path-bundling. (Sept. 22, 2025). JavaScript. Accessed: Nov. 21, 2025. [Online]. Available: https://github.com/mwallinger-tu/edge-path-bundling
`````
