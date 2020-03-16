from .config import CfgNode
import os

class HierarchicalCfgNode:
    """ 
    Config Node help class for open yaml file that depends on another yaml file.
    
    You can specify the dependency between yaml files with ``__BASE__`` tag.
    
    Example:
        We can load yaml file ``example-A.yaml`` which depends on ``example-B.yaml`` in the
        following way.

        ``example-A.yaml`` :

        .. code-block:: yaml

            __BASE__: ./example-B.yaml
            A: in example-A.yaml
            C: in example-A.yaml

        ``example-B.yaml`` :

        .. code-block:: yaml

            A: in example-B.yaml
            B: in example-B.yaml

        Now, you can open example-A.yaml:
        
        .. code-block:: python

            >>> import easycore.common.config import HierarchicalCfgNode
            >>> cfg = HierarchicalCfgNode.open("./example-A.yaml")
            >>> print(cfg)
            {"A" : "in example-A.yaml", "B" : "in example-B.yaml", "C" : "in example-A.yaml"}

        Attributes in ``example-A.yaml`` will cover attributes in ``example-B.yaml``.

    Note:
        ``__BASE__`` can be an absolute path or a path relative to the yaml file. And it will be first
        considered as a path relative to the yaml file then an absolute path.

    """

    __BASE__ = '__BASE__'

    @classmethod
    def open(cls, file, encoding='utf-8'):
        """ 
        load a CfgNode from file.

        Args:
            file (str): path to the yaml file.
            encoding (str): 
        
        Returns:
            CfgNode:
        """
        cfg_list = []
        file_list = []  # for checking loop

        file = os.path.abspath(file)  # convert to absolute path
        file_list.append(file)

        cfg = CfgNode.open(file, encoding=encoding)
        cfg_dir = os.path.dirname(os.path.abspath(file))
        cfg_list.append(cfg)
        
        # open all hierarchical configs
        while cls.__BASE__ in cfg:
            if os.path.exists(os.path.join(cfg_dir, cfg.__BASE__)):
                # consider __BASE__ as a path relative to the yaml file
                file = os.path.join(cfg_dir, cfg.__BASE__)
            elif os.path.exists(cfg.__BASE__):
                # consider __BASE__ as an absolute path
                file = cfg.__BASE__
            else:
                raise FileNotFoundError(
                    "{}:{} in {}".format(cls.__BASE__, cfg.__BASE__, file)
                )

            file = os.path.abspath(file)
            if file in file_list:
                raise FileExistsError("Can not open an yaml file whose dependency cause loop.")

            cfg = CfgNode.open(file, encoding=encoding)
            cfg_dir = os.path.dirname(os.path.abspath(file))
            cfg_list.append(cfg)

        # merge configs
        base_cfg = cfg_list.pop()
        while len(cfg_list) > 0:
            cfg = cfg_list.pop()
            if cls.__BASE__ in cfg:
                del cfg[cls.__BASE__]
            base_cfg.merge(cfg)

        return base_cfg

    @classmethod
    def save(cls, cfg, save_path, base_cfg_path=None, base_path_relative=True, encoding='utf-8'):
        """ 
        save the CfgNode into a yaml file

        Args:
            cfg (CfgNode):
            save_path (str):
            base_cfg_path (str): if not specified, it behavior like ``cfg.save(save_path, encoding)``.
            base_path_relative (bool): whether to set base cfg path to a path relative to the save_path.
            encoding (str):
        """
        def remove_exists_attribute(cfg, base_cfg):
            cfg_copy = cfg.copy()
            
            for key, value in cfg.items():
                if key in base_cfg:
                    if value == base_cfg[key]:
                        del cfg_copy[key]
                    elif isinstance(value, CfgNode) and isinstance(base_cfg[key], CfgNode):
                        cfg_copy[key] = remove_exists_attribute(value, base_cfg[key])
            
            return cfg_copy

        if base_cfg_path is not None:
            if not os.path.exists(base_cfg_path):
                raise FileNotFoundError(base_cfg_path)

            base_cfg = cls.open(base_cfg_path, encoding)

            if base_path_relative:
                base_cfg_path = os.path.relpath(base_cfg_path, start=os.path.dirname(save_path))
            else:
                base_cfg_path = os.path.abspath(base_cfg_path)

            cfg = remove_exists_attribute(cfg, base_cfg)
            cfg[cls.__BASE__] = base_cfg_path

        cfg.save(save_path, encoding=encoding)
    
    
        