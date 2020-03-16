from easycore.common.config import CfgNode, HierarchicalCfgNode
import os

FILE_DIR = os.path.dirname(__file__)

def test_open():
    cfg_path = os.path.join(FILE_DIR, 'hierarchical_config', 'example-A.yaml')

    cfg = HierarchicalCfgNode.open(cfg_path)

    assert cfg.A == 'in example-A.yaml'
    assert cfg.B.C == 'in example-B.yaml'
    assert cfg.B.D == 'in example-A.yaml'
    assert cfg.C == 'in example-A.yaml'
    assert cfg.E == 'in example-B.yaml'
    assert HierarchicalCfgNode.__BASE__ not in cfg

def test_save():
    cfg = CfgNode()
    cfg.A = 'in example-C.yaml'
    cfg.B = CfgNode()
    cfg.B.C = 'in example-B.yaml'
    cfg.D = 'in example-C.yaml'
    
    save_path = os.path.join(FILE_DIR, 'example-C.yaml')
    base_cfg_path = os.path.join(FILE_DIR, 'hierarchical_config', 'example-A.yaml')
    
    HierarchicalCfgNode.save(cfg, save_path, base_cfg_path)
    cfg = HierarchicalCfgNode.open(save_path)
    
    assert cfg.A == 'in example-C.yaml'
    assert cfg.B.C == 'in example-B.yaml'
    assert cfg.D == 'in example-C.yaml'
    
    cfg = CfgNode.open(save_path)
    
    assert 'C' not in cfg.B

    os.remove(save_path)