# Register Mechanism

**easycore** make it easy to register an object with name, and get it later.

## Create a registry

```python
MODEL_REGISTRY = Registry("MODEL")
```

## Register an object with its `__name__`

```python
@MODEL_REGISTRY.register()
class ResNet50:
    pass

# or

MODEL_REGISTRY.register(obj=ResNet50)
```

## Register an object with a given name

```python
@MODEL_REGISTRY.register("resnet")
class RestNet50:
    pass

# or

MODEL_REGISTRY.register("resnet", ResNet50)
```

## Get a registered object from registry

```python
model_class = MODEL_REGISTRY.get("ResNet50")

# or

model_class = MODEL_REGISTRY.get("resnet")
```


## API Documentation

+ [easycore.common.registry](../modules/easycore.common.registry.html)