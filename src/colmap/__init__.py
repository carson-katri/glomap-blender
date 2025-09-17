from .operators import register as register_operators
from .operators import unregister as unregister_operators

from .panels import register as register_panels
from .panels import unregister as unregister_panels

from .property_groups import register as register_property_groups
from .property_groups import unregister as unregister_property_groups

def register():
    register_property_groups()
    register_operators()
    register_panels()

def unregister():
    unregister_property_groups()
    unregister_operators()
    unregister_panels()