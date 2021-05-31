from functools import partial

from flask_principal import Need

ProjectNeed = partial(Need, 'project')
