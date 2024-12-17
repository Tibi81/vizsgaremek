from django.test import TestCase
from store.models import Product  

class ProductModelTest(TestCase):

    def setUp(self):
        """Tesztadatok létrehozása."""
        self.product = Product.objects.create(
            name="Teszt Termék",
            price=1000.0,
            discount_percentage=10,
            category="option1"
        )

    def test_product_creation(self):
        """Ellenőrzi, hogy a termék létrehozása helyesen működik."""
        product = self.product
        self.assertEqual(product.name, "Teszt Termék")
        self.assertEqual(product.price, 1000.0)
        self.assertEqual(product.discount_percentage, 10)
        self.assertEqual(product.category, "option1")

    def test_discounted_price(self):
        """Ellenőrzi, hogy az akciós ár számítása helyes."""
        product = self.product
        discounted_price = product.discounted_price
        self.assertEqual(discounted_price, 900.0)  # 10% kedvezmény levonva az árból

    def test_image_url(self):
        """Ellenőrzi, hogy az imageURL helyesen működik kép nélkül."""
        product = self.product
        self.assertEqual(product.imageURL, '')  # Nincs kép, ezért üres stringet várunk

    def test_category_choices(self):
        """Ellenőrzi, hogy a kategória helyesen kerül mentésre a választások közül."""
        product = self.product
        self.assertIn(product.category, dict(Product.CATEGORY_CHOICES))
