Sections:

* How to run the project on your computer
* Possible Issues
* API
    * Adding an item to the cart
    * Removing an item from the cart
    * Making a purchase
    * View a user's order history
* Further Improvements

**Installation/How to run the Project**

Step 1) Check that you are at the level that contains the env/ directory (the same level that also has this README file) and activate the virtual env by running:
    `source env/bin/activate`

    Possible issue: You do not have virtualenv. To install it run:
        `pip install virtualenv`
        Then try `source env/bin/activate` again.


Step 2) Go into the ecommercesite/ directory and install the dependencies by running:
    ```
    cd ecommercesite/
    pip install -r requirements.txt
    ```

    Possible issue: You do not have pip and so you cannot do any of the above.
        Unlikely because pip is already installed if you're using Python 2 >=2.7.9 or Python 3 >=3.4
        You can check by running:
        `pip --version`

        If you have pip but it is not working as it should (installing the dependencies) try updating it by running:
        `pip install -U pip`

    If you ran `pip install -r requirements.txt` it should have installed Django 1.11 and 
    Django Rest Framework.
    Check if you have the right Django version by running:
        `python -c "import django; print(django.get_version())`

    Possible issue: The dependencies are not installing.
        The above should definitely work, but just in case, you can make your own
        virtual environment and install the two dependencies this project uses. You
        can do this by running:
            ```
            pip install virtualenv
            virtualenv name_you_want_for_your_virtual_env
            source name_you_want_for_your_virtual_env/bin/activate
            pip install django
            pip install djangorestframework
            ```

Step 3) You should still be in the directory ecommercesite/ which contains the manage.py file.
    Start the server:
        `python manage.py runserver`

Step 4) Keep the server running on that tab and then open another terminal tab. Run the curl commands from the API section below in that tab.

Step 5) It's simpler to just use the curl commands, but you can also interact with the API
using the Django Rest interface. Just go to `http://localhost:8000/` ( or the port your development server is running on) in your browser. You'll need to login. The username is `admin` and the password is `password123`. The endpoints
to use the interface are below in the API section after each curl command.

**Other possible issues**

1) You are getting an error that says `'ImportError: No module named django.core.management`':
    That means you don't have django installed. Check by running `python -c "import django; print(django.get_version())`
2) If you are getting that error but you do have django installed, it might be that django is installed on your computer in a directory path that is unaccessible to the project. Try pip installing:

    `pip install django`

3) If you are still having issues and the server is not starting check that you have the dependencies installed (django and django rest framework). 
If `pip install -r requirements.txt` did not work and you don't have django or requirements you can pip install the 2 dependencies.
```
    pip install django
    pip install djangorestframework
```
Those 2 dependencies are all you need.

4) `Six` issue when installing packages
  * go here: github.com/pypa/pip/issues/3165


**API**

You can interact with the API either using curl commands in the terminal or the
Django Rest Framework interface. Both included in each section, but using
curl commands is simpler and faster.

*Adding an item to the cart*

Curl

Using Terminal

Keep the server running and on another tab use the curl command.

endpoint is `/carts/<card_id>/add_to_cart/` and you have to send the product id
of the product you want to add to the cart and the quantity.
Try this:

```
curl -X PUT http://127.0.0.1:8000/carts/1/add_to_cart/ -d "product_id=1&quantity=2" -H 'Accept: application/json; indent=4' -u admin:password123

```

Using Django Rest Interface

First login (username = `admin` password = `password123`) then go to:

`http://localhost:8000/carts/1/add_to_cart/`

If you scroll to the bottom you will see a section to make a PUT request.
In the content section add `{"product_id":1, "quantity"=2}` and hit the PUT button.

The response will be the serialized cart, but it won't display the nested cart
items. This was a decision when implementing the serializers and deciding on which to display the reverse relationship. Seeing the serialized cart means the request was successful otherwise
you'll see
```
{
    "status": "fail"
}
```

To check things in the shell
Get to the directory with manage.py file and then run `./manage.py shell`
```
>>> from shop.models import *
>>> u = User.objects.get(id=1)
>>> u.cart.items.all()
<QuerySet [<CartItem: CartItem object>]>
>>> u.cart.items.values_list('product__title','quantity')
<QuerySet [(u'tshirt', 2)]>
```

*Removing an item from the cart*

Using Terminal

endpoint is `/carts/<card_id>/remove_from_cart/` and you have to send the product id
of the product you want to remove from the cart. Items are removed one by one so
the quantity is always 1.

Try this:

```
curl -X PUT http://127.0.0.1:8000/carts/1/remove_from_cart/ -d "product_id=1" -H 'Accept: application/json; indent=4' -u admin:password123

```

Using Django Rest Interface

`http://localhost:8000/carts/1/remove_from_cart/`

If you scroll to the bottom you will see a section to make a PUT request.
In the content section add `{"product_id":1}` and hit the PUT button.

Same as adding to the cart, removing from it the response will be the serialized cart, but it won't display the nested cart items because of how the relationship was handled in the
serializers.

To check things in the shell
Get to the directory with manage.py file and then run `./manage.py shell`
```
>>> from shop.models import *
>>> u = User.objects.get(id=1)
>>> u.cart.items.all()
<QuerySet [(u'tshirt', 1)]>
```

*Making a purchase*

Using Terminal

endpoint is `/orders/` and you have to send the purchaser id (the user id of the customer making the purchase/order). An Order is created with the contents of the user's cart.

Try this:

```
curl -X POST -H "Content-Type:application/json; indent=4" -d '{"purchaser":1}' -u admin:password123 http://127.0.0.1:8000/orders/

```

Using Django Rest Interface


`http://localhost:8000/orders/`

If you scroll to the bottom you will see a section to make a POST request.
In the content section add:
```
{
    "total": null
    "purchaser": 1
}
```
Then hit the POST button.

To check things in the shell
Get to the directory with manage.py file and then run `./manage.py shell`
```
>>> from shop.models import *
>>> u = User.objects.get(id=1)
>>> u.orders.all()
<QuerySet [(u'tshirt', 1)]>
>>> u.orders.values_list('created_at')
<QuerySet [(datetime.datetime(2017, 6, 8, 2, 44, 27, 428748, tzinfo=<UTC>)]
>>> u.cart.items.all()
<QuerySet []>
```
Cart should be empty after creating an Order.

*View a user's order history*

Using Terminal

endpoint is `/orders/order_history/?user_id=<user_id>`

Try this:

```
curl -X GET http://127.0.0.1:8000/orders/order_history/?user_id=1 -H 'Accept application/json; indent=4' -u admin:password123

```

Using Django Rest Interface

`http://localhost:8000/orders/order_history/?user_id=1`

You'll see the json for all of the user's orders.

To check things in the shell
Get to the directory with manage.py file and then run `./manage.py shell`
```
>>> from shop.models import *
>>> u = User.objects.get(id=1)
>>> u.orders.all()
<QuerySet [<Order: Order object>]>
```

**Further Improvements**

    * Consistency on deletion versus disassociation. Right now if the quantity of the product to remove from the cart is 1 the cart item is deleted. But when an order is created and the cart is emptied, the cart items are not deleted, just disassociated from the cart. That means
    for example, that insights can be gained from cart items that were previously in a customer's cart. If that's a use case then they should potentially not be deleted when removed from the cart.

    * Some of the logic in the API views should be decomped to model methods.

    * Billing information should be added to the Order model.

