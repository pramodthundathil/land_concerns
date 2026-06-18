from django.test import TestCase
from django.utils.text import slugify
from Home.models import Projects, Services

class SlugUniqueTestCase(TestCase):
    def test_project_slug_uniqueness(self):
        # Create first project
        p1 = Projects.objects.create(
            project_title="Land for Sale at Elamakkara",
            project_subname="Elamakkara, Kochi",
            project_category="Land",
            price=1500000.00
        )
        self.assertEqual(p1.slug, "land-for-sale-at-elamakkara")
        
        # Create second project with duplicate title
        p2 = Projects.objects.create(
            project_title="Land for Sale at Elamakkara",
            project_subname="Elamakkara, Kochi",
            project_category="Land",
            price=2000000.00
        )
        self.assertEqual(p2.slug, "land-for-sale-at-elamakkara-1")
        
        # Create third project with duplicate title
        p3 = Projects.objects.create(
            project_title="Land for Sale at Elamakkara",
            project_subname="Elamakkara, Kochi",
            project_category="Land",
            price=2500000.00
        )
        self.assertEqual(p3.slug, "land-for-sale-at-elamakkara-2")

    def test_service_slug_uniqueness(self):
        # Create first service
        s1 = Services.objects.create(
            title="Premium Architecture",
            description="Service Description"
        )
        self.assertEqual(s1.slug, "premium-architecture")
        
        # Create second service with duplicate title
        s2 = Services.objects.create(
            title="Premium Architecture",
            description="Service Description"
        )
        self.assertEqual(s2.slug, "premium-architecture-1")

class VisitorMiddlewareTestCase(TestCase):
    def setUp(self):
        from django.test import RequestFactory
        from Home.middleware import VisitorMiddleware
        self.factory = RequestFactory()
        self.middleware = VisitorMiddleware(get_response=lambda r: None)

    def test_first_visit_creates_record(self):
        from Home.models import Visitor
        request = self.factory.get('/')
        self.middleware(request)
        self.assertEqual(Visitor.objects.count(), 1)

    def test_sequential_visits_reuses_record(self):
        from Home.models import Visitor
        request = self.factory.get('/')
        self.middleware(request)
        self.middleware(request)
        self.assertEqual(Visitor.objects.count(), 1)

    def test_concurrent_visits_race_condition(self):
        from unittest.mock import patch
        from Home.models import Visitor
        request = self.factory.get('/')
        
        # Mock filter().exists() to always return False to simulate a race condition
        # where two concurrent threads check the database at the same time and both see no record.
        with patch('Home.models.Visitor.objects.filter') as mock_filter:
            mock_filter.return_value.exists.return_value = False
            
            # The first call will create the record.
            self.middleware(request)
            self.assertEqual(Visitor.objects.count(), 1)
            
            # The second call will also try to create the record because filter().exists() is mocked to False.
            # Because of the database unique constraint, django will raise an IntegrityError inside
            # Visitor.objects.create, which the middleware should catch and handle.
            try:
                self.middleware(request)
            except Exception as e:
                self.fail(f"VisitorMiddleware failed to handle the concurrent request: {e}")
            
            # Count should still be 1
            self.assertEqual(Visitor.objects.count(), 1)
