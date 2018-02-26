from unittest import TestCase
from mock import MagicMock, patch
from tgt_grease.core import GreaseContainer, Configuration
from tgt_grease.enterprise.Model import KafkaSource
import time
import kafka
import multiprocessing as mp

class MockThread():
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
        self.good_config = {"source": "kafka", "max_backlog": 20, "min_backlog": 5, "servers": ["server"], "topics": ["topic"]}
        self.bad_config = {"source": "not kafka"}
        self.mock_thread = MagicMock()
        self.ks = KafkaSource()

    @patch('tgt_grease.enterprise.Model.KafkaSource.validate_configs')
    def test_run_bad_config(self, mock_validate):
        mock_validate.return_value = False
        self.assertFalse(self.ks.run(self.bad_config))

    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_manager_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.validate_configs')
    def test_run_good_config(self, mock_validate, mock_create):
        mock_thread = MockThread()
        mock_create.return_value = mock_thread
        mock_validate.return_value = True
        self.assertFalse(self.ks.run(self.good_config))
        self.assertEqual(self.ks.configs, [self.good_config])
        self.assertEqual(mock_thread.is_alive_called, 1)

    @patch('tgt_grease.enterprise.Model.KafkaSource.get_configs')
    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_manager_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.validate_configs')
    def test_run_no_config(self, mock_validate, mock_create, mock_get_configs):
        mock_get_configs.return_value = [self.good_config]*5
        mock_thread = MockThread()
        mock_create.return_value = mock_thread
        mock_validate.return_value = True
        self.assertFalse(self.ks.run())
        self.assertEqual(self.ks.configs, [self.good_config]*5)
        self.assertEqual(mock_thread.is_alive_called, 5)

    @patch('tgt_grease.enterprise.Model.KafkaSource.get_configs')
    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_manager_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.validate_configs')
    def test_run_invalid_config(self, mock_validate, mock_create, mock_get_configs):
        mock_get_configs.return_value = [self.good_config]*5
        mock_thread = MockThread()
        mock_create.return_value = mock_thread
        mock_validate.return_value = False
        self.assertFalse(self.ks.run())
        self.assertEqual(self.ks.configs, [self.good_config]*5)
        self.assertEqual(mock_thread.is_alive_called, 0)

    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer')
    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.reallocate_consumers')
    def test_consumer_manager(self, mock_reallocate, mock_create, mock_make):
        mock_make.return_value = []
        mock_thread = MockThread()
        mock_create.return_value = (mock_thread, None)
        self.assertFalse(self.ks.consumer_manager(self.ioc, self.good_config))
        self.assertEqual(mock_thread.is_alive_called, 1)
        self.assertEqual(mock_reallocate.call_count, 1)
        self.assertEqual(mock_make.call_count, 1)
        self.assertEqual(mock_create.call_count, 1)

    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer')
    def test_consume_empty_consumer(self, mock_make):
        # It's hard to test something that is designed to run forever, so going to test when the consumer is empty
        mock_make.return_value = []
        pipe1, pipe2 = mp.Pipe()
        self.assertFalse(self.ks.consume(self.ioc, self.good_config, pipe1))

    @patch('tgt_grease.enterprise.Model.KafkaSource.parse_message')
    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer')
    def test_consume_kill_signal(self, mock_make, mock_parse):
        # It's hard to test something that is designed to run forever, so going to test the pipe kill signal
        mock_make.return_value = ["consumer"]
        pipe1, pipe2 = mp.Pipe()
        pipe1.send("STOP")
        self.assertFalse(self.ks.consume(self.ioc, self.good_config, pipe2))
        mock_parse.assert_not_called()

    def test_sleep(self):
        sleep_time = 1.
        now = time.time()
        self.ks.sleep(sleep_time)
        wake = time.time()
        self.assertTrue(wake-now >= sleep_time)
        self.assertTrue(wake-now < sleep_time + .1)

    def test_parse_message_key_present(self):
        parse_config = {
            "source": "kafka",
            "key_aliases": {"a.b.c": "key"}
        }
        message = MagicMock()
        MagicMock.value = '{"a": {"b": {"c": "value"}}}'
        expected = {"key": "value"}
        self.assertEqual(self.ks.parse_message(self.ioc, parse_config, message), expected)

    def test_parse_message_invalid_json(self):
        parse_config = {
            "source": "kafka",
            "key_aliases": {"a.b.c": "key"}
        }
        message = MagicMock()
        MagicMock.value = '{"a": {"b": {"c": "value"'
        expected = {}
        self.assertEqual(self.ks.parse_message(self.ioc, parse_config, message), expected)

    def test_parse_message_key_present_split(self):
        parse_config = {
            "source": "kafka",
            "key_sep": "@@",
            "key_aliases": {"a@@b@@c": "key"}
        }
        message = MagicMock()
        MagicMock.value = '{"a": {"b": {"c": "value"}}}'

        expected = {"key": "value"}
        self.assertEqual(self.ks.parse_message(self.ioc, parse_config, message), expected)

    def test_parse_message_key_missing(self):
        parse_config = {
            "source": "kafka",
            "key_aliases": {"a.b.c": "key"}
        }
        message = MagicMock()
        MagicMock.value = '{"a": {"b": {"d": "value"}}}'
        expected = {}
        self.assertEqual(self.ks.parse_message(self.ioc, parse_config, message), expected)

    def test_parse_message_key_missing_split(self):
        parse_config = {
            "source": "kafka",
            "split_char": "@@",
            "key_aliases": {"a@@b@@c": "key"}
        }
        message = MagicMock()
        MagicMock.value = '{"a": {"b": {"d": "value"}}}'
        expected = {}
        self.assertEqual(self.ks.parse_message(self.ioc, parse_config, message), expected)

    def test_parse_message_keys_present(self):
        parse_config = {
            "source": "kafka",
            "key_aliases": {"a.b.c": "abc_key",
                            "a.b.d": "abd_key",
                            "aa": "aa_key"
                           }
        }
        message = MagicMock()
        MagicMock.value = '{"a": {"b": {"c": "cvalue", "d":"dvalue"}}, "aa": "aavalue"}'
        expected = {"abc_key": "cvalue", "abd_key": "dvalue", "aa_key": "aavalue"}
        self.assertEqual(self.ks.parse_message(self.ioc, parse_config, message), expected)

    def test_parse_message_keys_missing(self):
        parse_config = {
            "source": "kafka",
            "key_aliases": {"a.b.c": "abc_key",
                            "a.b.d": "abd_key",
                            "aa": "aa_key"
                           }
        }
        message = MagicMock()
        MagicMock.value = '{"a": {"b": {"c": "cvalue"}}, "aa": "aavalue"}'
        expected = {}
        self.assertEqual(self.ks.parse_message(self.ioc, parse_config, message), expected)

    @patch('tgt_grease.enterprise.Model.KafkaSource.sleep')
    @patch('tgt_grease.enterprise.Model.KafkaSource.kill_consumer_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.get_backlog')
    def test_reallocate_consumers_kill(self, mock_backlog, mock_create, mock_kill, mock_sleep):
        mock_backlog.return_value = 3
        self.assertEqual(self.ks.reallocate_consumers(self.ioc, self.good_config, None, ["thread1", "thread2"]), -1)
        mock_kill.assert_called_once_with(self.ioc, "thread1")
        self.assertEqual(mock_backlog.call_count, 2)
        mock_create.assert_not_called()

    @patch('tgt_grease.enterprise.Model.KafkaSource.sleep')
    @patch('tgt_grease.enterprise.Model.KafkaSource.kill_consumer_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.get_backlog')
    def test_reallocate_consumers_kill_1thread(self, mock_backlog, mock_create, mock_kill, mock_sleep):
        mock_backlog.return_value = 3
        self.assertEqual(self.ks.reallocate_consumers(self.ioc, self.good_config, None, ["thread1"]), 0)
        mock_kill.assert_not_called()
        self.assertEqual(mock_backlog.call_count, 2)
        mock_create.assert_not_called()

    @patch('tgt_grease.enterprise.Model.KafkaSource.sleep')
    @patch('tgt_grease.enterprise.Model.KafkaSource.kill_consumer_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.get_backlog')
    def test_reallocate_consumers_create(self, mock_backlog, mock_create, mock_kill, mock_sleep):
        mock_backlog.return_value = 21
        mock_create.return_value = "new_thread"
        threads = ["thread1"]
        self.assertEqual(self.ks.reallocate_consumers(self.ioc, self.good_config, None, threads), 1)
        mock_kill.assert_not_called()
        self.assertEqual(mock_backlog.call_count, 2)
        mock_create.assert_called_once_with(self.ioc, self.good_config)
        self.assertTrue("new_thread" in threads)

    @patch('tgt_grease.enterprise.Model.KafkaSource.sleep')
    @patch('tgt_grease.enterprise.Model.KafkaSource.kill_consumer_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.get_backlog')
    def test_reallocate_consumers_pass(self, mock_backlog, mock_create, mock_kill, mock_sleep):
        mock_backlog.return_value = 10
        self.assertEqual(self.ks.reallocate_consumers(self.ioc, self.good_config, None, ["thread1"]), 0)
        mock_kill.assert_not_called()
        mock_create.assert_not_called()
        self.assertEqual(mock_backlog.call_count, 2)


    @patch('tgt_grease.enterprise.Model.KafkaSource.sleep')
    @patch('tgt_grease.enterprise.Model.KafkaSource.kill_consumer_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.get_backlog')
    def test_reallocate_consumers_max_thread(self, mock_backlog, mock_create, mock_kill, mock_sleep):
        mock_backlog.return_value = 30
        threads = ["thread" for i in range(0, 32)]
        self.assertEqual(self.ks.reallocate_consumers(self.ioc, self.good_config, None, threads), 0)
        mock_kill.assert_not_called()
        mock_create.assert_not_called()
        self.assertEqual(mock_backlog.call_count, 2)

    @patch('tgt_grease.enterprise.Model.KafkaSource.sleep')
    @patch('tgt_grease.enterprise.Model.KafkaSource.kill_consumer_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.get_backlog')
    def test_reallocate_consumers_max_thread_create(self, mock_backlog, mock_create, mock_kill, mock_sleep):
        mock_backlog.return_value = 30
        threads = ["thread" for i in range(0, 33)]
        config = {"max_consumers": 35, "max_backlog":20, "min_backlog":5}
        self.assertEqual(self.ks.reallocate_consumers(self.ioc, config, None, threads), 1)
        mock_kill.assert_not_called()
        mock_create.assert_called()
        self.assertEqual(mock_backlog.call_count, 2)

    @patch('tgt_grease.enterprise.Model.KafkaSource.sleep')
    @patch('tgt_grease.enterprise.Model.KafkaSource.kill_consumer_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.create_consumer_thread')
    @patch('tgt_grease.enterprise.Model.KafkaSource.get_backlog')
    def test_reallocate_consumers_max_thread_pass(self, mock_backlog, mock_create, mock_kill, mock_sleep):
        mock_backlog.return_value = 30
        threads = ["thread" for i in range(0, 36)]
        config = {"max_consumers": 35, "max_backlog":20, "min_backlog":5}
        self.assertEqual(self.ks.reallocate_consumers(self.ioc, config, None, threads), 0)
        mock_kill.assert_not_called()
        mock_create.assert_not_called()
        self.assertEqual(mock_backlog.call_count, 2)

    @patch('tgt_grease.enterprise.Model.KafkaSource.sleep')
    def test_kill_consumer_thread(self, mock_sleep):
        conn1, conn2 = mp.Pipe()
        self.ks.kill_consumer_thread(self.ioc, (None, conn1))
        self.assertEqual(conn2.recv(), "STOP")

    def test_get_backlog_happy(self):
        mock_consumer = MagicMock()
        for part_count in range(1, 10):
            for start in range(0, 10):
                for end in range(start, 10):
                    mock_partitions = ["part" + str(part_i) for part_i in range(part_count)] # assignment returns an array of TopicPartitions, but our mocked consumer works with just strings
                    mock_consumer.assignment.return_value = mock_partitions
                    mock_consumer.position.return_value = start
                    mock_consumer.end_offsets.return_value = {part:end for part in mock_partitions}
                    expected_average = end - start
                    res = self.ks.get_backlog(self.ioc, mock_consumer)
                    self.assertTrue(isinstance(res, float))
                    self.assertEqual(res, expected_average)

    def test_get_backlog_not_assigned(self):
        mock_consumer = MagicMock()
        assigned = {"status": False}

        def poll():
            assigned["status"] = True

        mock_consumer.poll.side_effect = poll
        for part_count in range(1, 10):
            for start in range(0, 10):
                for end in range(start, 10):
                    mock_partitions = ["part" + str(part_i) for part_i in range(part_count)] # assignment returns an array of TopicPartitions, but our mocked consumer works with just strings
                    def assignment():
                        if assigned["status"]:
                            return mock_partitions
                        else:
                            return []

                    mock_consumer.assignment.side_effect = assignment
                    mock_consumer.position.return_value = start
                    mock_consumer.end_offsets.return_value = {part:end for part in mock_partitions}
                    expected_average = end - start
                    res = self.ks.get_backlog(self.ioc, mock_consumer)
                    self.assertTrue(isinstance(res, float))
                    self.assertEqual(res, expected_average)

    def test_get_backlog_no_assign(self):
        mock_consumer = MagicMock()
        mock_consumer.assignment.return_value = []
        self.assertEqual(self.ks.get_backlog(self.ioc, mock_consumer), -1.)

    def test_get_backlog_position_error(self):
        mock_consumer = MagicMock()
        mock_consumer.assignment.return_value = ["part"]
        mock_consumer.position.side_effect = kafka.errors.KafkaTimeoutError()
        mock_consumer.end_offsets.return_value = {"part": 1}
        self.assertEqual(self.ks.get_backlog(self.ioc, mock_consumer), -1.)

    def test_get_backlog_end_offsets_error(self):
        mock_consumer = MagicMock()
        mock_consumer.assignment.return_value = ["part"]
        mock_consumer.position.return_value = 1
        mock_consumer.end_offsets.side_effect  = kafka.errors.UnsupportedVersionError()
        self.assertEqual(self.ks.get_backlog(self.ioc, mock_consumer), -1.)

    @patch("tgt_grease.enterprise.Model.CentralScheduling.Scheduling.scheduleDetection")
    def test_send_to_scheduling_happy(self, mock_scheduling):
        config = {
            "source": "kafka",
            "name": "test_config"
        }
        mock_msg = {"a": "b"}
        mock_scheduling.return_value = True
       
        self.assertTrue(self.ks.send_to_scheduling(self.ioc, config, mock_msg))
        mock_scheduling.assert_called_once_with("kafka", "test_config", mock_msg)

    @patch("tgt_grease.enterprise.Model.CentralScheduling.Scheduling.scheduleDetection")
    def test_send_to_scheduling_sad(self, mock_scheduling):
        config = {
            "source": "kafka",
            "name": "test_config"
        }
        mock_msg = {"a": "b"}
        mock_scheduling.return_value = False
        self.assertFalse(self.ks.send_to_scheduling(self.ioc, config, mock_msg))
        mock_scheduling.assert_called_once_with("kafka", "test_config", mock_msg)

    @patch("threading.Thread")
    def test_create_consumer_manager_thread(self, mock_thread):
        mockp = MockThread()
        mock_thread.return_value = mockp
        self.assertEqual(self.ks.create_consumer_manager_thread(self.good_config), mockp)
        self.assertEqual(mockp.is_alive_called, 0)
        self.assertEqual(mockp.start_called, 1)
        self.assertFalse(mockp.daemon)

    @patch("threading.Thread")
    def test_create_consumer_thread(self, mock_thread):
        mockp = MockThread()
        mock_thread.return_value = mockp
        thread, pipe = self.ks.create_consumer_thread(self.ioc, self.good_config)
        self.assertEqual(thread, mockp)
        self.assertEqual(type(pipe), type(mp.Pipe()[0]))
        self.assertEqual(mockp.is_alive_called, 0)
        self.assertEqual(mockp.start_called, 1)
        self.assertTrue(mockp.daemon)

    def test_validate_configs_happy(self):
        good_config = {
            "name": "kafka_config",
            "source": "kafka",
            "key_aliases": {
                "a*b*c": "abc_key",
                "a*b*d": "abd_key"
            },
            "key_sep": "*",         #opt
            "max_consumers": 32,    #opt
            "topics": [
                "topic1",
                "topic2"
            ],
            "servers": [
                "server.target.com:1234"
            ],
            "max_backlog": 200,     #opt
            "min_backlog": 100      #opt
        }

        self.assertTrue(self.ks.validate_configs([good_config]))
        self.assertTrue(self.ks.validate_configs([good_config]*5))

    def test_validate_configs_wrong_source(self):
        config = {
            "name": "kafka_config",
            "source": "not kafka",
            "key_aliases": {
                "a*b*c": "abc_key",
                "a*b*d": "abd_key"
            },
            "key_sep": "*",         #opt
            "max_consumers": 32,    #opt
            "topics": [
                "topic1",
                "topic2"
            ],
            "servers": [
                "server.target.com:1234"
            ],
            "max_backlog": 200,     #opt
            "min_backlog": 100      #opt
        }

        self.assertFalse(self.ks.validate_configs([config]))
        self.assertFalse(self.ks.validate_configs([config]*5))

    def test_validate_configs_duplicate_aliases(self):
        config = {
            "name": "kafka_config",
            "source": "kafka",
            "key_aliases": {
                "a*b*c": "key",
                "a*b*d": "key"
            },
            "key_sep": "*",         #opt
            "max_consumers": 32,    #opt
            "topics": [
                "topic1",
                "topic2"
            ],
            "servers": [
                "server.target.com:1234"
            ],
            "max_backlog": 200,     #opt
            "min_backlog": 100      #opt
        }

        self.assertFalse(self.ks.validate_configs([config]))
        self.assertFalse(self.ks.validate_configs([config]*5))

    def test_validate_configs_wrong_types(self):
        config = {
            "name": "kafka_config",
            "source": "kafka",
            "key_aliases": {
                "a*b*c": "abc_key",
                "a*b*d": "abd_key"
            },
            "key_sep": 11,         #opt
            "max_consumers": "32", #opt
            "topics": [
                "topic1",
                "topic2"
            ],
            "servers": [
                "server.target.com:1234"
            ],
            "max_backlog": 200,     #opt
            "min_backlog": 100      #opt
        }

        self.assertFalse(self.ks.validate_configs([config]))
        self.assertFalse(self.ks.validate_configs([config]*5))

    def test_validate_configs_key_missing(self):
        config = {
            "name": "kafka_config",
            "source": "kafka",
            "key_sep": "*",         #opt
            "max_consumers": 32,    #opt
            "topics": [
                "topic1",
                "topic2"
            ],
            "servers": [
                "server.target.com:1234"
            ],
            "max_backlog": 200,     #opt
            "min_backlog": 100      #opt
        }

        self.assertFalse(self.ks.validate_configs([config]))
        self.assertFalse(self.ks.validate_configs([config]*5))

    def test_validate_configs_empty_keys(self):
        config = {
            "name": "kafka_config",
            "source": "kafka",
            "key_aliases": {},
            "key_sep": "*",         #opt
            "max_consumers": 32,    #opt
            "topics": [],
            "servers": [],
            "max_backlog": 200,     #opt
            "min_backlog": 100      #opt
        }

        self.assertFalse(self.ks.validate_configs([config]))
        self.assertFalse(self.ks.validate_configs([config]*5))

    def test_validate_configs_no_opt(self):
        config = {
            "name": "kafka_config",
            "source": "kafka",
            "key_aliases": {
                "a*b*c": "abc_key",
                "a*b*d": "abd_key"
            },
            "topics": [
                "topic1",
                "topic2"
            ],
            "servers": [
                "server.target.com:1234"
            ]
        }

        self.assertTrue(self.ks.validate_configs([config]))
        self.assertTrue(self.ks.validate_configs([config]*5))
