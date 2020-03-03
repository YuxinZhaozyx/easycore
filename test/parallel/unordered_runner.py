from easycore.common.config import CfgNode
from easycore.common.parallel import UnorderedRunner
import time

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


if __name__ == '__main__':
    runner = Runner(devices=3)
    
    data_list = list(range(100))
    
    start_time = time.time()
    result = runner(data_list)
    end_time = time.time()
    
    print(result)
    print(end_time - start_time, "s")

    runner.close()
