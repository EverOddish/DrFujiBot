class WestwoodDatabaseRouter(object):
    """
    Determine how to route database calls for an app's models (in this case, for Westwood).
    All other models will be routed to the next router in the DATABASE_ROUTERS setting if applicable,
    or otherwise to the default database.
    """

    def db_for_read(self, model, **hints):
        """Send all read operations on Westwood app models to `westwood`."""
        if model._meta.app_label == 'westwood':
            return 'westwood'
        return None

    def db_for_write(self, model, **hints):
        """Send all write operations on Westwood app models to `westwood`."""
        if model._meta.app_label == 'westwood':
            return 'westwood'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Determine if relationship is allowed between two objects."""

        # Allow any relation between two models that are both in the Westwood app.
        if obj1._meta.app_label == 'westwood' and obj2._meta.app_label == 'westwood':
            return True
        # No opinion if neither object is in the Westwood app (defer to default or other routers).
        elif 'westwood' not in [obj1._meta.app_label, obj2._meta.app_label]:
            return None

        # Block relationship if one object is in the Westwood app and the other isn't.
            return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that the Westwood app's models get created on the right database."""
        if app_label == 'westwood':
            # The Westwood app should be migrated only on the westwood database.
            return db == 'westwood'
        elif db == 'westwood':
            # Ensure that all other apps don't get migrated on the westwood database.
            return False

        # No opinion for all other scenarios
        return None
