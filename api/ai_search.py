from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer
import torch
from PIL import Image
import numpy as np
from django.conf import settings
import os
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class AISearchService:
    def __init__(self):
        try:
            # CLIP model cho tìm kiếm bằng hình ảnh
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            
            # Sentence transformer cho tìm kiếm bằng text
            self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Cache để lưu embeddings
            self.cache_dir = os.path.join(settings.BASE_DIR, 'ai_cache')
            os.makedirs(self.cache_dir, exist_ok=True)
            
            logger.info("AI models loaded successfully")
        except Exception as e:
            logger.error(f"Error loading AI models: {e}")
            raise
    
    def encode_image(self, image_path):
        """Encode hình ảnh thành vector"""
        try:
            # Kiểm tra cache
            cache_key = f"img_{hash(image_path)}.pkl"
            cache_path = os.path.join(self.cache_dir, cache_key)
            
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            
            # Encode image
            image = Image.open(image_path).convert('RGB')
            inputs = self.clip_processor(images=image, return_tensors="pt")
            
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
                image_vector = image_features.numpy().flatten()
            
            # Lưu cache
            with open(cache_path, 'wb') as f:
                pickle.dump(image_vector, f)
            
            return image_vector
            
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            return None
    
    def encode_text(self, text):
        """Encode text thành vector"""
        try:
            # Kiểm tra cache
            cache_key = f"txt_{hash(text)}.pkl"
            cache_path = os.path.join(self.cache_dir, cache_key)
            
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            
            # Encode text
            text_vector = self.text_model.encode(text)
            
            # Lưu cache
            with open(cache_path, 'wb') as f:
                pickle.dump(text_vector, f)
            
            return text_vector
            
        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            return None
    
    def search_by_image(self, query_image_path, products, top_k=10, min_similarity=0.4):
        """Tìm kiếm sản phẩm bằng hình ảnh"""
        try:
            query_vector = self.encode_image(query_image_path)
            if query_vector is None:
                return []
            
            similarities = []
            
            for product in products:
                if product.image and product.countInStock > 0:
                    try:
                        if hasattr(product.image, 'path'):
                            image_path = product.image.path
                        else:
                            image_path = os.path.join(settings.MEDIA_ROOT, str(product.image))
                        
                        if os.path.exists(image_path):
                            product_vector = self.encode_image(image_path)
                            if product_vector is not None:
                                similarity = cosine_similarity(
                                    [query_vector], [product_vector]
                                )[0][0]
                                # Chỉ thêm nếu độ tương đồng >= min_similarity
                                if similarity >= min_similarity:
                                    similarities.append((product.id, float(similarity)))
                    except Exception as e:
                        logger.warning(f"Error processing product {product.id}: {e}")
                        continue
            
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error in image search: {e}")
            return []
    
    def search_by_text(self, query_text, products, top_k=10, min_similarity=0.4):
        """Tìm kiếm sản phẩm bằng text"""
        try:
            query_vector = self.encode_text(query_text)
            if query_vector is None:
                return []
            
            similarities = []
            
            for product in products:
                if product.countInStock > 0:
                    try:
                        description = f"{product.name}"
                        if product.description:
                            description += f" {product.description}"
                        if hasattr(product, 'category') and product.category:
                            description += f" {product.category.title}"
                        
                        product_vector = self.encode_text(description)
                        if product_vector is not None:
                            similarity = cosine_similarity(
                                [query_vector], [product_vector]
                            )[0][0]
                            # Chỉ thêm nếu độ tương đồng >= min_similarity
                            if similarity >= min_similarity:
                                similarities.append((product.id, float(similarity)))
                        
                    except Exception as e:
                        logger.warning(f"Error processing product {product.id}: {e}")
                        continue
            
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Error in text search: {e}")
            return []
    
    def hybrid_search(self, query_text, query_image_path, products, top_k=10):
        """Tìm kiếm kết hợp text và image"""
        try:
            text_results = self.search_by_text(query_text, products, top_k * 2)
            image_results = self.search_by_image(query_image_path, products, top_k * 2)
            
            # Kết hợp kết quả
            combined_scores = {}
            
            # Thêm điểm từ text search
            for product_id, score in text_results:
                combined_scores[product_id] = score * 0.6  # 60% weight cho text
            
            # Thêm điểm từ image search
            for product_id, score in image_results:
                if product_id in combined_scores:
                    combined_scores[product_id] += score * 0.4  # 40% weight cho image
                else:
                    combined_scores[product_id] = score * 0.4
            
            # Sắp xếp kết quả
            final_results = sorted(
                combined_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            return final_results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []

# Singleton instance
ai_search_service = None

def get_ai_search_service():
    global ai_search_service
    if ai_search_service is None:
        ai_search_service = AISearchService()
    return ai_search_service




