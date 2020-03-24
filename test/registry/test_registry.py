from easycore.common.registry import Registry

MODEL_REGISTRY = Registry('model')

def test_registry_call_1():
    @MODEL_REGISTRY.register()
    class ResNet50:
        def __call__(self):
            return "Call in ResNet50"
    
    assert MODEL_REGISTRY.get('ResNet50')()() == 'Call in ResNet50'

def test_registry_call_2():
    @MODEL_REGISTRY.register('MobileNet')
    class MobileNetV2:
        def __call__(self):
            return "Call in MobileNetV2"
    
    assert MODEL_REGISTRY.get('MobileNet')()() == "Call in MobileNetV2"

def test_registry_call_3():
    def build_resnet():
        return "Call in build_resnet"

    MODEL_REGISTRY.register(obj=build_resnet)

    assert MODEL_REGISTRY.get('build_resnet')() == 'Call in build_resnet'

def test_registry_call_4():
    def build_mobilenetv2():
        return "Call in build_mobilenetv2"

    MODEL_REGISTRY.register('build_mobilenet', build_mobilenetv2)

    assert MODEL_REGISTRY.get('build_mobilenet')() == 'Call in build_mobilenetv2'

def test_registry_registered_names():
    FUNC_REGISTRY = Registry('func')

    @FUNC_REGISTRY.register()
    def A():
        pass

    @FUNC_REGISTRY.register('B')
    def B_impl():
        pass

    def C():
        pass

    FUNC_REGISTRY.register(obj=C)
    FUNC_REGISTRY.register('D', C)

    registered_names = FUNC_REGISTRY.registered_names()
    assert set(registered_names) == set(['A', 'B', 'C', 'D'])

def test_unregister():
    REGISTRY = Registry("test")

    assert REGISTRY.is_registered('obj') == False

    REGISTRY.register('obj', ["hello world"])

    assert REGISTRY.is_registered('obj') == True

    REGISTRY.unregister('obj')

    assert REGISTRY.is_registered('obj') == False

