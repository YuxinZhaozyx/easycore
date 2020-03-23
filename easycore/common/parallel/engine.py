import multiprocessing as mp
import threading
import queue
import atexit
import bisect
from typing import Callable, Iterable, Any
from easycore.common.config import CfgNode as CN


class BaseRunner:
    """
    A Multi-process runner whose consumer receive data in unorder. 
    The runner will start multi-processes for producers and 1 thread for consumer.
    """

    class _Producer(mp.Process):
        def __init__(self,
                     input_queue,
                     output_queue,
                     device,
                     cfg,
                     init_func,
                     work_func,
                     end_func):
            super(BaseRunner._Producer, self).__init__()
            self.input_queue = input_queue
            self.output_queue = output_queue
            self.device = device
            self.cfg = cfg.copy()
            self.init_func = init_func
            self.work_func = work_func
            self.end_func = end_func

        def run(self):
            raise NotImplementedError("This is a base runner without implement.")

        class _StopToken:
            pass

    class _Consumer(threading.Thread):
        def __init__(self,
                     receive_func,
                     input_queue,
                     output_queue,
                     cfg,
                     init_func,
                     work_func,
                     end_func):
            super(BaseRunner._Consumer, self).__init__(daemon=True)
            self.receive_func = receive_func
            self.input_queue = input_queue
            self.output_queue = output_queue
            self.cfg = cfg.copy()
            self.init_func = init_func
            self.work_func = work_func
            self.end_func = end_func

        def run(self):
            raise NotImplementedError("This is a base runner without implement.")

        class _InitToken:
            pass

        class _EndToken:
            pass   

        class _StopToken:
            pass

    def __init__(self,
                 devices,
                 cfg = CN(),
                 queue_scale = 3.0):
        """
        Args:
            devices (int or Iterable): If the `devices` is `int`, it will use devices cpu to do
                the work. If the `devices` is an iterable object, such as list, it will use the
                devices specified by the iterable object, such as ["cpu", "cuda:0", "cuda:1"].
            cfg (easycore.common.config.CfgNode): user custom data.
            queue_scale (float): scale the queues for communication between processes.
        """
        # get devices
        if isinstance(devices, int):
            self.devices = ["cpu" for _ in range(devices)]
        elif isinstance(devices, Iterable):
            self.devices = devices
        else:
            raise Exception("parameter `devices` must be int or Iterable.")

        self.cfg = cfg
        self.queue_scale = queue_scale

        self._is_activate = False
        self.activate()
        
        atexit.register(self.close)

    @property
    def is_activate(self):
        """ whether the runner is alive. """
        return self._is_activate

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

    def __call__(self, data_iter):
        """
        Args:
            data_iter (Iterable): iterator of data
        
        Returns:
            Any: result
        """
        if not self.is_activate:
            raise Exception("The runner is closed. Please activate it.")

        # inform the consumer to initialize
        self._put_into_consumer(self._Consumer._InitToken())

        # put data to producer
        for data in data_iter:
            self._put_into_producer(data)
            self._put_into_consumer(None)  # inform the consumer to process 1 data

        # inform the consumer to return result
        self._put_into_consumer(self._Consumer._EndToken())

        # get result from consumer
        data = self._get_from_consumer()
        return data

    def __del__(self):
        self.close()

    def close(self):
        """
        Shutdown all processes if this runner is alive.
        """
        if self.is_activate:
            self._is_activate = False
            # stop workers
            for _ in self.devices:
                self.producer_input_queue.put(self._Producer._StopToken())
            self.consumer_input_queue.put(self._Consumer._StopToken())

            # join workers
            for producer in self.producers:
                producer.join()
            self.consumer.join()

            # delete resources
            del self.producer_input_queue
            del self.producer_output_queue
            del self.consumer_input_queue
            del self.consumer_output_queue
            del self.producers
            del self.consumer


    def activate(self):
        """
        Restart all processes if this runner is closed.
        """
        if not self.is_activate:
            self._is_activate = True
            # init queues for communication between processes
            self.producer_input_queue = mp.Queue(maxsize = int(len(self.devices) * self.queue_scale))
            self.producer_output_queue = mp.Queue(maxsize = int(len(self.devices) * self.queue_scale))
            self.consumer_input_queue = queue.Queue(maxsize = int(len(self.devices) * self.queue_scale))
            self.consumer_output_queue = queue.Queue(maxsize = 1)

            # create workers
            self.producers = []
            for device in self.devices:
                self.producers.append(
                    self._Producer(
                        self.producer_input_queue,
                        self.producer_output_queue,
                        device,
                        self.cfg,
                        self.producer_init,
                        self.producer_work,
                        self.producer_end))
            self.consumer = self._Consumer(
                self._get_from_producer,
                self.consumer_input_queue,
                self.consumer_output_queue,
                self.cfg,
                self.consumer_init,
                self.consumer_work,
                self.consumer_end)

            # start workers
            for producer in self.producers:
                producer.start()
            self.consumer.start()


    def _put_into_producer(self, data):
        self.producer_input_queue.put(data)
    
    def _get_from_producer(self):
        return self.producer_output_queue.get()

    def _put_into_consumer(self, data):
        self.consumer_input_queue.put(data)
    
    def _get_from_consumer(self):
        data = self.consumer_output_queue.get()
        self.consumer_output_queue.task_done()
        return data



class UnorderedRunner(BaseRunner):
    """
    A Multi-process runner whose consumer receive data in unorder. 
    The runner will start multi-processes for producers and 1 thread for consumer.
    """
    class _Producer(BaseRunner._Producer):
        def run(self):
            # initialization
            self.init_func(self.device, self.cfg)

            while True:
                data = self.input_queue.get()
                if isinstance(data, self._StopToken):
                    break

                # decode data and do task
                data = self.work_func(self.device, self.cfg, data)

                self.output_queue.put(data)

            # end
            self.end_func(self.device, self.cfg)


    class _Consumer(BaseRunner._Consumer):
        def run(self):
            while True:
                data = self.input_queue.get()
                self.input_queue.task_done()
                if isinstance(data, self._StopToken):
                    break
                elif isinstance(data, self._InitToken):
                    # initialization
                    cfg = self.cfg.copy()
                    self.init_func(cfg)
                elif isinstance(data, self._EndToken):
                    # end
                    data = self.end_func(cfg)
                    self.output_queue.put(data)
                    del cfg
                else:
                    # work
                    data = self.receive_func()
                    self.work_func(cfg, data)


    def __init__(self,
                 devices,
                 cfg = CN(),
                 queue_scale = 3.0):
        """
        Args:
            devices (int or Iterable): If the `devices` is `int`, it will use devices cpu to do
                the work. If the `devices` is an iterable object, such as list, it will use the
                devices specified by the iterable object, such as ["cpu", "cuda:0", "cuda:1"].
            cfg (easycore.common.config.CfgNode): user custom data.
            queue_scale (float): scale the queues for communication between processes.
        """
        super(UnorderedRunner, self).__init__(devices, cfg=cfg, queue_scale=queue_scale)



class OrderedRunner(BaseRunner):
    """ 
    A Multi-process runner whose consumer receive data in order. 
    The runner will start multi-processes for producers and 1 thread for consumer.
    """
    class _Producer(BaseRunner._Producer):
        def run(self):
            # initialization
            self.init_func(self.device, self.cfg)

            while True:
                data = self.input_queue.get()
                if isinstance(data, self._StopToken):
                    break

                # decode data and do task
                id, data = data
                data = self.work_func(self.device, self.cfg, data)

                self.output_queue.put((id, data))

            # end
            self.end_func(self.device, self.cfg)


    class _Consumer(BaseRunner._Consumer):
        def run(self):
            while True:
                data = self.input_queue.get()
                self.input_queue.task_done()
                if isinstance(data, self._StopToken):
                    break
                elif isinstance(data, self._InitToken):
                    # initialization
                    cfg = self.cfg.copy()
                    self.init_func(cfg)
                elif isinstance(data, self._EndToken):
                    # end
                    data = self.end_func(cfg)
                    self.output_queue.put(data)
                    del cfg
                else:
                    data = self.receive_func()
                    self.work_func(cfg, data)

    def __init__(self,
                 devices,
                 cfg = CN(),
                 queue_scale = 3.0):
        """
        Args:
            devices (int or Iterable): If the `devices` is `int`, it will use devices cpu to do
                the work. If the `devices` is an iterable object, such as list, it will use the
                devices specified by the iterable object, such as ["cpu", "cuda:0", "cuda:1"].
            cfg (easycore.common.config.CfgNode): user custom data.
            queue_scale (float): scale the queues for communication between processes.
        """
        super(OrderedRunner, self).__init__(devices, cfg=cfg, queue_scale=queue_scale)


    def close(self):
        """
        Shutdown all processes if this runner is alive.
        """
        if self.is_activate:
            del self._put_id, self._get_id
            del self._id_buffer, self._data_buffer

            super(OrderedRunner, self).close()

    def activate(self):
        """
        Restart all processes if this runner is closed.
        """
        if not self.is_activate:
            self._put_id = 0
            self._get_id = 0
            self._id_buffer = []
            self._data_buffer = []

            super(OrderedRunner, self).activate()

    def _put_into_producer(self, data):
        id = self._put_id
        self._put_id += 1
        self.producer_input_queue.put((id, data))
    
    def _get_from_producer(self):
        if len(self._id_buffer) and self._id_buffer[0] == self._get_id:
            data = self._data_buffer[0]
            del self._id_buffer[0], self._data_buffer[0]
            self._get_id += 1
            return data

        while True:
            id, data = self.producer_output_queue.get()
            if id == self._get_id:
                self._get_id += 1
                return data
            insert_position = bisect.bisect(self._id_buffer, id)
            self._id_buffer.insert(insert_position, id)
            self._data_buffer.insert(insert_position, data)

