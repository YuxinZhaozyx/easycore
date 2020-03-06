from easycore.common.config import CfgNode
from easycore.torch.parallel import OrderedRunner
import torch
import torch.nn as nn
import torch.nn.functional as F

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc = nn.Linear(1, 3)
    
    def forward(self, x):
        x = self.fc(x)
        x = F.relu(x)
        return x


def batch_generator(data_list, batch_size):
    for i in range(0, len(data_list), batch_size):
        data_batch = data_list[i : i+batch_size]
        yield data_batch


class Runner(OrderedRunner):

    @staticmethod
    def producer_init(device, cfg):
        cfg.model = Net()
        cfg.model.to(device)

    @staticmethod
    def producer_work(device, cfg, data):
        with torch.no_grad():
            data = torch.Tensor(data).view(-1,1)
            data = data.to(device)
            output = cfg.model(data)
            output = output.cpu()
        return output

    @staticmethod
    def producer_end(device, cfg):
        del cfg.model

    @staticmethod
    def consumer_init(cfg):
        cfg.data_list = []

    @staticmethod
    def consumer_work(cfg, data):
        cfg.data_list.append(data)

    @staticmethod
    def consumer_end(cfg):
        data = torch.cat(cfg.data_list, dim=0)
        return data

def test_runner():
    runner = Runner(devices=["cpu", "cpu"])
    
    data_list = list(range(100))
    
    result = runner(batch_generator(data_list, 10))
    
    assert tuple(result.shape) == (100, 3)
    
    runner.close()
