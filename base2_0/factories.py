## collections.abc.Mapping is use to test validict of attribute_classes argument
##
import collections
import collections.abc

class InstantiationException(Exception):
    pass


class Pyoot(object):
    """Base class for python-ooo-tables"""

class ItemClassBase(Pyoot):
    """
    ItemClassBase
    =============

    Base class designed for use with the MetaItemClass metaclass
    """

    def __init__(self, **kwargs):

        assert ( hasattr( self, 'required' ) and hasattr( self, 'attribute_classes' ) ), "This base class cannot be instantiated until 'required' and 'attribute_classes' are defined"

#
#  Check arguments
#
        missing = self.required - kwargs.keys()
        unknown = kwargs.keys() - self.attribute_classes.keys()

        error_msg = ''
        if len(missing) != 0:
            print( 'ERROR: missing required argument(s): %s' % missing )
            error_msg += 'ERROR: missing required argument(s): %s' % missing
        if len(unknown) != 0:
            print( 'ERROR: unknown argument(s) present: %s' % unknown  )
            error_msg += 'ERROR: unknown argument(s) present: %s' % unknown
        if error_msg != '':
            raise InstantiationException("Example01: %s" % error_msg)

        #
        # load argumens into instance structure
        #

        for a,v in kwargs.items():
            ## if v is already an instance of the required class, it is used;
            ## otherwise, it is used as input to instantiate the class.
            if isinstance( v, self.attribute_classes[a] ):
              self.__dict__['_%s' % a ] = v
            else:
              self.__dict__['_%s' % a ] = self.attribute_classes[a](v)

            self.__dict__[a] = self.__dict__['_%s' % a ].__value__


class MetaItemClass(type):
    """
    MetaItemClass
    =============

    This metaclass requires two elements in the classdict:
      * attribute_classes : a dictionary of classes which can be instantiated to create attribute values;
      * required : a list of required attributes

    The metaclass creates the __slots__ tuple and combines the classdict with the base class.
    """
    
    def __new__(cls, name, bases, classdict):

        assert 'required' and 'attribute_classes' in classdict

        result = type.__new__(cls, name, bases, classdict)

        assert isinstance(result.attribute_classes,collections.abc.Mapping), 'Attribute_classes must be a dictionary or other mapping'

        unknown = result.required - result.attribute_classes.keys() 
        assert len(unknown) == 0, 'Unknown attributes marked as required: %s' % unknown

        ks = list(result.attribute_classes.keys())
        result.__slots__ = tuple( ks + ['_%s' % x for x in ks] )

        if result.__doc__:
            result.__doc__ += "\n Created by MetaItemClass"
        else:
            result.__doc__ = "%s: Created by MetaItemClass" % name
        return result


class PyootNS(Pyoot):
    def __init__(self,tag,description):
        self.tag=tag
        self.decription=description
        self.contents=dict()
        self.records=collections.defaultdict(set)

    def add_rec(self,item):
        self.records[item.__class__.__name__].add(item)

    def add_dt(self,item):
        assert item.__name__ not in self.contents
        self.contents[item.__name__] = item

## Some simple test code

class ClassThis(object):
    """The This attribute : the value is converted to a string"""
    def __init__(self,value):
        self.__value__ = str(value)

class ClassThat(object):
    """The That attribute : the value is converted to a float, with negative values rounded up to zero"""
    def __init__(self,value):
        self.__value__ = max( [float(value),0.] )

class ClassOther(object):
    """The This attribute : the value is converted to a capitalised string"""
    def __init__(self,value):
        self.__value__ = str(value).title()

def get_example():
    ns = PyootNS('ex', 'Examples' )
    Example01 = MetaItemClass('Example01', (ItemClassBase,), dict( attribute_classes=dict( this=ClassThis, that=ClassThat ), required = {'that'} ) )
    Example02 = MetaItemClass('Example02', (ItemClassBase,), dict( attribute_classes=dict( this=ClassThis, other=ClassOther ), required = {'this'} ) )

    ns.add_dt(Example01)
    ns.add_dt(Example02)

    Example03a = MetaItemClass('Example03a', (ItemClassBase,), dict( attribute_classes=dict( __value__=ClassThis, other=ClassOther ), required = {'__value__'} ) )
    Example03 =  MetaItemClass('Example03', (ItemClassBase,), dict( attribute_classes=dict( this=ClassThis, other=ClassOther, more=Example03a ), required = {'this'} ) )
    ns.add_dt( Example03a )
    ns.add_dt( Example03 )

    x = Example01( this='a string', that=5.6 )
    y = Example01( this='another string', that=-3.2)
    w = Example02( this='another string', other='a longer string signifying greater meaning')

    print ( 'Value of x.this: ',x.this )
    print ( 'Value of w.other: ',w.other )
    ns.add_rec( x )
    ns.add_rec( y )
    ns.add_rec( w )

    xxa = Example03a( __value__=42, other='Demonstrating the ability to build a graph' )
    xx = Example03( this='A tree example', more=xxa )

    print ( 'Value of xx.more: ',xx.more )
    print ( 'Value of xx._more.other: ',xx._more.other )

    print ( 'Testing outcome of instantiation with an invalid argument' )
    try:
      z = Example01( other=None )
      raise Exception( 'This line should not be executed .. line above should raise exception' )
    except InstantiationException:
      print ('Expected InstantiationException caught' )

if __name__ == "__main__":
  get_example()
