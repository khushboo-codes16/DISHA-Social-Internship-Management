from app.database import MongoDB
from bson import ObjectId
from datetime import datetime

class DatabaseFixes:
    def __init__(self):
        self.db = MongoDB()
    
    def update_toli_comprehensive(self, toli_id, update_data):
        """Comprehensive toli update with proper error handling"""
        try:
            # Ensure toli_id is ObjectId
            if isinstance(toli_id, str):
                toli_id = ObjectId(toli_id)
            
            # Add updated_at timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            # Update the toli
            result = self.db.tolis.update_one(
                {'_id': toli_id},
                {'$set': update_data}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating toli: {e}")
            return False
    
    def update_program_comprehensive(self, program_id, update_data):
        """Comprehensive program update with proper error handling"""
        try:
            # Ensure program_id is ObjectId
            if isinstance(program_id, str):
                program_id = ObjectId(program_id)
            
            # Add updated_at timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            # Update the program
            result = self.db.programs.update_one(
                {'_id': program_id},
                {'$set': update_data}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating program: {e}")
            return False
    
    def sync_toli_members(self, toli_id):
        """Sync toli members with student toli_id assignments"""
        try:
            toli_data = self.db.get_toli_by_id(toli_id)
            if not toli_data:
                return False
            
            # Get all students in this toli
            students = self.db.get_users_by_toli(toli_id)
            
            # Update toli members list
            updated_members = []
            for student in students:
                member_info = {
                    'name': student.get('name'),
                    'scholar_no': student.get('scholar_no'),
                    'course': student.get('course'),
                    'email': student.get('email'),
                    'is_leader': student.get('_id') == toli_data.get('leader_id')
                }
                updated_members.append(member_info)
            
            # Update toli with synced members
            return self.update_toli_comprehensive(toli_id, {'members': updated_members})
            
        except Exception as e:
            print(f"Error syncing toli members: {e}")
            return False
    
    def refresh_all_data(self):
        """Force refresh all data connections"""
        try:
            # Close and reopen connection
            self.db.close_connection()
            # Reinitialize connection
            self.db.__init__()
            return True
        except Exception as e:
            print(f"Error refreshing data: {e}")
            return False