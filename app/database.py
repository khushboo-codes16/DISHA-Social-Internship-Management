from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

class MongoDB:
    def __init__(self):
        try:
            self.client = MongoClient('mongodb://localhost:27017/')
            self.db = self.client['disha_db']
            print("Connected to MongoDB successfully!")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

    # User methods
    def create_user(self, user_data):
        return self.db.users.insert_one(user_data).inserted_id

    def get_user_by_id(self, user_id):
        return self.db.users.find_one({'_id': ObjectId(user_id)})

    def get_user_by_email(self, email):
        return self.db.users.find_one({'email': email})

    def get_user_by_scholar_no(self, scholar_no):
        return self.db.users.find_one({'scholar_no': scholar_no})

    def get_all_users(self, role=None):
        if role:
            return list(self.db.users.find({'role': role}))
        return list(self.db.users.find())

    def count_users_by_role(self, role):
        return self.db.users.count_documents({'role': role})

    def update_user(self, user_id, update_data):
        return self.db.users.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})

    def get_students_without_toli(self):
        return list(self.db.users.find({'role': 'student', 'toli_id': None}))

    # Toli methods
    def create_toli(self, toli_data):
        return self.db.tolis.insert_one(toli_data).inserted_id

    def get_toli_by_id(self, toli_id):
        return self.db.tolis.find_one({'_id': ObjectId(toli_id)})

    def get_all_tolis(self):
        return list(self.db.tolis.find())

    def count_tolis(self):
        return self.db.tolis.count_documents({})

    def count_active_tolis(self):
        return self.db.tolis.count_documents({'status': 'active'})

    def update_toli(self, toli_id, update_data):
        return self.db.tolis.update_one({'_id': ObjectId(toli_id)}, {'$set': update_data})

    def get_tolis_with_available_slots(self):
        # Return tolis with less than 4 members
        return list(self.db.tolis.find({'$expr': {'$lt': [{'$size': '$member_ids'}, 4]}}))

    def get_tolis_by_session(self):
        pipeline = [
            {'$group': {'_id': '$session_year', 'count': {'$sum': 1}}}
        ]
        return list(self.db.tolis.aggregate(pipeline))

    def get_average_members_per_toli(self):
        pipeline = [
            {'$project': {'member_count': {'$size': '$member_ids'}}},
            {'$group': {'_id': None, 'average_members': {'$avg': '$member_count'}}}
        ]
        result = list(self.db.tolis.aggregate(pipeline))
        return result[0]['average_members'] if result else 0

    # Program methods
    def create_program(self, program_data):
        return self.db.programs.insert_one(program_data).inserted_id

    def get_programs_by_toli(self, toli_id):
        return list(self.db.programs.find({'toli_id': toli_id}))

    def get_programs_by_student(self, student_id):
        return list(self.db.programs.find({'student_id': student_id}))

    def get_all_programs(self):
        return list(self.db.programs.find())

    def count_programs(self):
        return self.db.programs.count_documents({})

    def count_pending_programs(self):
        return self.db.programs.count_documents({'status': 'pending'})

    # Resource methods
    def create_resource(self, resource_data):
        return self.db.resources.insert_one(resource_data).inserted_id

    def get_all_resources(self):
        return list(self.db.resources.find().sort('created_at', -1))

    def count_resources(self):
        return self.db.resources.count_documents({})

    # Message methods
    def create_message(self, message_data):
        return self.db.messages.insert_one(message_data).inserted_id

    def get_messages_for_user(self, user_id):
        return list(self.db.messages.find({
            '$or': [
                {'receiver_id': user_id},
                {'receiver_id': None}  # Broadcast messages
            ]
        }).sort('created_at', -1))