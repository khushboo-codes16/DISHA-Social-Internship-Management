from app.database import MongoDB
from datetime import datetime

class DataSync:
    def __init__(self):
        self.db = MongoDB()
    
    def sync_all_toli_members(self):
        """Sync all toli members with user data"""
        try:
            if not self.db.is_connected():
                return {'success': False, 'error': 'Database not connected'}
                
            tolis = self.db.get_all_tolis()
            sync_count = 0
            
            for toli_data in tolis:
                toli_id = str(toli_data['_id'])
                members = toli_data.get('members', [])
                
                # Update each member's data with current user info
                updated_members = []
                for member in members:
                    if isinstance(member, dict) and member.get('scholar_no'):
                        # Get current user data
                        user_data = self.db.get_user_by_scholar_no(member['scholar_no'])
                        if user_data:
                            updated_member = {
                                'name': user_data.get('name', member.get('name', '')),
                                'scholar_no': member['scholar_no'],
                                'course': user_data.get('course', member.get('course', '')),
                                'email': user_data.get('email', member.get('email', '')),
                                'contact': user_data.get('contact', member.get('contact', '')),
                                'is_leader': member.get('is_leader', False),
                                'last_synced': datetime.utcnow()
                            }
                            updated_members.append(updated_member)
                            sync_count += 1
                
                # Update toli with synced members
                if updated_members:
                    self.db.update_toli(toli_id, {'members': updated_members})
            
            return {'success': True, 'synced_count': sync_count}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_programs_data(self):
        """Ensure all programs have proper data references"""
        try:
            if not self.db.is_connected():
                return {'success': False, 'error': 'Database not connected'}
                
            programs = self.db.get_all_programs()
            updated_count = 0
            
            for program_data in programs:
                program_id = str(program_data['_id'])
                updates = {}
                
                # Ensure student data is referenced
                student_id = program_data.get('student_id')
                if student_id:
                    student_data = self.db.get_user_by_id(student_id)
                    if student_data:
                        updates['student_name'] = student_data.get('name', '')
                        updates['student_scholar_no'] = student_data.get('scholar_no', '')
                
                # Ensure toli data is referenced
                toli_id = program_data.get('toli_id')
                if toli_id:
                    toli_data = self.db.get_toli_by_id(toli_id)
                    if toli_data:
                        updates['toli_name'] = toli_data.get('name', '')
                        updates['toli_number'] = toli_data.get('toli_no', '')
                
                if updates:
                    self.db.update_program(program_id, updates)
                    updated_count += 1
            
            return {'success': True, 'updated_count': updated_count}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_data_consistency(self):
        """Verify and report data consistency issues"""
        if not self.db.is_connected():
            return ["Database not connected - cannot verify consistency"]
            
        issues = []
        
        try:
            # Check programs without student references
            programs = self.db.get_all_programs()
            for program in programs:
                if not program.get('student_id'):
                    issues.append(f"Program '{program.get('title')}' has no student reference")
                
                if not program.get('toli_id'):
                    issues.append(f"Program '{program.get('title')}' has no toli reference")
            
            # Check tolis with member inconsistencies
            tolis = self.db.get_all_tolis()
            for toli in tolis:
                members = toli.get('members', [])
                for member in members:
                    if isinstance(member, dict) and member.get('scholar_no'):
                        user_data = self.db.get_user_by_scholar_no(member['scholar_no'])
                        if not user_data:
                            issues.append(f"Toli '{toli.get('name')}' has invalid member: {member['scholar_no']}")
        
        except Exception as e:
            issues.append(f"Error during consistency check: {str(e)}")
        
        return issues
    
    def fix_data_inconsistencies(self):
        """Automatically fix common data inconsistencies"""
        if not self.db.is_connected():
            return {'success': False, 'error': 'Database not connected'}
            
        fixed_issues = []
        
        try:
            # Fix programs without proper references
            programs = self.db.get_all_programs()
            for program in programs:
                program_id = str(program['_id'])
                student_id = program.get('student_id')
                
                if student_id:
                    # Ensure student exists and update program with student data
                    student_data = self.db.get_user_by_id(student_id)
                    if student_data:
                        update_data = {
                            'student_name': student_data.get('name'),
                            'student_scholar_no': student_data.get('scholar_no')
                        }
                        self.db.update_program(program_id, update_data)
                        fixed_issues.append(f"Updated program '{program.get('title')}' with student data")
            
            return {'success': True, 'fixed_issues': fixed_issues}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}