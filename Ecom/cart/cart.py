from store.models import Product

# Customer sessions Shopping Cart
class Cart():
    def __init__(self, request):
        self.session = request.session

        # Get the current session Key if it exists
        cart = self.session.get("session_key")

        # If the user is new (no session key), create a new session key
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # Make sure cart is available on all pages on the site
        self.cart = cart

    def add(self, product):
        product_id = str(product.id)
        
        # Check if product is already in the cart
        if product_id in self.cart:
            pass
        else:
            self.cart[product_id] = {'price': str(product.price)}

        self.session.modified = True

    def __len__(self):
        return len(self.cart)
    
    def get_prods(self):
        # get IDs of products from the cart
        product_ids = self.cart.keys()
        # USe IDs to lookup products in the database model
        products = Product.objects.filter(id__in=product_ids)
        # return those looked up products
        return products

        