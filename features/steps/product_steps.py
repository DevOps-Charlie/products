from os import getenv
import json
import requests
from behave import *
import server
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

WAIT_SECONDS = 30
#BASE_URL = getenv('BASE_URL', None)
# if not BASE_URL:
BASE_URL = getenv('BASE_URL', 'http://localhost:5000')


@given(u'the following products')
def step_impl(context):
    """ Delete all Pets and load new ones """
    headers = {'Content-Type': 'application/json'}
    context.resp = requests.delete(
        context.base_url + '/products/reset', headers=headers)
    #print ("HHHHHHHHHHETTTTTTTTTTTTT")
    #print (context.resp.status_code)
    assert context.resp.status_code == 204
    create_url = context.base_url + '/products'
    for row in context.table:
        data = {"name": row['name'], "category": row['category'],
                "color": row['color'], "count": row['count'],
                "price": row['price'], "description": row['description']}
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        assert context.resp.status_code == 201


@when(u'I visit the "home page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url + '/ui')


@then(u'I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    assert message in context.driver.title


@then(u'I should not see "{message}"')
def step_impl(context, message):
    assert message not in context.resp.text


@when(u'I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = 'product_' + element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)

##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clean button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################


@when(u'I press the "{button}" button')
def step_impl(context, button):
    button = button.replace(' ', '-').lower()
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()


@then(u'I should see "{name}" in the results')
def step_impl(context, name):
    #element = context.driver.find_element_by_id('search_results')
    #assert name in element.text

    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_results'),
            name
        )
    )
    expect(found).to_be(True)


@then(u'I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('search_results')
    assert name not in element.text


@then(u'I should see the message "{message}"')
def step_impl(context, message):
    #element = context.driver.find_element_by_id('flash_message')
    #assert message in element.text
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    expect(found).to_be(True)

##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by 'pet_' so the Name field has an id='pet_name'
# We can then lowercase the name and prefix with pet_ to get the id
##################################################################


@then(u'I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = 'product_' + element_name.lower()
    #element = context.driver.find_element_by_id(element_id)
    #assert text_string in element.get_attribute('value')
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    # expect(element.get_attribute('value')).to_equal(text_string)
    expect(found).to_be(True)


@when(u'I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = 'product_' + element_name.lower()
    #element = context.driver.find_element_by_id(element_id)
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)


# @then(u'I should see "{message}" in "{field}"')
# def step_impl(context, message, field):
#     """ Check a field for text """
#     element = context.driver.find_element_by_id(field)
#     assert message in element.text

# @when(u'I change "{key}" to "{value}"')
# def step_impl(context, key, value):
#     context.data[key] = value
