from unittest import TestCase
from tgt_grease.core import ImportTool, Configuration, Logging
from mock import MagicMock, patch


class TestImporter(TestCase):
    def test_load(self):
        log = Logging()
        imp = ImportTool(log)
        Conf = imp.load("Configuration")
        self.assertTrue(isinstance(Conf, Configuration))

    def test_failed_path(self):
        log = Logging()
        imp = ImportTool(log)
        obj = imp.load("defaultdict")
        self.assertFalse(obj)

    @patch("tgt_grease.core.ImportTool._dir_contains")
    @patch("importlib.import_module")
    @patch("tgt_grease.core.ImportTool._get_attr")
    def test_init_exception(self, mock_getattr, mock_import, mock_dir_contains):
        log = Logging()
        imp = ImportTool(log)

        def raise_exception():
            raise Exception("Test Exception")

        d = {'times_called': 0} #Need mutable object for nonlocal updates
        def return_true_once(*args, **kwargs):
            d['times_called'] += 1
            return d['times_called'] == 1

        mock_dir_contains.side_effect = return_true_once
        mock_req = MagicMock()
        mock_req.side_effect = raise_exception
        mock_getattr.return_value = mock_req

        self.assertEqual(imp.load("mock_class"), None)
        mock_getattr.assert_called_once()
        mock_req.assert_called_once()
