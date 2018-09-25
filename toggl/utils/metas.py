import logging
from pprint import pformat
from traceback import format_stack

logger = logging.getLogger('toggl.utils.metas')

sentinel = object()


class CachedFactoryMeta(type):
    """
    Similar to Singleton patter, except there are more instances cached based on a input parameter.
    It utilizes Factory pattern and forbids direct instantion of the class.
    """

    SENTINEL_KEY = '20800fa4-c75d-4c2c-9c99-fb35122e1a18'

    def __new__(mcs, name, bases, namespace):
        mcs.cache = {}

        def new__init__(self):
            raise ValueError('Cannot directly instantiate new object, you have to use \'factory\' method for that!')

        old_init = namespace.get('__init__')
        namespace['__init__'] = new__init__

        def factory(cls_obj, key=sentinel, *args, **kwargs):
            # Key with None are not cached
            if key is None:
                obj = cls_obj.__new__(cls_obj, key, *args, **kwargs)
                old_init(obj, key, *args, **kwargs)
                return obj

            cached_key = mcs.SENTINEL_KEY if key == sentinel else key

            if cached_key in mcs.cache:
                return mcs.cache[cached_key]

            if key == sentinel:
                obj = cls_obj.__new__(cls_obj, *args, **kwargs)
                old_init(obj, *args, **kwargs)
            else:
                obj = cls_obj.__new__(cls_obj, key, *args, **kwargs)
                old_init(obj, key, *args, **kwargs)

            mcs.cache[cached_key] = obj

            return obj

        namespace['factory'] = classmethod(factory)
        return super().__new__(mcs, name, bases, namespace)


class ClassAttributeModificationWarning(type):
    def __setattr__(cls, attr, value):
        logger.warning('You are modifying class attribute of \'{}\' class. You better know what you are doing!'
                       .format(cls.__name__))

        logger.debug(pformat(format_stack()))

        super(ClassAttributeModificationWarning, cls).__setattr__(attr, value)
