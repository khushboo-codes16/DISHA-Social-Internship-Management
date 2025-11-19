"""
Toli Analytics Module
Analyzes toli performance and engagement
"""

from datetime import datetime, timedelta
from collections import Counter


class ToliAnalytics:
    """Analytics for tolis"""
    
    def __init__(self, db):
        self.db = db
    
    def get_toli_summary(self):
        """Get overall toli summary statistics"""
        try:
            tolis = self.db.get_all_tolis()
            
            if not tolis:
                return {
                    'total_tolis': 0,
                    'active_tolis': 0,
                    'total_members': 0,
                    'avg_members_per_toli': 0
                }
            
            active_tolis = sum(1 for t in tolis if t.get('status') == 'active')
            total_members = sum(len(t.get('members', [])) for t in tolis)
            
            return {
                'total_tolis': len(tolis),
                'active_tolis': active_tolis,
                'pending_tolis': sum(1 for t in tolis if t.get('status') == 'pending'),
                'total_members': total_members,
                'avg_members_per_toli': total_members // len(tolis) if tolis else 0
            }
        except Exception as e:
            print(f"Error in get_toli_summary: {e}")
            return {}
    
    def get_toli_performance(self):
        """Get performance metrics for each toli"""
        try:
            tolis = self.db.get_all_tolis()
            performance_data = []
            
            for toli in tolis:
                toli_id = str(toli.get('_id'))
                programs = self.db.get_programs_by_toli(toli_id)
                
                # Calculate metrics
                total_programs = len(programs)
                total_participants = sum(p.get('total_persons', 0) for p in programs)
                
                # Program types diversity
                program_types = set(p.get('program_type') for p in programs if p.get('program_type'))
                
                # Calculate engagement score (0-100)
                engagement_score = self._calculate_engagement_score(
                    total_programs,
                    total_participants,
                    len(toli.get('members', []))
                )
                
                performance_data.append({
                    'toli_id': toli_id,
                    'toli_name': toli.get('name', 'Unknown'),
                    'toli_no': toli.get('toli_no', 'N/A'),
                    'status': toli.get('status', 'unknown'),
                    'member_count': len(toli.get('members', [])),
                    'program_count': total_programs,
                    'total_participants': total_participants,
                    'avg_participants': total_participants // total_programs if total_programs > 0 else 0,
                    'program_diversity': len(program_types),
                    'engagement_score': engagement_score,
                    'location': toli.get('location', {}).get('city', 'Not assigned')
                })
            
            # Sort by engagement score
            performance_data.sort(key=lambda x: x['engagement_score'], reverse=True)
            
            return performance_data
        except Exception as e:
            print(f"Error in get_toli_performance: {e}")
            return []
    
    def get_toli_comparison_chart_data(self):
        """Get data formatted for comparison charts"""
        try:
            performance = self.get_toli_performance()
            
            return {
                'labels': [t['toli_name'] for t in performance[:10]],  # Top 10
                'programs': [t['program_count'] for t in performance[:10]],
                'participants': [t['total_participants'] for t in performance[:10]],
                'engagement': [t['engagement_score'] for t in performance[:10]]
            }
        except Exception as e:
            print(f"Error in get_toli_comparison_chart_data: {e}")
            return {}
    
    def get_location_effectiveness(self):
        """Analyze effectiveness of different locations"""
        try:
            tolis = self.db.get_all_tolis()
            location_data = {}
            
            for toli in tolis:
                location = toli.get('location', {})
                city = location.get('city', 'Not assigned')
                state = location.get('state', 'Unknown')
                
                if city not in location_data:
                    location_data[city] = {
                        'state': state,
                        'toli_count': 0,
                        'total_programs': 0,
                        'total_participants': 0,
                        'active_tolis': 0
                    }
                
                location_data[city]['toli_count'] += 1
                
                if toli.get('status') == 'active':
                    location_data[city]['active_tolis'] += 1
                
                # Get programs for this toli
                toli_id = str(toli.get('_id'))
                programs = self.db.get_programs_by_toli(toli_id)
                location_data[city]['total_programs'] += len(programs)
                location_data[city]['total_participants'] += sum(p.get('total_persons', 0) for p in programs)
            
            # Calculate effectiveness score
            for city in location_data:
                data = location_data[city]
                effectiveness = (
                    (data['total_programs'] * 0.4) +
                    (data['total_participants'] * 0.3) +
                    (data['active_tolis'] * 10 * 0.3)
                )
                location_data[city]['effectiveness_score'] = round(effectiveness, 2)
            
            return location_data
        except Exception as e:
            print(f"Error in get_location_effectiveness: {e}")
            return {}
    
    def get_member_engagement_analysis(self):
        """Analyze member engagement across tolis"""
        try:
            tolis = self.db.get_all_tolis()
            engagement_data = {
                'highly_engaged': 0,  # >5 programs
                'moderately_engaged': 0,  # 2-5 programs
                'low_engaged': 0,  # 1 program
                'inactive': 0  # 0 programs
            }
            
            for toli in tolis:
                toli_id = str(toli.get('_id'))
                programs = self.db.get_programs_by_toli(toli_id)
                program_count = len(programs)
                member_count = len(toli.get('members', []))
                
                if member_count == 0:
                    continue
                
                # Categorize based on programs per member
                programs_per_member = program_count / member_count if member_count > 0 else 0
                
                if programs_per_member > 5:
                    engagement_data['highly_engaged'] += member_count
                elif programs_per_member >= 2:
                    engagement_data['moderately_engaged'] += member_count
                elif programs_per_member >= 1:
                    engagement_data['low_engaged'] += member_count
                else:
                    engagement_data['inactive'] += member_count
            
            return engagement_data
        except Exception as e:
            print(f"Error in get_member_engagement_analysis: {e}")
            return {}
    
    def get_toli_growth_trend(self):
        """Get toli creation trend over time"""
        try:
            tolis = self.db.get_all_tolis()
            monthly_growth = {}
            
            # Initialize last 6 months
            for i in range(6):
                month_date = datetime.utcnow() - timedelta(days=30 * i)
                month_key = month_date.strftime('%Y-%m')
                monthly_growth[month_key] = 0
            
            # Count tolis created per month
            for toli in tolis:
                created_at = toli.get('created_at')
                if created_at:
                    if isinstance(created_at, str):
                        try:
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        except:
                            continue
                    
                    month_key = created_at.strftime('%Y-%m')
                    if month_key in monthly_growth:
                        monthly_growth[month_key] += 1
            
            return [
                {'month': month, 'count': count}
                for month, count in sorted(monthly_growth.items())
            ]
        except Exception as e:
            print(f"Error in get_toli_growth_trend: {e}")
            return []
    
    def _calculate_engagement_score(self, programs, participants, members):
        """Calculate engagement score (0-100)"""
        try:
            if members == 0:
                return 0
            
            # Factors:
            # - Programs per member (40%)
            # - Participants per program (30%)
            # - Overall activity (30%)
            
            programs_per_member = programs / members if members > 0 else 0
            avg_participants = participants / programs if programs > 0 else 0
            
            # Normalize scores
            program_score = min(programs_per_member * 10, 40)  # Max 40 points
            participant_score = min(avg_participants / 2, 30)  # Max 30 points
            activity_score = min(programs * 2, 30)  # Max 30 points
            
            total_score = program_score + participant_score + activity_score
            
            return round(min(total_score, 100), 2)
        except Exception as e:
            print(f"Error calculating engagement score: {e}")
            return 0
    
    def get_top_performing_tolis(self, limit=5):
        """Get top performing tolis"""
        try:
            performance = self.get_toli_performance()
            return performance[:limit]
        except Exception as e:
            print(f"Error in get_top_performing_tolis: {e}")
            return []
    
    def get_tolis_needing_attention(self, limit=5):
        """Get tolis that need attention (low engagement)"""
        try:
            performance = self.get_toli_performance()
            # Filter tolis with low engagement
            low_engagement = [t for t in performance if t['engagement_score'] < 30]
            return low_engagement[:limit]
        except Exception as e:
            print(f"Error in get_tolis_needing_attention: {e}")
            return []
