from easycore.common.config import CfgNode
from easycore.common.parallel import OrderedRunner
import time

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


if __name__ == '__main__':

    
    runner = Runner(3)
    
    data_list = list(range(100))
    
    start_time = time.time()
    result = runner(data_list)
    end_time = time.time()
    
    print(result)
    print(end_time - start_time, "s")

    runner.close()
