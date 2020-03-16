import re
import copy as cp
import yaml
import io
from ast import literal_eval

class CfgNode(dict):
    """ Config Node """

    __FROZEN_KEY__ = '__frozen__'

    def __init__(self, init_dict:dict=None, copy=True):
        """
        Args:
            init_dict (dict): a possibly-nested dictionary to initialize the CfgNode.
            copy (bool): if this option is set to False, the CfgNode instance will share the value
                with the `init_dict`, otherwise the contents of `init_dict` will be deepcopied.
        """
        if copy:
            init_dict = cp.deepcopy(init_dict)

        if init_dict is None:
            init_dict = {}
        init_dict = CfgNode._create_config_from_dict(init_dict)
        super(CfgNode, self).__init__(init_dict)

        self.__dict__[CfgNode.__FROZEN_KEY__] = False


    @classmethod
    def _create_config_from_dict(cls, in_dict):
        """ 
        Create a config tree from a possible nested dictionary.

        Note:
            this method will share variables with `in_dict` and modify `in_dict`. 

        Args:
            in_dict (dict):
        
        Returns:
            dict: a dict whose nested dictionaries are all replaced with CfgNode.
        """
        for key, value in in_dict.items():
            # check key
            if not isinstance(key, str):
                raise KeyError("each key of the input dictionary must be `str` type.")
            if not cls._check_name_valid(key):
                raise KeyError("key in the input dictionary must be a vaild python variable name.")
            
            # process value
            in_dict[key] = cls._decode_value(value)
        return in_dict    
    

    @classmethod
    def _check_name_valid(cls, name):
        """ 
        Check whether the name satisfies the named rule of python variable.

        Args:
            name (str):

        Returns:
            bool: whether the name is a valid python variable name.
        """
        return re.match("[a-zA-Z_][a-zA-Z0-9_]*", name) is not None


    @classmethod
    def _decode_value(cls, value):
        """ 
        Decode the value into CfgNode, str or other possible type.

        Args:
            value (Any):
        
        Returns:
            Any
        """
        if isinstance(value, dict):
            value = cls(init_dict=value, copy=False)
        elif isinstance(value, str):
            try:
                value = literal_eval(value)
            except(ValueError, SyntaxError):
                pass
        return value


    def freeze(self, frozen:bool=True):
        """ 
        freeze or unfreeze the CfgNode and all of its children

        Args:
            frozen (bool): freeze or unfreeze the config
        """
        self.__dict__[CfgNode.__FROZEN_KEY__] = frozen
        for value in self.values():
            if isinstance(value, CfgNode):
                value.freeze(frozen)


    def is_frozen(self):
        """ 
        get the state of the config.
        
        Returns: 
            bool: whether the config tree is frozen.
        """
        return self.__dict__[CfgNode.__FROZEN_KEY__]


    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError(name)


    def __setattr__(self, name, value):
        if self.is_frozen():
            raise AttributeError("Attempted to set {} to {}, but the CfgNode is frozen.".format(name, value))
        
        self[name] = value
        
    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError(name)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, super(CfgNode, self).__repr__())
    

    def copy(self):
        """ 
        deepcopy this CfgNode
        
        Returns:
            CfgNode:
        """
        return cp.deepcopy(self)


    def merge(self, cfg):
        """ 
        merge another CfgNode into this CfgNode, the another CfgNode will override this CfgNode.

        Args:
            cfg (CfgNode):
        """
        if self.is_frozen():
            raise Exception("Attempted to merge another CfgNode to this CfgNode, but this CfgNode is frozen.")

        cfg = cfg.copy()
        for key, value in cfg.items():
            if key not in self:
                self[key] = value
            elif self[key] != value:
                if isinstance(self[key], CfgNode) and isinstance(value, CfgNode):
                    self[key].merge(value)
                else:
                    self[key] = value


    def save(self, save_path, encoding='utf-8'):
        """ 
        save the CfgNode into a yaml file

        Args:
            save_path:
        """
        with open(save_path, 'w', encoding=encoding) as f:
            CfgNode.dump(self, stream=f, encoding=encoding)


    @classmethod
    def _load_cfg_from_yaml_str(cls, yaml_str):
        """ 
        load a CfgNode from a string of yaml format

        Args:
            yaml_str (str): a string of yaml format

        Returns:
            CfgNode:
        """
        cfg_dict = yaml.safe_load(yaml_str)
        return cls(cfg_dict)


    @classmethod
    def _load_cfg_from_yaml_file(cls, yaml_file):
        """ 
        load a CfgNode from a yaml file object

        Args:
            yaml_file (io.IOBase):
        
        Returns:
            CfgNode:
        """
        return cls._load_cfg_from_yaml_str(yaml_file.read())


    @classmethod
    def open(cls, file, encoding='utf-8'):
        """ 
        load a CfgNode from file.

        Args:
            file (io.IOBase or str): file object or path to the yaml file.
            encoding (str): 
        
        Returns:
            CfgNode:
        """
        if isinstance(file, str):
            with open(file, 'r', encoding=encoding) as f:
                return cls._load_cfg_from_yaml_file(f)
        elif isinstance(file, io.IOBase):
            return cls._load_cfg_from_yaml_file(file)
        else:
            raise TypeError("Expect a file object or str object, but got a {}".format(type(file)))


    @classmethod
    def load(cls, yaml_str:str):
        """
        load a CfgNode from a string of yaml format

        Args:
            yaml_str (str): 
        
        Returns:
            CfgNode:
        """
        return cls._load_cfg_from_yaml_str(yaml_str)


    @classmethod
    def _convert_cfg_to_dict(cls, cfg):
        """
        convert a CfgNode to pure dict

        Args:
            cfg (CfgNode):
        
        Returns:
            dict:
        """
        out_dict = {}
        for key, value in cfg.items():
            if isinstance(value, cls):
                out_dict[key] = cls._convert_cfg_to_dict(value)
            else:
                out_dict[key] = value
        return out_dict        


    @classmethod
    def dump(cls, cfg, stream=None, encoding=None, **kwargs):
        """
        dump CfgNode into yaml str or yaml file

        Note:
            if `stream` option is set to non-None object, the CfgNode will be dumpped into stream and return None, 
            if `stream` option is not given or set to None, return a string instead.

        Args:
            cfg (CfgNode):
            stream (io.IOBase or None): if set to a file object, the CfgNode will be dumpped into stream
                and return None, if set to None, return a string instead.
            encoding (str or None):
            **kwargs: options of the yaml dumper. \n
                Some useful options: ["allow_unicode", "line_break", "explicit_start", 
                "explicit_end", "version", "tags"]. \n
                See more details at https://github.com/yaml/pyyaml/blob/2f463cf5b0e98a52bc20e348d1e69761bf263b86/lib3/yaml/__init__.py#L252

        Returns:
            None or str:
        """
        cfg_dict = CfgNode._convert_cfg_to_dict(cfg)
        return yaml.safe_dump(cfg_dict, stream=stream, encoding=encoding, **kwargs)

    def dict(self):
        """
        convert to a dict

        Returns:
            dict:
        """
        return CfgNode._convert_cfg_to_dict(self)

    def __str__(self):
        """
        Returns:
            str: a str of dict format
        """
        return str(self.dict())
