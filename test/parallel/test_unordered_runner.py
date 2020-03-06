from easycore.common.config import CfgNode
from easycore.common.parallel import UnorderedRunner

class Runner(UnorderedRunner):

    @staticmethod
    def producer_work(device, cfg, data):
        return data * data

    @staticmethod
    def consumer_init(cfg):
        cfg.sum = 0

    @staticmethod
    def consumer_work(cfg, data):
        cfg.sum += data

    @staticmethod
    def consumer_end(cfg):
        return cfg.sum


def test_runner():
    runner = Runner(devices=3)
    
    data_list = list(range(100))
    
    result = runner(data_list)
    
    assert result == sum([data * data for data in data_list])

    runner.close()
