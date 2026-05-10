from django.core.management.base import BaseCommand
from nole.models import Laptop
import random

class Command(BaseCommand):
    help = "Seed database với dữ liệu laptop"

    def handle(self, *args, **kwargs):
        
        # ❌ Nếu đã có dữ liệu thì không tạo lại
        if Laptop.objects.exists():
            self.stdout.write(self.style.WARNING("Đã có dữ liệu, bỏ qua!"))
            return

        brands = ["Dell", "Asus", "HP", "Apple", "Lenovo"]
        cpus = ["i5", "i7", "Ryzen 5", "Ryzen 7", "M1", "M2"]

        for i in range(15):
            Laptop.objects.create(
                name=f"Laptop {i+1}",
                brand=random.choice(brands),
                cpu=random.choice(cpus),
                ram=random.choice([8, 16, 32]),
                storage=random.choice([256, 512, 1024]),
                price=random.randint(10000000, 30000000)
            )

        self.stdout.write(self.style.SUCCESS("Seed data thành công!"))