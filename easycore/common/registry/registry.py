from typing import Dict, Optional, List

class Registry:
    """
    The registry that provides name -> object mapping.

    To create a registry:
    
    .. code-block:: python

        MODEL_REGISTRY = Registry("MODEL")

    To register an object with its ``__name__``:
    
    .. code-block:: python

        @MODEL_REGISTRY.register()
        class ResNet50:
            pass

        # or

        MODEL_REGISTRY.register(obj=ResNet50)
    
    To register an object with a given name:

    .. code-block:: python

        @MODEL_REGISTRY.register("resnet")
        class RestNet50:
            pass

        # or

        MODEL_REGISTRY.register("resnet", ResNet50)

    To get a registered object from registry:
    
    .. code-block:: python

        model_class = MODEL_REGISTRY.get("ResNet50")

        # or

        model_class = MODEL_REGISTRY.get("resnet")
    """

    def __init__(self, name:str) -> None:
        """
        Args:
            name (str): name of this registry
        """
        self._name = name
        self._obj_map: Dict[str, object] = {}


    def _do_register(self, name:str, obj:object) -> None:
        if name in self._obj_map:
            raise KeyError("An object named '{}' was already registered in '{}' registry.".format(name, self._name))

        self._obj_map[name] = obj


    def register(self, name:str=None, obj:object=None) -> Optional[object]:
        """
        Register the given object with given name.
        If the object is not given, it will act as a decorator.

        Args:
            name (str, optional): if not given, it will use `obj.__name__` as the name.
            obj (object, optional): if not given, this method will return a decorator.

        Returns:
            Optional[object]: None or a decorator.
        """
        if obj is None:
            # use as a decorator
            def decorator(func_or_class:object) -> object:
                nonlocal name
                if name is None:
                    name = func_or_class.__name__
                self._do_register(name, func_or_class)
                return func_or_class
            return decorator

        # use as a function call
        if name is None:
            name = obj.__name__
        self._do_register(name, obj)


    def get(self, name:str) -> object:
        """
        Get a registered object from registry by its name.

        Args:
            name (str): registered name.

        Returns:
            object: registered object.
        """
        if name not in self._obj_map:
            raise KeyError(
                "No object name '{}' found in '{}' registry.".format(
                    name, self._name
                )
            )
        return self._obj_map[name]

    def registered_names(self) -> List[str]:
        """
        Get all registered names.

        Returns:
            list[str]: list of registered names.
        """
        return list(self._obj_map.keys())