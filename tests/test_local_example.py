import importlib.util
import json
from pathlib import Path
import shutil
import unittest
import uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("local_example", ROOT / "scripts/local_example.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class LocalExampleTests(unittest.TestCase):
    def setUp(self):
        self.folder = ROOT / "tests" / ("scratch_" + uuid.uuid4().hex)
        self.source = self.folder / "installed/share/Geant4-11.3.0/examples/advanced/dna/moleculardna"
        self.source.mkdir(parents=True)
        for name in ("CMakeLists.txt", "molecular.cc", "human_cell.mac"):
            (self.source / name).write_text("test fixture")
        for name in ("src", "include", "geometries"):
            (self.source / name).mkdir()
        for name in m.REQUIRED_GEOMETRY:
            (self.source / "geometries" / name).write_text("local geometry fixture")
        self.prefix = self.folder / "installed"
        self.repo = self.folder / "work"

    def tearDown(self):
        shutil.rmtree(self.folder)

    def test_discover_copy_and_verify_local_install(self):
        self.assertEqual(m.discover(self.prefix), self.source.resolve())
        with patch.object(m, "REPO", self.repo):
            m.copy_example(self.prefix)
            m.verify()
        record = json.loads((self.repo / "vendor/source.json").read_text())
        self.assertEqual(record["source_kind"], "local-geant4-installation")
        self.assertEqual((self.repo / "vendor/moleculardna/molecular.cc").read_text(), "test fixture")
        self.assertIn("human_cell.mac", record["files_sha256"])
        self.assertNotIn("geometries/cube-centred-X-8.txt", record["files_sha256"])

    def test_allow_copy_before_cmake_prepares_geometries(self):
        shutil.rmtree(self.source / "geometries")
        with patch.object(m, "REPO", self.repo):
            m.copy_example(self.prefix)
            m.verify(sources_only=True)
            with self.assertRaisesRegex(ValueError, "Faltan geometrías"):
                m.verify()
        self.assertTrue((self.repo / "vendor/moleculardna").exists())

    def test_refuse_overwrite_and_detect_changed_sources(self):
        with patch.object(m, "REPO", self.repo):
            m.copy_example(self.prefix)
            with self.assertRaisesRegex(ValueError, "No se sobrescribe"):
                m.copy_example(self.prefix)
            (self.repo / "vendor/moleculardna/molecular.cc").write_text("changed")
            with self.assertRaisesRegex(ValueError, "cambiaron"):
                m.verify()

    def test_explicit_geometry_directory(self):
        separate = self.folder / "shared-geometries"
        shutil.move(str(self.source / "geometries"), separate)
        with patch.object(m, "REPO", self.repo):
            m.copy_example(self.prefix, self.source, separate)
            m.verify()
