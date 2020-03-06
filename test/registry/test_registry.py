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