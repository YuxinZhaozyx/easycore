from easycore.common.config import CfgNode
from easycore.common.parallel import OrderedRunner

class Runner(OrderedRunner):

    @staticmethod
    def producer_work(device, cfg, data):
        return data * data

    @staticmethod
    def consumer_init(cfg):
        cfg.data_list = []

    @staticmethod
    def consumer_work(cfg, data):
        cfg.data_list.append(data)

    @staticmethod
    def consumer_end(cfg):
        return cfg.data_list


def test_runner():
    runner = Runner(3)
    
    data_list = list(range(100))
    
    result = runner(data_list)

    assert result == [data * data for data in data_list]

    runner.close()

