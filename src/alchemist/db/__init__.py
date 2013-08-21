# -*- coding: utf-8 -*-
import types
import sys


class Module(types.ModuleType):

    def __init__(self, *args, **kwargs):
        from sqlalchemy import orm

        # Initialize our module first.
        super().__init__(*args, **kwargs)

        # Create a scope function that keys on the application context.
        def scopefunc():
            import flask
            return id(flask._app_ctx_stack.top)

        # Create the scoped session factory which automatically creates
        # sessions when it needs to when accessed.
        self.Session = orm.scoped_session(
            self.create_session, scopefunc=scopefunc)

    @property
    def session(self):
        # Return the available session which is created automatically for
        # the current context if it does not exist.
        return self.Session()

    @property
    def create_session(self):
        # Save these for reference.
        from sqlalchemy import orm

        # Construct an inner class to late-bind configuration.
        class Session(orm.Session):

            def __init__(self, *args, **kwargs):
                from alchemist import application
                from alchemist.db.query import Query

                # Default the bind and query class.
                kwargs.setdefault('bind', application.databases['default'])
                kwargs.setdefault('query_cls', Query)

                # Continue the initialization.
                super().__init__(*args, **kwargs)

            def __repr__(self):
                return '<alchemist.db.Session(bind=%r)>' % self.bind

        # Return the inner class.
        return Session

    # Create helper proxies to the scoped session.

    def commit(self):
        return self.session.commit()

    def rollback(self, *args, **kwargs):
        return self.session.rollback(*args, **kwargs)

    def add(self, *targets):
        """Add the passed targets to the local session."""
        return self.session.add_all(targets)

    def remove(self):
        """Remove the local reference to the session."""
        return self.Session.remove()


# Update the inner module with the actual contents.
instance = Module(__name__)
instance.__dict__.update(sys.modules[__name__].__dict__)

# Store the module wrapper
sys.modules[__name__] = instance
