import json

from django.test import TestCase
from django.urls import reverse

from .models import Flavor, Scoop, IceCream, Order


class SerializationTestCase(TestCase):

    def setUp(self):
        self.flavor = Flavor.objects.create(flavor='vanilla')
        self.order = Order.objects.create()
        self.ice_cream = IceCream.objects.create(order=self.order)
        self.scoop = Scoop.objects.create(flavor=self.flavor, ice_cream=self.ice_cream, size=2)
        self.url = reverse('scoop-detail', args=[self.scoop.id])
        self.list_url = reverse('scoop-list')

    def test_not_expanded(self):
        response = self.client.get(self.url)
        expected = {
            'id': self.scoop.id,
            'size': self.scoop.size,
            'flavor': self.flavor.id,
            'ice_cream': self.ice_cream.id
        }
        self.assertEqual(response.json(), expected)

    def test_expanded(self):
        response = self.client.get(self.url+'?expand=flavor')
        expected = {
            'id': self.scoop.id,
            'size': self.scoop.size,
            'flavor': {
                'id': self.flavor.id,
                'flavor': self.flavor.flavor
            },
            'ice_cream': self.ice_cream.id,
        }
        self.assertEqual(response.json(), expected)

    def test_multiple_expanded(self):
        response = self.client.get(self.url+'?expand=flavor&expand=ice_cream')
        expected = {
            'id': self.scoop.id,
            'size': self.scoop.size,
            'flavor': {
                'id': self.flavor.id,
                'flavor': self.flavor.flavor
            },
            'ice_cream': {
                'id': self.ice_cream.id,
                'order': self.order.id,
                'with_waffle': self.ice_cream.with_waffle
            },
        }
        self.assertEqual(response.json(), expected)

    def test_nested_expansion(self):
        response = self.client.get(self.url + '?expand=ice_cream.order')
        expected = {
            'id': self.scoop.id,
            'size': self.scoop.size,
            'flavor': self.flavor.id,
            'ice_cream': {
                'id': self.ice_cream.id,
                'order': {
                    'id': self.order.id,
                    'paid': self.order.paid,
                },
                'with_waffle': self.ice_cream.with_waffle
            },
        }
        self.assertEqual(response.json(), expected)

    def test_list(self):
        """
        We need a separate test case for list vs. retrieve as listing
        non-transparantly adds another node to the parent chain, a
        ListSerializer.
        """
        response = self.client.get(self.list_url)
        expected = [
            {
                'id': self.scoop.id,
                'size': self.scoop.size,
                'flavor': self.flavor.id,
                'ice_cream': self.ice_cream.id
            }
        ]
        self.assertEqual(response.json(), expected)

    def test_list_expanded(self):
        """
        See SerializationTestCase.test_list.
        """
        response = self.client.get(self.list_url+'?expand=flavor')
        expected = [
            {
                'id': self.scoop.id,
                'size': self.scoop.size,
                'flavor': {
                    'id': self.flavor.id,
                    'flavor': self.flavor.flavor
                },
                'ice_cream': self.ice_cream.id,
            }
        ]
        self.assertEqual(response.json(), expected)


class DeSerializationTestCase(TestCase):
    """These tests are just as much for WritableNestedMixin as they are for ExpandableProxy."""

    def setUp(self):
        self.flavor = Flavor.objects.create(flavor='vanilla')
        self.order = Order.objects.create()
        self.ice_cream = IceCream.objects.create(order=self.order)
        self.scoop = Scoop.objects.create(flavor=self.flavor, ice_cream=self.ice_cream, size=2)
        self.create_url = reverse('scoop-list')
        self.update_url = reverse('scoop-detail', args=[self.scoop.id])

    def test_create_not_expanded(self):
        response = self.client.post(
            self.create_url,
            data={
                'size': 3,
                'flavor': self.flavor.id,
                'ice_cream': self.ice_cream.id
            }
        )

        scoop = Scoop.objects.last()
        expected = {
            'id': scoop.id,
            'size': scoop.size,
            'flavor': self.flavor.id,
            'ice_cream': self.ice_cream.id
        }
        self.assertEqual(response.json(), expected)

    def test_create_expanded(self):
        response = self.client.post(
            self.create_url + '?expand=ice_cream.order',
            data=json.dumps({
                'size': 3,
                'flavor': self.flavor.id,
                'ice_cream': {
                    'order': {
                        'paid': True
                    }
                }
            }),
            content_type='application/json'
        )
        scoop = Scoop.objects.last()
        ice_cream = IceCream.objects.last()
        order = Order.objects.last()
        expected = {
            'id': scoop.id,
            'size': scoop.size,
            'flavor': self.flavor.id,
            'ice_cream': {
                'id': ice_cream.id,
                'order': {
                    'id': order.id,
                    'paid': True
                },
                'with_waffle': ice_cream.with_waffle
            }
        }
        self.assertEqual(response.json(), expected)

    def test_update_expanded(self):
        response = self.client.patch(
            self.update_url + '?expand=ice_cream.order',
            data=json.dumps({
                'ice_cream': {
                    'order': {
                        'paid': True
                    }
                }
            }),
            content_type='application/json'
        )
        expected = {
            'id': self.scoop.id,
            'size': self.scoop.size,
            'flavor': self.flavor.id,
            'ice_cream': {
                'id': self.ice_cream.id,
                'with_waffle': self.ice_cream.with_waffle,
                'order': {
                    'id': self.order.id,
                    'paid': True
                }
            }
        }

        self.assertEqual(response.json(), expected)

    def test_errors(self):
        response = self.client.patch(
            self.update_url + '?expand=ice_cream.order',
            data=json.dumps({
                'size': 1,
                'ice_cream': {
                    'with_waffle': False,
                    'order': {
                        'paid': 'Invalid boolean'
                    }
                }
            }),
            content_type='application/json'
        )
        self.scoop.refresh_from_db()
        expected = {
            'ice_cream': {
                'order': {
                    'paid': ['Must be a valid boolean.']
                }
            }
        }
        self.assertEqual(response.json(), expected)

        # Ensure that they've not updated
        self.assertNotEqual(self.scoop.size, 1)
        self.assertNotEqual(self.ice_cream.with_waffle, False)
        self.assertNotEqual(self.order.paid, 'Invalid boolean')
