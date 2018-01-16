from unittest import TestCase
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

    def __init__(self, x):
        super(TestKafka, self).__init__(x)
        self.ioc = GreaseContainer()
        self.good_config = {"source": "kafka"}
        self.bad_config = {"source": "not kafka"}

    def test_run_bad_config(self):
        ks = KafkaSource()
        self.assertFalse(ks.run(self.bad_config))
        self.assertEqual(ks.configs, [])

    def test_run_good_config(self):
        ks = KafkaSource()
        mock_proc = MockProcess()
        ks.create_consumer_manager_proc = lambda x: mock_proc
        self.assertFalse(ks.run(self.good_config))
        self.assertEqual(ks.configs, [self.good_config])
        self.assertEqual(mock_proc.is_alive_called, 1)
    
    def test_run_no_config(self):
        ks = KafkaSource()
        ks.get_configs = lambda: [self.good_config]*5
        mock_proc = MockProcess()
        ks.create_consumer_manager_proc = lambda x: mock_proc
        self.assertFalse(ks.run())
        self.assertEqual(ks.configs, [self.good_config]*5)
        self.assertEqual(mock_proc.is_alive_called, 5)

    def test_consumer_manager(self):
        KafkaSource.make_consumer = lambda x, y: []
        mock_proc = MockProcess()
        KafkaSource.create_consumer_proc  = lambda x, y: (mock_proc, None)
        KafkaSource.reallocate_consumers = lambda a, b, c, d: True
        ks = KafkaSource()
        self.assertFalse(ks.consumer_manager(self.ioc, self.good_config))
        self.assertEqual(mock_proc.is_alive_called, 1)

    def test_consume(self):
        pass

    def test_sleep(self):
        pass

    def test_make_consumer(self):
        pass

    def test_parse_message(self):
        pass

    def test_reallocate_consumers(self):
        pass

    def test_kill_consumer_proc(self):
        pass

    def test_get_backlog(self):
        pass

    def test_send_to_scheduling(self):
        pass

    def test_get_configs(self):
        pass
   