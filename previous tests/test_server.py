""" Test cases for the Product Model """

import logging
import unittest
import json
from mock import MagicMock, patch
from flask_api import status    # HTTP Status Codes
import server

######################################################################
#  T E S T   C A S E S
######################################################################
class TestProductServer(unittest.TestCase):
    """ Product Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        server.app.debug = False
        # server.initialize_logging(logging.ERROR)

    def setUp(self):
        """ Runs before each test """
        server.Product.remove_all()
        server.Product(0, 'Asus2500', 'Laptop', '234', 'qerwrw', 'erwwfwf').save()
        server.Product(0, 'GE4509', 'Microwave','34324', 'wewef', 'fwfwsxdws' ).save()
        self.app = server.app.test_client()

    def tearDown(self):
        """ Runs after each test """
        server.Product.remove_all()

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'Product Demo REST API Service')

    def test_get_pet_list(self):
        """ Get a list of Pets """
        resp = self.app.get('/Products')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)

    def test_get_pet(self):
        """ Get one Pet """
        resp = self.app.get('/Products/2')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'GE4509')

    def test_get_pet_not_found(self):
        """ Get a Pet thats not found """
        resp = self.app.get('/Products/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_pet(self):
        """ Create a Pet """
        # save the current number of pets for later comparrison
        pet_count = self.get_pet_count()
        # add a new pet
        new_pet = {'name': 'High_Sierra', 'category': 'Bag', 'price': '1234', 'description': 'Cool Bag','color':'blue' }
        data = json.dumps(new_pet)
        resp = self.app.post('/Products', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['name'], 'High_Sierra')
        # check that count has gone up and includes sammy
        resp = self.app.get('/Products')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), pet_count + 1)
        self.assertIn(new_json, data)

    def test_update_pet(self):
        """ Update a Pet """
        new_kitty = {'name': 'GE4509', 'category': 'Microwave','price':'1000','description':'Dont buy','color':'faded'}
        data = json.dumps(new_kitty)
        resp = self.app.put('/Products/2', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.get('/Products/2', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['price'], '1000')

    def test_update_pet_with_no_name(self):
        """ Update a Pet with no name """
        new_pet = {'category': 'Microwave','price':'1200','description':'Dont buy','color':'faded'}
        data = json.dumps(new_pet)
        resp = self.app.put('/Products/2', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_pet_not_found(self):
        """ Update a Pet that can't be found """
        new_kitty = {'name': 'GE4509', 'category': 'Microwave','price':'1000','description':'Dont buy','color':'faded'}
        data = json.dumps(new_kitty)
        resp = self.app.put('/Products/0', data=data, content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_pet(self):
        """ Delete a Pet that exists """
        # save the current number of pets for later comparrison
        pet_count = self.get_pet_count()
        # delete a pet
        resp = self.app.delete('/Products/2', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_pet_count()
        self.assertEqual(new_count, pet_count - 1)

    def test_create_pet_with_no_name(self):
        """ Create a Pet with the name missing """
        new_pet = {'category': 'Microwave','price':'1000','description':'Dont buy','color':'faded'}
        data = json.dumps(new_pet)
        resp = self.app.post('/Products', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_nonexisting_pet(self):
        """ Get a Pet that doesn't exist """
        resp = self.app.get('/Products/5')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_pet_list_by_category(self):
        """ Query Pets by Category """
        resp = self.app.get('/Products', query_string='category=Microwave')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        self.assertTrue('GE4509' in resp.data)
        self.assertFalse('Asus2500' in resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['category'], 'Microwave')

    def test_query_pet_list_by_name(self):
        """ Query Pets by Name """
        resp = self.app.get('/Products', query_string='name=GE4509')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        self.assertTrue('GE4509' in resp.data)
        self.assertFalse('Asus2500' in resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['name'], 'GE4509')

    # def test_method_not_allowed(self):
    #     """ Call a Method thats not Allowed """
    #     resp = self.app.post('/pets/0')
    #     self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # @patch('server.Pet.find_by_name')
    # def test_bad_request(self, bad_request_mock):
    #     """ Test a Bad Request error from Find By Name """
    #     bad_request_mock.side_effect = ValueError()
    #     resp = self.app.get('/pets', query_string='name=fido')
    #     self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # @patch('server.Pet.find_by_name')
    # def test_mock_search_data(self, pet_find_mock):
    #     """ Test showing how to mock data """
    #     pet_find_mock.return_value = [MagicMock(serialize=lambda: {'name': 'fido'})]
    #     resp = self.app.get('/pets', query_string='name=fido')
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)


######################################################################
# Utility functions
######################################################################

    def get_pet_count(self):
        """ save the current number of pets """
        resp = self.app.get('/Products')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
