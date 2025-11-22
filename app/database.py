from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import urllib.parse

# Load environment variables
load_dotenv()

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB with enhanced error handling"""
        try:
            # Get MongoDB Atlas URI from environment
            mongodb_uri = os.getenv('MONGODB_URI')
            database_name = os.getenv('DATABASE_NAME', 'disha_db')
            
            if not mongodb_uri:
                print("❌ MONGODB_URI environment variable is not set")
                print("💡 Please check your .env file")
                return
            
            print(f"🔗 Attempting to connect to MongoDB...")
            print(f"📁 Database: {database_name}")
            
            # Connect to MongoDB Atlas with enhanced settings
            self.client = MongoClient(
                mongodb_uri,
                # Reduced timeouts for better error handling
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                serverSelectionTimeoutMS=10000,
                retryWrites=True,
                # Direct connection to avoid SRV issues
                connect=False  # Don't connect immediately
            )
            
            self.db = self.client[database_name]
            
            # Test the connection with a simple command
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB Atlas successfully!")
            print(f"✅ Database: {database_name}")
            
        except Exception as e:
            print(f"❌ Error connecting to MongoDB Atlas: {e}")
            print("💡 Troubleshooting steps:")
            print("1. Check your internet connection")
            print("2. Verify MONGODB_URI in .env file")
            print("3. Check if MongoDB Atlas IP is whitelisted")
            print("4. Try using direct connection string")
            
            # Fallback: Try local MongoDB if available
            try:
                print("🔄 Attempting fallback to local MongoDB...")
                self.client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
                self.db = self.client[database_name]
                self.client.admin.command('ping')
                print("✅ Connected to local MongoDB successfully!")
            except Exception as local_error:
                print(f"❌ Local MongoDB also failed: {local_error}")
                self.client = None
                self.db = None

    def is_connected(self):
        """Check if database is connected"""
        if self.client is None:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except:
            return False

    def close_connection(self):
        """Close the database connection"""
        if self.client:
            try:
                self.client.close()
                print("✅ Database connection closed")
            except Exception as e:
                print(f"⚠️ Error closing database connection: {e}")

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
        """Get all programs for a specific toli with error handling"""
        if not self.is_connected():
            print("❌ Database not connected")
            return []
        try:
            # Convert to string if ObjectId
            toli_id_str = str(toli_id)
            
            # Try both string and ObjectId formats
            programs = list(self.db.programs.find({
                '$or': [
                    {'toli_id': toli_id_str},
                    {'toli_id': ObjectId(toli_id_str) if ObjectId.is_valid(toli_id_str) else None}
                ]
            }).sort('created_at', -1))
            
            print(f"✅ Found {len(programs)} programs for toli_id: {toli_id_str}")
            return programs
        except Exception as e:
            print(f"❌ Error fetching programs for toli: {e}")
            return []

    def get_programs_by_student(self, student_id):
        """Get all programs for a specific student with error handling"""
        if not self.is_connected():
            print("❌ Database not connected")
            return []
        try:
            return list(self.db.programs.find({'student_id': student_id}).sort('created_at', -1))
        except Exception as e:
            print(f"❌ Error fetching programs: {e}")
            return []

    def get_report_by_program(self, program_id):
        """Get report by program ID with error handling"""
        if not self.is_connected():
            return None
        try:
            return self.db.reports.find_one({'program_id': program_id})
        except Exception as e:
            print(f"❌ Error fetching report: {e}")
            return None

    def update_program(self, program_id, update_data):
        if not self.is_connected():
            return None
        return self.db.programs.update_one({'_id': ObjectId(program_id)}, {'$set': update_data})

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

    def get_recent_newsletters(self, limit=5):
        if not self.is_connected():
            return []
        return list(self.db.newsletters.find({'status': 'published'}).sort('created_at', -1).limit(limit))

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

    def get_users_by_toli(self, toli_id):
        """Get all users belonging to a specific toli"""
        if not self.is_connected():
            return []
        try:
            if isinstance(toli_id, str):
                toli_id = ObjectId(toli_id)
            return list(self.db.users.find({'toli_id': toli_id}))
        except Exception as e:
            print(f"Error getting users by toli: {e}")
            return []

    def get_toli_by_name(self, toli_name):
        """Get toli by name"""
        if not self.is_connected():
            return None
        try:
            return self.db.tolis.find_one({'name': toli_name})
        except Exception as e:
            print(f"Error getting toli by name: {e}")
            return None

    def update_user_toli(self, user_id, toli_id):
        """Update user's toli assignment with validation"""
        if not self.is_connected():
            return False
        try:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            if isinstance(toli_id, str) and toli_id != 'None':
                toli_id = ObjectId(toli_id)
            elif toli_id == 'None':
                toli_id = None
        
            update_data = {
                'toli_id': toli_id,
                'updated_at': datetime.utcnow()
            }
        
            result = self.db.users.update_one(
                {'_id': user_id},
                {'$set': update_data}
            )
        
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user toli: {e}")
            return False

    def get_recent_tolis(self, limit=5, hours=24):
        """Get recent tolis created within specified hours"""
        if not self.is_connected():
            return []
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            return list(self.db.tolis.find({
                'created_at': {'$gte': cutoff_time}
            }).sort('created_at', -1).limit(limit))
        except Exception as e:
            print(f"Error getting recent tolis: {e}")
            return []

    def get_recent_students(self, limit=5, hours=24):
        """Get recent students registered within specified hours"""
        if not self.is_connected():
            return []
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            return list(self.db.users.find({
                'role': 'student',
                'created_at': {'$gte': cutoff_time}
            }).sort('created_at', -1).limit(limit))
        except Exception as e:
            print(f"Error getting recent students: {e}")
            return []

    def get_recent_programs(self, limit=5, hours=24):
        """Get recent programs created within specified hours"""
        if not self.is_connected():
            return []
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            return list(self.db.programs.find({
                'created_at': {'$gte': cutoff_time}
            }).sort('created_at', -1).limit(limit))
        except Exception as e:
            print(f"Error getting recent programs: {e}")
            return []

    # ==================== INSTRUCTION METHODS ====================
    
    def get_active_instruction(self):
        """Get the active instruction document"""
        if not self.is_connected():
            return None
        try:
            return self.db.instructions.find_one({'is_active': True})
        except Exception as e:
            print(f"Error getting active instruction: {e}")
            return None
    
    def create_instruction(self, instruction_data):
        """Create a new instruction"""
        if not self.is_connected():
            return None
        try:
            # Deactivate all existing instructions
            self.db.instructions.update_many({}, {'$set': {'is_active': False}})
            
            # Insert new instruction
            result = self.db.instructions.insert_one(instruction_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating instruction: {e}")
            return None
    
    def update_instruction(self, instruction_id, update_data):
        """Update an instruction"""
        if not self.is_connected():
            return False
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.db.instructions.update_one(
                {'_id': ObjectId(instruction_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating instruction: {e}")
            return False
    
    def get_instruction_by_id(self, instruction_id):
        """Get instruction by ID"""
        if not self.is_connected():
            return None
        try:
            return self.db.instructions.find_one({'_id': ObjectId(instruction_id)})
        except Exception as e:
            print(f"Error getting instruction: {e}")
            return None
