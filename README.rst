Django Restframework Expandable Proxy
-------------------------------------
ExpandableProxy is a utility object for Django RestFramework that allows
clients to expand primitive fields into nested objects, based on URL
parameters.::

    import requests

    >>> requests.get('http://localhost:8000/book/1/').json()
    {'id': 1, 'title': 'Dune', 'author': 1}

    >>> requests.get('http://localhost:8000/book/1/?expand=author').json()
    {'id': 1, 'title': 'Dune', 'author': {'id': 2, 'name': 'Frank Herbert'}}

Setup
^^^^^
ExpandableProxy is used as a serializer field. Instantiate an instance passing
what field to use for the non-expanded representation and what serializer to
use for the expanded case as arguments.::

    from rest_framework import serializers
    from drf_expandable_proxy import ExpandableProxy
    from .models import Author, Book


    class AuthorSerializer(serializers.ModelSerializer):

        class Meta:
            model = Author
            fields = ('id', 'name')


    class BookSerializer(serializers.ModelSerializer):

        author = ExpandableProxy(
            serializer=AuthorSerializer(),
            field=serializers.PrimaryKeyRelatedField(queryset=Author.objects.all()),
        )

        class Meta:
            model = Book
            fields = ('id', 'title', 'author')

Features
^^^^^^^^
Expand multiple objects
~~~~~~~~~~~~~~~~~~~~~~~
You can expand multiple objects at once by identifying multiple items in the
expand array, e.g.::

    'http://localhost:8000/book/1/?expand=author&expand=publisher'

Nested expansion
~~~~~~~~~~~~~~~~
You can expand recursively by specifying nested fields after a dot, e.g.::

    'http://localhost:8000/book/1/?expand=publisher.company'

Custom expansion behaviour
~~~~~~~~~~~~~~~~~~~~~~~~~~
To customize the expansion behaviour, subclass ExpandableProxy and override
the 'expanded' property.::

    class GetExpandableProxy(ExpandableProxy):
        """Subclass of ExpandableProxy that expands on all GET-requests.

        @property
        def expanded(self):
            return self.context['request'].method == 'GET'

Expansion on create or update
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
ExpandableProxy is read only be default, just as standard nested serializers
are, as there are too many different expected behaviors/use cases, most of them
incompatible with each other, to support. The project does however feature a
serializer mixin which covers the most common (my) use case by delegating to
the expanded serializers create and update methods.::

    from drf_expandable_proxy import ExpandableProxy


    class WritableBookSerializer(WritableNestedMixin, BookSerializer):
        pass

Development
^^^^^^^^^^^
To run the tests, clone the repository, setup the virtual environment, and run
the tests.::

    # Setup the virtual environment
    $ virtualenv test_env
    $ source test_env/bin/activate
    $ pip3 install -r test_requirements.txt

    # Run the tests
    $ cd tests
    $ python3 manage.py test
