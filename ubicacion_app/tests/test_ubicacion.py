from odoo.tests.common import TransactionCase


class TestUbicacion(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(TestUbicacion, self).setUp(*args, **kwargs)
        # Prepare environment with the Admin user
        user_admin = self.env.ref('base.user_admin')
        self.env = self.env(user=user_admin)
        # Setup test data
        self.Ubicacion = self.env['ubicacion']
        self.ubicacion_ode = self.Ubicacion.create({
            'name': 'Odoo Development Essentials',
            'isbn': '978-1-78439-279-6'})
        return result

    def test_create(self):
        "Test Ubicacion are active by default"
        self.assertEqual(self.ubicacion_ode.active, True)

    def test_check_isbn(self):
        "Check valid ISBN"
        self.assertTrue(self.ubicacion_ode._check_isbn())
