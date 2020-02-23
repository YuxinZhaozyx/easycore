import unittest
from easycore.common.config import CfgNode as CN
import os

class TestCfgNode(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUP(self):
        pass

    def tearDown(self):
        pass

    def test_init_dict(self):
        init_dict = {
            "hello": 123, 
            "world": {
                "tuple": (1,3), 
                "list": [1,2]
            }
        }
        cfg = CN(init_dict)

        self.assertEqual(cfg.hello, 123)
        self.assertIsInstance(cfg.world, CN)
        self.assertEqual(cfg.world.tuple, (1,3))
        self.assertEqual(cfg.world.list, [1,2])
        
    def test_add(self):
        cfg = CN()
        cfg.MODEL = CN()
        cfg.MODEL.NAME = 'resnet'
        cfg.INPUT = CN()
        cfg.INPUT.SIZE = (224, 224)

        self.assertIsInstance(cfg.MODEL, CN)
        self.assertEqual(cfg.MODEL.NAME, 'resnet')
        self.assertIsInstance(cfg.INPUT, CN)
        self.assertEqual(cfg.INPUT.SIZE, (224,224))
    
    def test_open_load_dump_save(self):
        cfg = CN.open('example.yaml')
        self.assertIsInstance(cfg, CN)
        yaml_str = CN.dump(cfg)
        self.assertIsInstance(yaml_str, str)
        cfg = CN.load(yaml_str)
        self.assertIsInstance(cfg, CN)
        cfg.save("./example-save.yaml")
        self.assertTrue(os.path.exists("./example-save.yaml"))

    def test_merge(self):
        cfg_a = CN()
        cfg_b = CN()
        cfg_a.A = 1
        cfg_a.B = 2
        cfg_b.B = CN()
        cfg_b.B.C = 3
        
        cfg_a.merge(cfg_b)
        self.assertEqual(cfg_a.A, 1)
        self.assertIsInstance(cfg_a.B, CN)
        self.assertEqual(cfg_a.B.C, 3)
        
if __name__ == '__main__':
    unittest.main()