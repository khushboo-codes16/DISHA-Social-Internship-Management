"""
Image Processor Module
Handles image processing, categorization, and quality assessment
"""

import os
from PIL import Image
import hashlib
from datetime import datetime


class ImageProcessor:
    """Process and analyze images"""
    
    def __init__(self, upload_path='static/uploads'):
        self.upload_path = upload_path
        self.gallery_path = os.path.join(upload_path, 'gallery')
        self.thumbnail_path = os.path.join(upload_path, 'thumbnails')
        
        # Create directories if they don't exist
        os.makedirs(self.gallery_path, exist_ok=True)
        os.makedirs(self.thumbnail_path, exist_ok=True)
        
        # Program type keywords for categorization
        self.category_keywords = {
            'Yagya': ['yagya', 'havan', 'fire', 'ritual', 'ceremony'],
            'Yoga': ['yoga', 'asana', 'meditation', 'exercise', 'fitness'],
            'Community Service': ['community', 'service', 'help', 'volunteer', 'social'],
            'Health Camp': ['health', 'medical', 'doctor', 'checkup', 'camp'],
            'Tree Plantation': ['tree', 'plant', 'green', 'environment', 'nature'],
            'Educational': ['education', 'school', 'teaching', 'learning', 'student'],
            'Cultural': ['cultural', 'dance', 'music', 'art', 'performance']
        }
    
    def process_image(self, image_file, program_data=None):
        """
        Process uploaded image
        
        Args:
            image_file: File object
            program_data: Dictionary with program information
        
        Returns:
            Dictionary with processed image information
        """
        try:
            # Open image
            img = Image.open(image_file)
            
            # Get image info
            image_info = {
                'original_size': img.size,
                'format': img.format,
                'mode': img.mode
            }
            
            # Quality assessment
            quality_score = self._assess_quality(img)
            image_info['quality_score'] = quality_score
            
            # Auto-categorize if program data provided
            if program_data:
                category = self._categorize_image(program_data)
                image_info['category'] = category
            
            # Generate unique filename
            filename = self._generate_filename(image_file.filename)
            
            # Save original
            original_path = os.path.join(self.gallery_path, filename)
            img.save(original_path, quality=95)
            image_info['path'] = f'uploads/gallery/{filename}'
            
            # Create thumbnail
            thumbnail_filename = f'thumb_{filename}'
            thumbnail_path = os.path.join(self.thumbnail_path, thumbnail_filename)
            self._create_thumbnail(img, thumbnail_path)
            image_info['thumbnail'] = f'uploads/thumbnails/{thumbnail_filename}'
            
            # Calculate file hash for duplicate detection
            image_file.seek(0)
            file_hash = hashlib.md5(image_file.read()).hexdigest()
            image_info['hash'] = file_hash
            
            return image_info
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return None
    
    def _assess_quality(self, img):
        """
        Assess image quality (0-100)
        Based on resolution, sharpness, and other factors
        """
        try:
            width, height = img.size
            pixels = width * height
            
            # Resolution score (max 50 points)
            if pixels >= 1920 * 1080:  # Full HD or better
                resolution_score = 50
            elif pixels >= 1280 * 720:  # HD
                resolution_score = 40
            elif pixels >= 640 * 480:  # VGA
                resolution_score = 30
            else:
                resolution_score = 20
            
            # Aspect ratio score (max 20 points)
            aspect_ratio = width / height if height > 0 else 0
            if 1.3 <= aspect_ratio <= 1.8:  # Good aspect ratio
                aspect_score = 20
            else:
                aspect_score = 10
            
            # Format score (max 15 points)
            if img.format in ['JPEG', 'PNG']:
                format_score = 15
            else:
                format_score = 10
            
            # Mode score (max 15 points)
            if img.mode == 'RGB':
                mode_score = 15
            elif img.mode == 'RGBA':
                mode_score = 12
            else:
                mode_score = 8
            
            total_score = resolution_score + aspect_score + format_score + mode_score
            
            return min(total_score, 100)
            
        except Exception as e:
            print(f"Error assessing quality: {e}")
            return 50  # Default score
    
    def _categorize_image(self, program_data):
        """
        Categorize image based on program data
        """
        try:
            program_type = program_data.get('program_type', '').lower()
            title = program_data.get('title', '').lower()
            description = program_data.get('achievements', '').lower()
            
            # Combine all text
            text = f"{program_type} {title} {description}"
            
            # Check keywords
            category_scores = {}
            for category, keywords in self.category_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text)
                if score > 0:
                    category_scores[category] = score
            
            # Return category with highest score
            if category_scores:
                return max(category_scores, key=category_scores.get)
            
            # Default to program type if no match
            return program_data.get('program_type', 'General')
            
        except Exception as e:
            print(f"Error categorizing image: {e}")
            return 'General'
    
    def _create_thumbnail(self, img, output_path, size=(300, 300)):
        """Create thumbnail of image"""
        try:
            # Create a copy
            thumb = img.copy()
            
            # Resize maintaining aspect ratio
            thumb.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            thumb.save(output_path, quality=85)
            
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
    
    def _generate_filename(self, original_filename):
        """Generate unique filename"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        ext = os.path.splitext(original_filename)[1]
        unique_id = hashlib.md5(f"{original_filename}{timestamp}".encode()).hexdigest()[:8]
        return f"{timestamp}_{unique_id}{ext}"
    
    def detect_duplicates(self, image_hash, existing_hashes):
        """Check if image is duplicate"""
        return image_hash in existing_hashes
    
    def enhance_image(self, image_path):
        """
        Enhance image quality
        (Placeholder for future ML-based enhancement)
        """
        try:
            img = Image.open(image_path)
            
            # Basic enhancement
            from PIL import ImageEnhance
            
            # Increase sharpness slightly
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.2)
            
            # Increase contrast slightly
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)
            
            # Save enhanced image
            img.save(image_path, quality=95)
            
            return True
            
        except Exception as e:
            print(f"Error enhancing image: {e}")
            return False
    
    def extract_metadata(self, image_file):
        """Extract image metadata"""
        try:
            img = Image.open(image_file)
            
            metadata = {
                'size': img.size,
                'format': img.format,
                'mode': img.mode,
                'info': img.info
            }
            
            # Try to get EXIF data
            try:
                from PIL.ExifTags import TAGS
                exif_data = img._getexif()
                if exif_data:
                    metadata['exif'] = {
                        TAGS.get(tag, tag): value
                        for tag, value in exif_data.items()
                    }
            except:
                pass
            
            return metadata
            
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return {}
    
    def batch_process_images(self, image_files, program_data=None):
        """Process multiple images at once"""
        results = []
        
        for image_file in image_files:
            result = self.process_image(image_file, program_data)
            if result:
                results.append(result)
        
        return results
    
    def get_image_stats(self):
        """Get statistics about processed images"""
        try:
            gallery_files = os.listdir(self.gallery_path)
            
            total_images = len(gallery_files)
            total_size = sum(
                os.path.getsize(os.path.join(self.gallery_path, f))
                for f in gallery_files
            )
            
            return {
                'total_images': total_images,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'avg_size_mb': round(total_size / (1024 * 1024) / total_images, 2) if total_images > 0 else 0
            }
            
        except Exception as e:
            print(f"Error getting image stats: {e}")
            return {}
