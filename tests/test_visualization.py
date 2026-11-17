import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("prepare_visualization", ROOT / "scripts/prepare_visualization.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class VisualizationTests(unittest.TestCase):
    def fixture(self, root):
        source = root / "vendor/moleculardna"
        (source / "src").mkdir(parents=True)
        for name in ("DetectorConstruction.cc", "PhysicsList.cc"):
            (source / "src" / name).write_text("G4bool useParallelPhysicsWorld = false;\n")
        (source / "CMakeLists.txt").write_text('if (EXISTS "${GEOMETRY_FOlDER_NAME}")\nendif()\n' * 2)
        (source / "human_cell.mac").write_text(
            "/scheduler/endTime 5 ns\n/dnageom/definitionFile geometries/full.txt\n"
            "/dnageom/placementVolume straight geometries/straight.txt\n"
            "/dnageom/placementVolume turn geometries/turn.txt\n"
            "/dnageom/placementVolume turntwist geometries/twist.txt true\n"
            "/run/initialize\n/run/beamOn 10\n")
        (root / "build/molecular/geometries").mkdir(parents=True)
        (root / "build/molecular/geometries/cube-centred-X-8.txt").write_text("geometry")
        (root / "visualization").mkdir()
        (root / "visualization/human_cell_view.mac").write_text("/vis/drawVolume DNAWorld\n")
        return source

    def test_visual_copy_preserves_production_and_removes_events(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = self.fixture(root)
            before = {p.relative_to(source): p.read_bytes() for p in source.rglob("*") if p.is_file()}
            module.prepare(root)
            self.assertEqual(before, {p.relative_to(source): p.read_bytes() for p in source.rglob("*") if p.is_file()})
            target = root / "build/visualization-source"
            self.assertNotIn("/run/beamOn", (target / "human_cell_geometry.mac").read_text())
            self.assertIn("/run/initialize", (target / "human_cell_geometry.mac").read_text())
            for name in ("DetectorConstruction.cc", "PhysicsList.cc"):
                self.assertIn("useParallelPhysicsWorld = true", (target / "src" / name).read_text())
            self.assertEqual((target / "CMakeLists.txt").read_text().count("${PROJECT_BINARY_DIR}"), 2)
            self.assertEqual((target / "single_segment.txt").read_text().splitlines()[-1], "0 straight 0 0 0 0 0 0")
            self.assertEqual((target / "human_cell_geometry.mac").read_text().count("/dnageom/placementVolume"), 1)
            module.configure_view(root, "turn")
            self.assertIn("0 turn 0 0 0 0 0 0", (target / "single_segment.txt").read_text())
            with self.assertRaises(ValueError):
                module.prepare(root)

    def test_unexpected_sources_fail_before_creating_copy(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = self.fixture(root)
            (source / "src/PhysicsList.cc").write_text("unknown version")
            with self.assertRaises(ValueError):
                module.prepare(root)
            self.assertFalse((root / "build/visualization-source").exists())
