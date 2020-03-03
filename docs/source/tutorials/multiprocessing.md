# Multiprocessing parallel acceleration tools

**easycore** make it easy to parallel your tasks in cpus and gpus.

## API

You can write a parallel runner by inheriting class [`UnorderedRunner`](../modules/easycore.common.parallel.html#easycore.common.parallel.UnorderedRunner) or [`OrderedRunner`](../modules/easycore.common.parallel.html#easycore.common.parallel.OrderedRunner) and overriding following 6 static methods.

```python
@staticmethod
def producer_init(device, cfg):
    """ 
    function for producer initialization.
    
    Args:
        device (str): device for the this process.
        cfg (easycore.common.config.CfgNode): config of this process, you can use it to transfer data
            to `producer_work` and `producer_end` function.
    """
    pass

@staticmethod
def producer_work(device, cfg, data):
    """ 
    function specify how the producer processes the data.
    
    Args:
        device (str): device for this process.
        cfg (easycore.common.config.CfgNode): config of this process, you can use it to get data from
            `producer_init` function and transfer data to the next `producer_work` and `producer_end`
            function.
        data (Any): data get from input of `__call__` method.
    
    Returns:
        Any: processed data
    """
    return data

@staticmethod
def producer_end(device, cfg):
    """ 
    function after finishing all of its task and before close the process.
    
    Args:
        device (str): device for this process.
        cfg (easycore.common.config.CfgNode): config of this process, you can use it to get data
            from `producer_init` and `producer_work` function.
    """
    pass

@staticmethod
def consumer_init(cfg):
    """
    function for consumer initialization.
    
    Args:
        cfg (easycore.common.config.CfgNode): config of this process, you can use it to transfer data
            to `consumer_work` and `consumer_end` function.
    """
    pass

@staticmethod
def consumer_work(cfg, data):
    """
    function specify how the consumer processses the data from producers.
    
    Args:
        cfg (easycore.common.config.CfgNode): config of this process, you can use it to get data from
            `consumer_init` function and transfer data to the next `consumer_work` and `consumer_end`
            function.
    """
    pass

@staticmethod
def consumer_end(cfg):
    """
    function after receiving all data from producers.
    
    Args:
        cfg (easycore.common.config.CfgNode): config of this process, you can use it get data from
            `consumer_work` function.

    Returns:
        Any: processed data
    """
    return None
```

## Example 1: Sum of squares

It can be implemented with a simple way:

```python
data_list = list(range(100))
result = sum([data * data for data in data_list])

# or more simple
result = 0
for data in data_list:
    square = data * data
    result += square
```

We calculate square of each element of the list, and then sum they together. In this case, it can be divided into two tasks. We assign this two tasks to producer and consumer respectively.

```python
from easycore.common.config import CfgNode
from easycore.common.parallel import UnorderedRunner

class Runner(UnorderedRunner):
    @staticmethod
    def producer_work(device, cfg, data):
        return data * data  # calculate square of data

    @staticmethod
    def consumer_init(cfg):
        cfg.sum = 0  # init a sum variable with 0, you can use cfg to transfer data

    @staticmethod
    def consumer_work(cfg, data):
        cfg.sum += data  # add the square to the sum variable

    @staticmethod
    def consumer_end(cfg):
        return cfg.sum  # return the result you need

if __name__ == '__main__':
    runner = Runner(devices=3)  # if you specify `device with a integer`, it will use cpus.
    # You can specify a list of str instead, such as: 
    # runner = Runner(devices=["cpu", "cpu", "cpu"]) 
    
    data_list = list(range(100))  # prepare data, it must be iterable
    result = runner(data_list)  # call the runner
    print(result)

    runner.close()  # close the runner and shutdown all processes it opens.
```

## Example 2: An neural network predictor

First we define an neural network in `network.py`:

```python
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
```

The network can be paralleled to 4 gpus in the following way:

```python
from easycore.common.config import CfgNode
from easycore.common.parallel import OrderedRunner
from network import Net
import torch

class Predictor(OrderedRunner):
    @staticmethod
    def producer_init(device, cfg):
        cfg.model = Net()     # init the producer with a model
        cfg.model.to(device)  # transfer the model to certain device

    @staticmethod
    def producer_work(device, cfg, data):
        with torch.no_grad():
            data = torch.Tensor([[data]])  # preprocess data
            data = data.to(device)  # transfer data to certain device
            output = cfg.model(data)  # predict
            output = output.cpu()  # transfer result to cpu
        return output

    @staticmethod
    def producer_end(device, cfg):
        del cfg.model  # delete the model when all data has been predicted.

    @staticmethod
    def consumer_init(cfg):
        cfg.data_list = []  # prepare a list to store all data from producers.

    @staticmethod
    def consumer_work(cfg, data):
        cfg.data_list.append(data)  # store data from producers.

    @staticmethod
    def consumer_end(cfg):
        data = torch.cat(cfg.data_list, dim=0)  # postprocess data.
        return data

if __name__ == '__main__':
    predictor = Predictor(devices=["cuda:0", "cuda:1", "cuda:2", "cuda:3"])  # init a parallel predictor

    data_list = list(range(100))  # prepare data
    result = predictor(data_list)  # predict
    print(result.shape)

    predictor.close()  # close the predictor when you no longer need it.
```

## Example 3: Process data with batch

You can use a simple generator or pytorch dataloader to generate batch data.

```python
from easycore.common.config import CfgNode
from easycore.torch.parallel import OrderedRunner
from network import Net
import torch

def batch_generator(data_list, batch_size):
    for i in range(0, len(data_list), batch_size):
        data_batch = data_list[i : i+batch_size]
        yield data_batch

class Predictor(OrderedRunner):

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

if __name__ == '__main__':
    predictor = Rredictor(devices=["cuda:0", "cuda:1"])
    
    data_list = list(range(100))
    result = predictor(batch_generator(data_list, batch_size=10))  
    print(result.shape)

    predictor.close()
```

Here, we replace `easycore.common.parallel` with `easycore.torch.parallel`. `easycore.torch.parallel` has the same API with `easycore.common.parallel` but use `torch.multiprocessing` library instead of `multiprocessing` library.

## Example 4: Transfer outside parameters into Runner

You can transfer parameters into runner through `cfg` parameter. `cfg` is a `easycore.common.config.CfgNode`. See tutorial ["Light weight config tools"](./config.html) for how to use it.

We use "sum of power" as an example:

```python
from easycore.common.config import CfgNode as CN
from easycore.common.parallel import UnorderedRunner

class Runner(UnorderedRunner):
    @staticmethod
    def producer_work(device, cfg, data):
        return data ** cfg.exponent  # calculate power of data with outside parameter "exponent".

    @staticmethod
    def consumer_init(cfg):
        cfg.sum = 0  # init a sum variable with 0, you can use cfg to transfer data

    @staticmethod
    def consumer_work(cfg, data):
        cfg.sum += data  # add the square to the sum variable

    @staticmethod
    def consumer_end(cfg):
        return cfg.sum  # return the result you need

if __name__ == '__main__':
    # set parameters outside.
    cfg = CN()
    cfg.exponent = 3

    runner = Runner(devices=3, cfg=cfg)  # transfer `cfg` into the runner 
    
    data_list = list(range(100))
    result = runner(data_list)
    print(result)

    runner.close()
```


## API Documentation

+ [easycore.common.parallel](../modules/easycore.common.parallel.html)
+ [easycore.torch.parallel](../modules/easycore.torch.parallel.html)