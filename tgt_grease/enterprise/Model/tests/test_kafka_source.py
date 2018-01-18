from unittest import TestCase
from unittest.mock import MagicMock, patch
from tgt_grease.core import GreaseContainer, Configuration
from tgt_grease.enterprise.Model import KafkaSource
import time
import multiprocessing as mp

class MockProcess():
    def __init__(self):
        self.alive = False
        self.daemon = False
        self.is_alive_called = 0
        self.start_called = 0

    def is_alive(self):
        self.is_alive_called += 1
        return self.alive

    def start(self):
        self.start_called += 1

class TestKafka(TestCase):

    def setUp(self):
        self.ioc = GreaseContainer()
        self.good_config = {"source": "kafka"}
        self.bad_config = {"source": "not kafka"}

    def test_run_bad_config(self):
        ks = KafkaSource()
        self.assertFalse(ks.run(self.bad_config))
        self.assertEqual(ks.configs, [])

    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_manager_proc')
    def test_run_good_config(self, mock_create):
        ks = KafkaSource()
        mock_proc = MockProcess()
        mock_create.return_value = mock_proc
        self.assertFalse(ks.run(self.good_config))
        self.assertEqual(ks.configs, [self.good_config])
        self.assertEqual(mock_proc.is_alive_called, 1)
    
    @patch('tgt_grease.enterprise.Model.KafkaSource.get_configs')
    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_manager_proc')
    def test_run_no_config(self, mock_create, mock_get_configs):
        ks = KafkaSource()
        mock_get_configs.return_value = [self.good_config]*5
        mock_proc = MockProcess()
        mock_create.return_value = mock_proc
        self.assertFalse(ks.run())
        self.assertEqual(ks.configs, [self.good_config]*5)
        self.assertEqual(mock_proc.is_alive_called, 5)

    @patch('tgt_grease.enterprise.Model.KafkaSource.make_consumer')
    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_proc')
    @patch('tgt_grease.enterprise.Model.KafkaSource.reallocate_consumers')
    def test_consumer_manager(self, mock_reallocate, mock_create, mock_make):
        mock_make.return_value = []
        mock_proc = MockProcess()
        mock_create.return_value = (mock_proc, None)
        ks = KafkaSource()
        self.assertFalse(ks.consumer_manager(self.ioc, self.good_config))
        self.assertEqual(mock_proc.is_alive_called, 1)
        mock_reallocate.assert_called_once()
        mock_make.assert_called_once()
        mock_create.assert_called_once

    @patch('tgt_grease.enterprise.Model.KafkaSource.make_consumer')
    def test_consume_empty_consumer(self, mock_make):
        # It's hard to test something that is designed to run forever, so going to test when the consumer is empty
        mock_make.return_value = []
        ks = KafkaSource()
        pipe1, pipe2 = mp.Pipe()
        self.assertFalse(ks.consume(self.ioc, self.good_config, pipe1))

    @patch('tgt_grease.enterprise.Model.KafkaSource.make_consumer')
    def test_consume_kill_signal(self, mock_make):
        # It's hard to test something that is designed to run forever, so going to test the pipe kill signal
        mock_make.return_value = ["consumer"]
        ks = KafkaSource()
        pipe1, pipe2 = mp.Pipe()
        pipe1.send("STOP")
        self.assertFalse(ks.consume(self.ioc, self.good_config, pipe1))

    def test_sleep(self):
        sleep_time = 1.
        ks = KafkaSource()
        now = time.time()
        ks.sleep(sleep_time)
        wake = time.time()
        self.assertTrue(wake-now >= sleep_time)
        self.assertTrue(wake-now < sleep_time + .1)

    def test_parse_message_key_present(self):
        parse_config = {
            "source": "kafka",
            "key_aliases": {"a.b.c": "key"}
        }
        message = {"a": {"b": {"c": "value"}}}
        expected = {"key": "value"}
        ks = KafkaSource()
        self.assertEqual(ks.parse_message(self.ioc, parse_config, message), expected)
    
    def test_parse_message_key_present_split(self):
        parse_config = {
            "source": "kafka",
            "split_char": "@@", 
            "key_aliases": {"a@@b@@c": "key"}
        }
        message = {"a": {"b": {"c": "value"}}}

        expected = {"key": "value"}
        ks = KafkaSource()
        self.assertEqual(ks.parse_message(self.ioc, parse_config, message), expected)
    
    def test_parse_message_key_missing(self):
        parse_config = {
            "source": "kafka",
            "key_aliases": {"a.b.c": "key"}
        }
        message = {"a": {"b": {"d": "value"}}}
        expected = {}
        ks = KafkaSource()
        self.assertEqual(ks.parse_message(self.ioc, parse_config, message), expected)

    def test_parse_message_key_missing_split(self):
        parse_config = {
            "source": "kafka",
            "split_char": "@@", 
            "key_aliases": {"a@@b@@c": "key"}
        }
        message = {"a": {"b": {"d": "value"}}}
        expected = {}
        ks = KafkaSource()
        self.assertEqual(ks.parse_message(self.ioc, parse_config, message), expected)

    def test_parse_message_keys_present(self):
        parse_config = {
            "source": "kafka", 
            "key_aliases": {"a.b.c": "abc_key",
                            "a.b.d": "abd_key",
                            "aa": "aa_key"
                            }
        }
        message = {"a": {"b": {"c": "cvalue", "d":"dvalue"}}, "aa": "aavalue"}
        expected = {"abc_key": "cvalue", "abd_key": "dvalue", "aa_key": "aavalue"}
        ks = KafkaSource()
        self.assertEqual(ks.parse_message(self.ioc, parse_config, message), expected)

    def test_parse_message_keys_missing(self):
        parse_config = {
            "source": "kafka", 
            "key_aliases": {"a.b.c": "abc_key",
                            "a.b.d": "abd_key",
                            "aa": "aa_key"
                            }
        }
        message = {"a": {"b": {"c": "cvalue"}}, "aa": "aavalue"}
        expected = {}
        ks = KafkaSource()
        self.assertEqual(ks.parse_message(self.ioc, parse_config, message), expected)

    def test_parse_message_duplicate_alias(self):
        parse_config = {
            "source": "kafka", 
            "key_aliases": {"a.b.c": "key",
                            "a.b.d": "key"
                            }
        }
        message = {"a": {"b": {"c": "cvalue"}}, "aa": "aavalue"}
        expected = {}
        ks = KafkaSource()
        errored = False
        try:
            ks.parse_message(self.ioc, parse_config, message)
        except:
            errored = True
        self.assertTrue(errored)

    @patch('tgt_grease.enterprise.Model.KafkaSource.sleep')
    @patch('tgt_grease.enterprise.Model.KafkaSource.kill_consumer_proc')
    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_proc')
    @patch('tgt_grease.enterprise.Model.KafkaSource.get_backlog')
    def test_reallocate_consumers_kill(self, mock_backlog, mock_create, mock_kill, mock_sleep):
        mock_backlog.return_value = 3
        ks = KafkaSource()
        self.assertEqual(ks.reallocate_consumers(self.ioc, self.good_config, None, ["proc1", "proc2"]), -1)
        mock_kill.assert_called_once_with(self.ioc, "proc1")
        self.assertEqual(mock_backlog.call_count, 2)
        mock_create.assert_not_called()

    @patch('tgt_grease.enterprise.Model.KafkaSource.sleep')
    @patch('tgt_grease.enterprise.Model.KafkaSource.kill_consumer_proc')
    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_proc')
    @patch('tgt_grease.enterprise.Model.KafkaSource.get_backlog')
    def test_reallocate_consumers_kill_1proc(self, mock_backlog, mock_create, mock_kill, mock_sleep):
        mock_backlog.return_value = 3
        ks = KafkaSource()
        self.assertEqual(ks.reallocate_consumers(self.ioc, self.good_config, None, ["proc1"]), 0)
        mock_kill.assert_not_called()
        self.assertEqual(mock_backlog.call_count, 2)
        mock_create.assert_not_called()

    @patch('tgt_grease.enterprise.Model.KafkaSource.sleep')
    @patch('tgt_grease.enterprise.Model.KafkaSource.kill_consumer_proc')
    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_proc')
    @patch('tgt_grease.enterprise.Model.KafkaSource.get_backlog')
    def test_reallocate_consumers_create(self, mock_backlog, mock_create, mock_kill, mock_sleep):
        mock_backlog.return_value = 21
        mock_create.return_value = "new_proc"
        ks = KafkaSource()
        procs = ["proc1"]
        self.assertEqual(ks.reallocate_consumers(self.ioc, self.good_config, None, procs), 1)
        mock_kill.assert_not_called()
        self.assertEqual(mock_backlog.call_count, 2)
        mock_create.assert_called_once_with(self.ioc, self.good_config)
        self.assertTrue("new_proc" in procs)

    @patch('tgt_grease.enterprise.Model.KafkaSource.sleep')
    @patch('tgt_grease.enterprise.Model.KafkaSource.kill_consumer_proc')
    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_proc')
    @patch('tgt_grease.enterprise.Model.KafkaSource.get_backlog')
    def test_reallocate_consumers_pass(self, mock_backlog, mock_create, mock_kill, mock_sleep):
        mock_backlog.return_value = 10
        ks = KafkaSource()
        self.assertEqual(ks.reallocate_consumers(self.ioc, self.good_config, None, ["proc1"]), 0)
        mock_kill.assert_not_called()
        mock_create.assert_not_called()
        self.assertEqual(mock_backlog.call_count, 2)

    @patch('tgt_grease.enterprise.Model.KafkaSource.sleep')
    def test_kill_consumer_proc(self, mock_sleep):
        conn1, conn2 = mp.Pipe()
        ks = KafkaSource()
        ks.kill_consumer_proc(self.ioc, (None, conn1))
        self.assertEqual(conn2.recv(), "STOP")

    def test_get_backlog(self):
        pass

    def test_send_to_scheduling(self):
        pass

    def test_get_configs(self):
        pass

    def test_create_consumer_manager_proc(self):
        pass

    def test_create_consumer_proc(self):
        pass
   
    def test_make_consumer(self):
        pass
