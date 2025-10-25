from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
        try:
            # Get MongoDB Atlas URI from environment
            mongodb_uri = os.getenv('MONGODB_URI')
            database_name = os.getenv('DATABASE_NAME', 'disha_db')
            
            if not mongodb_uri:
                raise ValueError("MONGODB_URI environment variable is not set")
            
            # Connect to MongoDB Atlas with optimized settings
            self.client = MongoClient(
                mongodb_uri,
                # Connection pool settings
                maxPoolSize=50,
                minPoolSize=10,
                # Timeout settings
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                # Server selection timeout
                serverSelectionTimeoutMS=30000,
                # Retry writes
                retryWrites=True,
                w='majority'
            )
            
            self.db = self.client[database_name]
            
            # Test the connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB Atlas successfully!")
            print(f"✅ Database: {database_name}")
            print(f"✅ Cluster: disha-cluster")
            
        except Exception as e:
            print(f"❌ Error connecting to MongoDB Atlas: {e}")
            self.client = None
            self.db = None

    def is_connected(self):
        """Check if database is connected"""
        return self.db is not None

    def close_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("🔌 Database connection closed")

    # User methods
    def create_user(self, user_data):
        if not self.is_connected():
            return None
        return self.db.users.insert_one(user_data).inserted_id

    def get_user_by_id(self, user_id):
        if not self.is_connected():
            return None
        return self.db.users.find_one({'_id': ObjectId(user_id)})

    def get_user_by_email(self, email):
        if not self.is_connected():
            return None
        return self.db.users.find_one({'email': email})

    def get_user_by_scholar_no(self, scholar_no):
        if not self.is_connected():
            return None
        return self.db.users.find_one({'scholar_no': scholar_no})

    def get_all_users(self, role=None):
        if not self.is_connected():
            return []
        if role:
            return list(self.db.users.find({'role': role}))
        return list(self.db.users.find())

    def count_users_by_role(self, role):
        if not self.is_connected():
            return 0
        return self.db.users.count_documents({'role': role})

    def update_user(self, user_id, update_data):
        if not self.is_connected():
            return None
        return self.db.users.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})

    def get_students_without_toli(self):
        if not self.is_connected():
            return []
        return list(self.db.users.find({'role': 'student', 'toli_id': None}))

    # Toli methods
    def create_toli(self, toli_data):
        if not self.is_connected():
            return None
        return self.db.tolis.insert_one(toli_data).inserted_id

    def get_toli_by_id(self, toli_id):
        if not self.is_connected():
            return None
        return self.db.tolis.find_one({'_id': ObjectId(toli_id)})

    def get_all_tolis(self):
        if not self.is_connected():
            return []
        return list(self.db.tolis.find())

    def count_tolis(self):
        if not self.is_connected():
            return 0
        return self.db.tolis.count_documents({})

    def count_active_tolis(self):
        if not self.is_connected():
            return 0
        return self.db.tolis.count_documents({'status': 'active'})

    def update_toli(self, toli_id, update_data):
        if not self.is_connected():
            return None
        return self.db.tolis.update_one({'_id': ObjectId(toli_id)}, {'$set': update_data})

    def get_tolis_with_available_slots(self):
        if not self.is_connected():
            return []
        return list(self.db.tolis.find({'$expr': {'$lt': [{'$size': '$members'}, 4]}}))

    def get_tolis_by_session(self):
        if not self.is_connected():
            return []
        pipeline = [
            {'$group': {'_id': '$session_year', 'count': {'$sum': 1}}}
        ]
        return list(self.db.tolis.aggregate(pipeline))

    def get_average_members_per_toli(self):
        if not self.is_connected():
            return 0
        pipeline = [
            {'$project': {'member_count': {'$size': '$members'}}},
            {'$group': {'_id': None, 'average_members': {'$avg': '$member_count'}}}
        ]
        result = list(self.db.tolis.aggregate(pipeline))
        return result[0]['average_members'] if result else 0

    # Program methods
    def create_program(self, program_data):
        if not self.is_connected():
            return None
        return self.db.programs.insert_one(program_data).inserted_id

    def get_programs_by_toli(self, toli_id):
        if not self.is_connected():
            return []
        return list(self.db.programs.find({'toli_id': toli_id}))

    def get_programs_by_student(self, student_id):
        if not self.is_connected():
            return []
        return list(self.db.programs.find({'student_id': student_id}))

    def get_all_programs(self):
        if not self.is_connected():
            return []
        return list(self.db.programs.find())

    def count_programs(self):
        if not self.is_connected():
            return 0
        return self.db.programs.count_documents({})

    def count_pending_programs(self):
        if not self.is_connected():
            return 0
        return self.db.programs.count_documents({'status': 'pending'})

    # Resource methods
    def create_resource(self, resource_data):
        if not self.is_connected():
            return None
        return self.db.resources.insert_one(resource_data).inserted_id

    def get_resource_by_id(self, resource_id):
        if not self.is_connected():
            return None
        return self.db.resources.find_one({'_id': ObjectId(resource_id)})

    def get_all_resources(self):
        if not self.is_connected():
            return []
        return list(self.db.resources.find().sort('created_at', -1))

    def count_resources(self):
        if not self.is_connected():
            return 0
        return self.db.resources.count_documents({})

    def delete_resource(self, resource_id):
        if not self.is_connected():
            return None
        return self.db.resources.delete_one({'_id': ObjectId(resource_id)})

    def get_resources_by_type(self, resource_type):
        if not self.is_connected():
            return []
        return list(self.db.resources.find({'resource_type': resource_type}).sort('created_at', -1))

    def update_resource(self, resource_id, update_data):
        if not self.is_connected():
            return None
        return self.db.resources.update_one({'_id': ObjectId(resource_id)}, {'$set': update_data})

    # Message methods
    def create_message(self, message_data):
        if not self.is_connected():
            return None
        return self.db.messages.insert_one(message_data).inserted_id

    def get_message_by_id(self, message_id):
        if not self.is_connected():
            return None
        return self.db.messages.find_one({'_id': ObjectId(message_id)})

    def get_messages_for_user(self, user_id):
        """Get messages for a specific user (both direct and broadcast messages)"""
        if not self.is_connected():
            return []
        return list(self.db.messages.find({
            '$or': [
                {'receiver_id': user_id},
                {'receiver_id': None},  # Broadcast messages
                {'receiver_id': 'all'}  # Broadcast to all students
            ]
        }).sort('created_at', -1))

    def get_sent_messages(self, sender_id):
        """Get messages sent by a specific user"""
        if not self.is_connected():
            return []
        return list(self.db.messages.find({'sender_id': sender_id}).sort('created_at', -1))

    def get_broadcast_messages(self):
        """Get all broadcast messages"""
        if not self.is_connected():
            return []
        return list(self.db.messages.find({
            '$or': [
                {'receiver_id': None},
                {'receiver_id': 'all'}
            ]
        }).sort('created_at', -1))

    def update_message(self, message_id, update_data):
        if not self.is_connected():
            return None
        return self.db.messages.update_one({'_id': ObjectId(message_id)}, {'$set': update_data})

    def mark_message_as_read(self, message_id):
        if not self.is_connected():
            return None
        return self.db.messages.update_one({'_id': ObjectId(message_id)}, {'$set': {'is_read': True}})

    def delete_message(self, message_id):
        if not self.is_connected():
            return None
        return self.db.messages.delete_one({'_id': ObjectId(message_id)})

    def count_unread_messages(self, user_id):
        """Count unread messages for a user"""
        if not self.is_connected():
            return 0
        return self.db.messages.count_documents({
            '$or': [
                {'receiver_id': user_id},
                {'receiver_id': None},
                {'receiver_id': 'all'}
            ],
            'is_read': False
        })

    def count_messages(self):
        if not self.is_connected():
            return 0
        return self.db.messages.count_documents({})

    # Newsletter methods
    def create_newsletter(self, newsletter_data):
        if not self.is_connected():
            return None
        return self.db.newsletters.insert_one(newsletter_data).inserted_id

    def get_newsletter_by_id(self, newsletter_id):
        if not self.is_connected():
            return None
        return self.db.newsletters.find_one({'_id': ObjectId(newsletter_id)})

    def get_all_newsletters(self):
        if not self.is_connected():
            return []
        return list(self.db.newsletters.find({'status': 'published'}).sort('created_at', -1))

    def get_newsletters_by_toli(self, toli_name):
        if not self.is_connected():
            return []
        return list(self.db.newsletters.find({'toli_name': toli_name, 'status': 'published'}).sort('created_at', -1))

    def count_newsletters(self):
        if not self.is_connected():
            return 0
        return self.db.newsletters.count_documents({'status': 'published'})

    def update_newsletter(self, newsletter_id, update_data):
        if not self.is_connected():
            return None
        return self.db.newsletters.update_one({'_id': ObjectId(newsletter_id)}, {'$set': update_data})

    def delete_newsletter(self, newsletter_id):
        if not self.is_connected():
            return None
        return self.db.newsletters.delete_one({'_id': ObjectId(newsletter_id)})

    # Report methods
    def create_report(self, report_data):
        if not self.is_connected():
            return None
        return self.db.reports.insert_one(report_data).inserted_id

    def get_report_by_id(self, report_id):
        if not self.is_connected():
            return None
        return self.db.reports.find_one({'_id': ObjectId(report_id)})

    def get_reports_by_student(self, student_id):
        if not self.is_connected():
            return []
        return list(self.db.reports.find({'created_by': student_id}).sort('created_at', -1))

    def get_all_reports(self):
        if not self.is_connected():
            return []
        return list(self.db.reports.find().sort('created_at', -1))

    def get_reports_by_toli(self, toli_name):
        if not self.is_connected():
            return []
        return list(self.db.reports.find({'toli_name': toli_name}).sort('created_at', -1))

    def count_reports(self):
        if not self.is_connected():
            return 0
        return self.db.reports.count_documents({})

    # Additional utility methods
    def get_recent_resources(self, limit=5):
        if not self.is_connected():
            return []
        return list(self.db.resources.find().sort('created_at', -1).limit(limit))

    def get_recent_programs(self, limit=5):
        if not self.is_connected():
            return []
        return list(self.db.programs.find().sort('created_at', -1).limit(limit))

    def get_recent_tolis(self, limit=5):
        if not self.is_connected():
            return []
        return list(self.db.tolis.find().sort('created_at', -1).limit(limit))

    def get_recent_students(self, limit=5):
        if not self.is_connected():
            return []
        return list(self.db.users.find({'role': 'student'}).sort('created_at', -1).limit(limit))

    def get_recent_newsletters(self, limit=5):
        if not self.is_connected():
            return []
        return list(self.db.newsletters.find({'status': 'published'}).sort('created_at', -1).limit(limit))

    # Program methods (duplicate - keeping for compatibility)
    def get_programs_by_toli(self, toli_id):
        """Get all programs for a specific toli"""
        if not self.is_connected():
            return []
        return list(self.db.programs.find({'toli_id': toli_id}).sort('start_date', -1))

    def get_program_by_id(self, program_id):
        """Get program by ID"""
        if not self.is_connected():
            return None
        return self.db.programs.find_one({'_id': ObjectId(program_id)})

    def delete_program(self, program_id):
        """Delete a program"""
        if not self.is_connected():
            return None
        return self.db.programs.delete_one({'_id': ObjectId(program_id)})

    def get_programs_by_type(self):
        """Get program count by type"""
        if not self.is_connected():
            return []
        pipeline = [
            {'$group': {'_id': '$program_type', 'count': {'$sum': 1}}}
        ]
        return list(self.db.programs.aggregate(pipeline))

    def get_monthly_program_trends(self):
        """Get monthly program trends"""
        if not self.is_connected():
            return []
        pipeline = [
            {'$group': {
                '_id': {'$dateToString': {'format': '%Y-%m', 'date': '$start_date'}},
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        return list(self.db.programs.aggregate(pipeline))