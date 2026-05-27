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
