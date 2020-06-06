from easycore.common.config import CfgNode as CN
import os

FILE_DIR = os.path.dirname(__file__)

class TestCfgNode:

    def test_init_dict(self):
        init_dict = {
            "hello": 123, 
            "world": {
                "tuple": (1,3), 
                "list": [1,2]
            }
        }
        cfg = CN(init_dict)


        assert cfg.hello == 123
        assert isinstance(cfg.world, CN)
        assert cfg.world.tuple == (1,3)
        assert cfg.world.list == [1,2]
        
    def test_add(self):
        cfg = CN()
        cfg.MODEL = CN()
        cfg.MODEL.NAME = 'resnet'
        cfg.INPUT = CN()
        cfg.INPUT.SIZE = (224, 224)

        assert isinstance(cfg.MODEL, CN)
        assert cfg.MODEL.NAME == 'resnet'
        assert isinstance(cfg.INPUT, CN)
        assert cfg.INPUT.SIZE == (224,224)

    def test_open_load_dump_save(self):
        input_path = os.path.join(FILE_DIR, 'example.yaml')

        cfg = CN.open(input_path)
        assert isinstance(cfg, CN)
        
        yaml_str = CN.dump(cfg)
        assert isinstance(yaml_str, str)
        
        cfg = CN.load(yaml_str)
        assert isinstance(cfg, CN)
        
        save_path = os.path.join(FILE_DIR, 'example-save.yaml')

        cfg.save(save_path)
        assert os.path.exists(save_path)

        os.remove(save_path)

    def test_merge(self):
        cfg_a = CN()
        cfg_b = CN()
        cfg_a.A = 1
        cfg_a.B = 2
        cfg_b.B = CN()
        cfg_b.B.C = 3
        
        cfg_a.merge(cfg_b)
        assert cfg_a.A == 1
        assert isinstance(cfg_a.B, CN)
        assert cfg_a.B.C == 3
    
    def test_to_dict(self):
        cfg = CN()
        cfg.A = 1
        cfg.B = CN()
        cfg.B.C = 3
        cfg_dict = cfg.dict()
        
        result = {'A': 1, 'B':{'C': 3}}
        assert cfg_dict == result

    def test_python_specified_tag(self):
        input_path = os.path.join(FILE_DIR, 'example.yaml')

        cfg = CN.open(input_path)
        assert cfg.scale == [2 ** 0, 2 ** (1 / 3), 2 ** (2 / 3)]
