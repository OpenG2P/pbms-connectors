# Parent model must be imported before the models that _inherit it.
# isort would put farmer and household first, and Odoo then fails with
# "inherits from non-existing model 'g2p.registry'".
# isort: off
from .registry import G2PRegistry
from .farmer_registry import G2PFarmerRegistry
from .household import G2PRegisterHousehold

# isort: on
