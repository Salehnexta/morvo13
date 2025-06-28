# SQLAlchemy 2.0+ recommends importing `declarative_base` from `sqlalchemy.orm`
# to avoid the `MovedIn20Warning`.

from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here to ensure they are registered with SQLAlchemy Base.metadata

# These imports have side effects: they register the model classes with the
# SQLAlchemy `Base` registry so that relationship string look-ups resolve
# correctly during mapper configuration.

# pylint: disable=unused-import, wrong-import-position
# ruff: noqa: F401

from app.models import business_profile  # noqa: F401, E402
from app.models import seranking  # noqa: F401, E402
from app.models import user  # noqa: F401, E402
