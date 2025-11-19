"""
Gallery Manager Module
Manages gallery images, auto-upload, and categorization
"""

from datetime import datetime
from .image_processor import ImageProcessor


class GalleryManager:
    """Manage gallery images and auto-upload from programs"""
    
    def __init__(self, db):
        self.db = db
        self.image_processor = ImageProcessor()
    
    def auto_upload_program_images(self, program_id, image_files, program_data):
        """
        Automatically upload program images to gallery
        
        Args:
            program_id: Program ID
            image_files: List of image files
            program_data: Program information
        
        Returns:
            List of gallery image records
        """
        try:
            gallery_images = []
            
            for image_file in image_files:
                # Process image
                image_info = self.image_processor.process_image(image_file, program_data)
                
                if not image_info:
                    continue
                
                # Only add high-quality images to gallery
                if image_info['quality_score'] >= 60:
                    gallery_record = {
                        'program_id': program_id,
                        'image_path': image_info['path'],
                        'thumbnail_path': image_info['thumbnail'],
                        'category': image_info['category'],
                        'quality_score': image_info['quality_score'],
                        'hash': image_info['hash'],
                        'program_type': program_data.get('program_type'),
                        'program_title': program_data.get('title'),
                        'location': program_data.get('city', 'Unknown'),
                        'state': program_data.get('state', 'Unknown'),
                        'toli_id': program_data.get('toli_id'),
                        'uploaded_at': datetime.utcnow(),
                        'is_featured': False,
                        'views': 0,
                        'tags': self._generate_tags(program_data)
                    }
                    
                    # Save to database
                    gallery_id = self.db.db.gallery.insert_one(gallery_record).inserted_id
                    gallery_record['_id'] = gallery_id
                    gallery_images.append(gallery_record)
            
            return gallery_images
            
        except Exception as e:
            print(f"Error auto-uploading images: {e}")
            return []
    
    def get_gallery_images(self, filters=None, limit=50, skip=0):
        """
        Get gallery images with optional filters
        
        Args:
            filters: Dictionary of filters (category, program_type, location, etc.)
            limit: Number of images to return
            skip: Number of images to skip (for pagination)
        
        Returns:
            List of gallery images
        """
        try:
            query = {}
            
            if filters:
                if filters.get('category'):
                    query['category'] = filters['category']
                if filters.get('program_type'):
                    query['program_type'] = filters['program_type']
                if filters.get('location'):
                    query['location'] = filters['location']
                if filters.get('toli_id'):
                    query['toli_id'] = filters['toli_id']
                if filters.get('is_featured'):
                    query['is_featured'] = True
            
            images = list(self.db.db.gallery.find(query)
                         .sort('uploaded_at', -1)
                         .limit(limit)
                         .skip(skip))
            
            return images
            
        except Exception as e:
            print(f"Error getting gallery images: {e}")
            return []
    
    def get_gallery_by_category(self):
        """Get images grouped by category"""
        try:
            pipeline = [
                {'$group': {
                    '_id': '$category',
                    'count': {'$sum': 1},
                    'images': {'$push': {
                        'image_path': '$image_path',
                        'thumbnail_path': '$thumbnail_path',
                        'program_title': '$program_title',
                        'quality_score': '$quality_score'
                    }}
                }},
                {'$sort': {'count': -1}}
            ]
            
            results = list(self.db.db.gallery.aggregate(pipeline))
            
            # Limit images per category to 10 for preview
            for result in results:
                result['images'] = result['images'][:10]
            
            return results
            
        except Exception as e:
            print(f"Error getting gallery by category: {e}")
            return []
    
    def search_gallery(self, search_term):
        """
        Search gallery by keywords
        
        Args:
            search_term: Search string
        
        Returns:
            List of matching images
        """
        try:
            query = {
                '$or': [
                    {'program_title': {'$regex': search_term, '$options': 'i'}},
                    {'category': {'$regex': search_term, '$options': 'i'}},
                    {'program_type': {'$regex': search_term, '$options': 'i'}},
                    {'location': {'$regex': search_term, '$options': 'i'}},
                    {'tags': {'$in': [search_term.lower()]}}
                ]
            }
            
            results = list(self.db.db.gallery.find(query)
                          .sort('uploaded_at', -1)
                          .limit(50))
            
            return results
            
        except Exception as e:
            print(f"Error searching gallery: {e}")
            return []
    
    def mark_as_featured(self, image_id):
        """Mark image as featured"""
        try:
            from bson import ObjectId
            self.db.db.gallery.update_one(
                {'_id': ObjectId(image_id)},
                {'$set': {'is_featured': True}}
            )
            return True
        except Exception as e:
            print(f"Error marking as featured: {e}")
            return False
    
    def increment_views(self, image_id):
        """Increment view count"""
        try:
            from bson import ObjectId
            self.db.db.gallery.update_one(
                {'_id': ObjectId(image_id)},
                {'$inc': {'views': 1}}
            )
            return True
        except Exception as e:
            print(f"Error incrementing views: {e}")
            return False
    
    def get_gallery_stats(self):
        """Get gallery statistics"""
        try:
            total_images = self.db.db.gallery.count_documents({})
            
            # Images by category
            category_pipeline = [
                {'$group': {'_id': '$category', 'count': {'$sum': 1}}}
            ]
            categories = list(self.db.db.gallery.aggregate(category_pipeline))
            
            # Most viewed images
            most_viewed = list(self.db.db.gallery.find()
                              .sort('views', -1)
                              .limit(10))
            
            # Recent uploads
            recent = list(self.db.db.gallery.find()
                         .sort('uploaded_at', -1)
                         .limit(10))
            
            return {
                'total_images': total_images,
                'categories': {cat['_id']: cat['count'] for cat in categories},
                'most_viewed': most_viewed,
                'recent_uploads': recent
            }
            
        except Exception as e:
            print(f"Error getting gallery stats: {e}")
            return {}
    
    def delete_image(self, image_id):
        """Delete image from gallery"""
        try:
            from bson import ObjectId
            import os
            
            # Get image record
            image = self.db.db.gallery.find_one({'_id': ObjectId(image_id)})
            
            if image:
                # Delete files
                try:
                    if image.get('image_path'):
                        os.remove(os.path.join('static', image['image_path']))
                    if image.get('thumbnail_path'):
                        os.remove(os.path.join('static', image['thumbnail_path']))
                except:
                    pass
                
                # Delete from database
                self.db.db.gallery.delete_one({'_id': ObjectId(image_id)})
                return True
            
            return False
            
        except Exception as e:
            print(f"Error deleting image: {e}")
            return False
    
    def _generate_tags(self, program_data):
        """Generate tags from program data"""
        tags = []
        
        # Add program type as tag
        if program_data.get('program_type'):
            tags.append(program_data['program_type'].lower())
        
        # Add location as tag
        if program_data.get('city'):
            tags.append(program_data['city'].lower())
        
        if program_data.get('state'):
            tags.append(program_data['state'].lower())
        
        # Extract keywords from title
        if program_data.get('title'):
            title_words = program_data['title'].lower().split()
            # Add significant words (length > 3)
            tags.extend([word for word in title_words if len(word) > 3])
        
        # Remove duplicates
        tags = list(set(tags))
        
        return tags[:10]  # Limit to 10 tags
    
    def get_featured_images(self, limit=10):
        """Get featured images for homepage"""
        try:
            images = list(self.db.db.gallery.find({'is_featured': True})
                         .sort('views', -1)
                         .limit(limit))
            
            # If not enough featured images, get high-quality recent ones
            if len(images) < limit:
                additional = list(self.db.db.gallery.find({
                    'is_featured': False,
                    'quality_score': {'$gte': 80}
                }).sort('uploaded_at', -1).limit(limit - len(images)))
                
                images.extend(additional)
            
            return images
            
        except Exception as e:
            print(f"Error getting featured images: {e}")
            return []
    
    def get_related_images(self, image_id, limit=6):
        """Get related images based on category and tags"""
        try:
            from bson import ObjectId
            
            # Get current image
            current = self.db.db.gallery.find_one({'_id': ObjectId(image_id)})
            
            if not current:
                return []
            
            # Find similar images
            query = {
                '_id': {'$ne': ObjectId(image_id)},
                '$or': [
                    {'category': current.get('category')},
                    {'program_type': current.get('program_type')},
                    {'tags': {'$in': current.get('tags', [])}}
                ]
            }
            
            related = list(self.db.db.gallery.find(query)
                          .sort('quality_score', -1)
                          .limit(limit))
            
            return related
            
        except Exception as e:
            print(f"Error getting related images: {e}")
            return []
