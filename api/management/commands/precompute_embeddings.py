from django.core.management.base import BaseCommand
from api.models import Product
from api.ai_search import get_ai_search_service
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Pre-compute embeddings for all products to improve search speed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recompute all embeddings even if cache exists',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting embedding pre-computation...')
        
        try:
            ai_service = get_ai_search_service()
            products = Product.objects.filter(countInStock__gt=0)
            
            total_products = products.count()
            processed = 0
            
            for product in products:
                try:
                    # Pre-compute text embedding
                    description = f"{product.name}"
                    if product.description:
                        description += f" {product.description}"
                    if hasattr(product, 'category') and product.category:
                        # Sửa: dùng 'title' thay vì 'name'
                        description += f" {product.category.title}"
                    
                    ai_service.encode_text(description)
                    
                    # Pre-compute image embedding if image exists
                    if product.image:
                        try:
                            if hasattr(product.image, 'path'):
                                image_path = product.image.path
                            else:
                                image_path = os.path.join(settings.MEDIA_ROOT, str(product.image))
                            
                            if os.path.exists(image_path):
                                ai_service.encode_image(image_path)
                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(f'Failed to process image for product {product.id}: {e}')
                            )
                    
                    processed += 1
                    if processed % 10 == 0:
                        self.stdout.write(f'Processed {processed}/{total_products} products...')
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to process product {product.id}: {e}')
                    )
                    continue
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully pre-computed embeddings for {processed} products')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to initialize AI service: {e}')
            )

