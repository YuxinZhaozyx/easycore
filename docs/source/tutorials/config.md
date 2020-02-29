# Light weight config tools

**easycore** make it easy to load config from local yaml file, save config and control the config in runtime.

## Load config from local yaml file

An example of yaml file is shown bellow:

```yaml
MODEL:
    IN_FEAUTRES: ["res3", "res4", "res5"]
    INPUT_SIZE: (224, 224)
    NUM_CLASSES: 100
NAME: YuxinZhaozyx
```

You can load the yaml file in the follow way:

```python
from easycore.common.config import CfgNode as CN

cfg = CN.open('example.yaml')

# or
with open('example.yaml', 'r', encoding='utf-8') as f:
    cfg = CN.open(f)
```

## Get an empty config

```
cfg = CN()
```

## Get a config from from python `dict`

```python
init_dict = {
    "MODEL": {
        "IN_FEATURES": ["res3", "res4", "res5"],
        "INPUT_SIZE": (224, 224),
        "NUM_CLASSES": 100,
    },
    "NAME": "YuxinZhaozyx",
}
cfg = CN(init_dict)
```

## Use config

```python
# get value from config
# the config has been automatically transform into python data type.
in_features = cfg.MODEL.IN_FEATURES  # list
input_size = cfg.MODEL.INPUT_SIZE    # tuple
num_classes = cfg.MODEL.NUM_CLASSES  # int
name = cfg.NAME                      # str

# add new value to config
cfg.LICENSE = 'MIT'

# add a new CfgNode to config
cfg.SOLVER = CN()
cfg.SOLVER.LEARNING_RATE = 0.001
cfg.SOLVER.BATCH_SIZE = 128
```

## Merge two config

```python
cfg_a = CN()
cfg_a.key1 = 1
cfg_a.key2 = 2

cfg_b = CN()
cfg_b.key2 = 3
cfg_c.key3 = 4

# merge two config
cfg_a.merge(cfg_b)  # now cfg_a.key2 is 3
```

## Copy a config

```python
cfg_copy = cfg.copy()  # get a deepcopy of cfg
```

## Save config to yaml file

```python
cfg.save("example-save.yaml")

# or
with open("example-save.yaml", 'w', encoding='utf-8') as f:
    cfg.save(f)
```

## API Documentation

+ [easycore.common.config](../modules/easycore.common.config.html)