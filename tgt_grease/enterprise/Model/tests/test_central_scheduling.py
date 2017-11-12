from unittest import TestCase
from tgt_grease.core import GreaseContainer
from tgt_grease.enterprise.Model import Scheduling


class TestScheduling(TestCase):

    def test_empty_source_schedule(self):
        ioc = GreaseContainer()
        sch = Scheduling(ioc)
        self.assertFalse(sch.ScheduleSource([]))
