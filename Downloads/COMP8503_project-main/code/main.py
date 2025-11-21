import argparse
import warnings
from pathlib import Path

import airports
import dijkstra
import migrations
from bezier import control_points
from drawing import draw
from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning
from tqdm import tqdm

warnings.simplefilter('ignore', category=NumbaDeprecationWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)


def bundle_edges(nodes, edges, k, smoothing):
    """Bundle edges along existing paths while enforcing the detour-length constraint."""
    control_point_lists = []
    too_long = 0
    no_path = 0

    for edge in tqdm(edges, desc="Computing bundles"):
        if edge.lock:
            continue

        # Temporarily disable the direct edge so an alternate route can be found.
        edge.skip = True

        source = nodes[edge.source]
        dest = nodes[edge.destination]

        path = dijkstra.find_shortest_path(source, dest, nodes)

        if len(path) == 0:
            no_path += 1
            edge.skip = False
            continue

        original_edge_distance = source.distance_to(dest)
        new_path_length = sum([e.distance for e in path])

        # Reject overly long detours to stay faithful to the original topology.
        if new_path_length > k * original_edge_distance:
            too_long += 1
            edge.skip = False
            continue

        for edge_in_path in path:
            edge_in_path.lock = True

        control_point_lists.append(control_points.get(source, dest, nodes, path, smoothing))

    return control_point_lists, too_long, no_path


def load_dataset(dataset, d, assets_dir: Path):
    loaders = {
        "airports": airports.get_airpors_data,
        "migrations": migrations.get_migrations_data,
    }
    if dataset not in loaders:
        raise ValueError(f"Unknown dataset '{dataset}'. Choose from {', '.join(loaders.keys())}.")
    return loaders[dataset](d, assets_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Edge-Path Bundling demo (Wallinger et al.) with 2D/3D plotting."
    )
    parser.add_argument("--dataset", choices=["airports", "migrations"], default="airports",
                        help="Which dataset to load.")
    parser.add_argument("--d", type=float, default=2.0,
                        help="Edge weight exponent; weight = (distance ** d).")
    parser.add_argument("--k", type=float, default=2.0,
                        help="Allow detours up to k times the direct edge length when bundling.")
    parser.add_argument("--samples", type=int, default=100,
                        help="Sampling points per Bezier curve in 2D mode.")
    parser.add_argument("--smoothing", type=int, default=2,
                        help="Recursive midpoint smoothing level for control points.")
    parser.add_argument("--plot-3d", action="store_true",
                        help="Plot spherical texture instead of flat 2D map.")
    parser.add_argument("--step-size-3d", type=float, default=15.0,
                        help="Sampling step (degrees) along spherical curves; larger is faster.")
    parser.add_argument("--tag", type=str, default="",
                        help="Optional suffix for output filenames (bundled_2d_<tag>.png, spherical_texture_<tag>.png).")
    parser.add_argument("--draw-map", dest="draw_map", action="store_true",
                        help="Force-enable base map overlay.")
    parser.add_argument("--no-map", dest="draw_map", action="store_false",
                        help="Disable base map overlay.")
    default_assets = Path(__file__).resolve().parent.parent / "assets"
    default_output = Path(__file__).resolve().parent.parent / "output"
    parser.add_argument("--assets-dir", type=Path, default=default_assets,
                        help="Path to assets folder containing datasets and maps.")
    parser.add_argument("--output-dir", type=Path, default=default_output,
                        help="Directory to write generated textures/plots.")
    parser.set_defaults(draw_map=None)

    args = parser.parse_args()
    draw_map = args.draw_map if args.draw_map is not None else args.dataset == "airports"

    def fmt_number(val: float) -> str:
        """Build a filesystem-friendly number: 1.5 -> 1_5, -2 -> neg2."""
        txt = f"{val}".replace(".", "_")
        return txt.replace("-", "neg")

    # If no explicit tag is provided, include dataset + (d, k) so outputs don't overwrite.
    default_tag = f"{args.dataset}_d{fmt_number(args.d)}_k{fmt_number(args.k)}"
    effective_tag = args.tag or default_tag

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    nodes, edges = load_dataset(args.dataset, args.d, args.assets_dir)

    control_point_lists, too_long, no_path = bundle_edges(
        nodes, edges, args.k, args.smoothing
    )

    draw(control_point_lists, nodes, edges, args.samples, args.plot_3d, draw_map,
         args.assets_dir, output_dir, args.step_size_3d, effective_tag)

    print(
        f"Evaluated {len(edges)} edges: {len(control_point_lists)} bundled, "
        f"{too_long} rejected as too long, {no_path} without alternative path."
    )


if __name__ == "__main__":
    main()
