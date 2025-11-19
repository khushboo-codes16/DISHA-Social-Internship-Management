"""
Program Analytics Module
Analyzes program data and generates insights
"""

from datetime import datetime, timedelta
from collections import Counter
import json


class ProgramAnalytics:
    """Analytics for programs"""
    
    def __init__(self, db):
        self.db = db
    
    def get_program_summary(self):
        """Get overall program summary statistics"""
        try:
            programs = self.db.get_all_programs()
            
            if not programs:
                return {
                    'total_programs': 0,
                    'total_participants': 0,
                    'program_types': {},
                    'locations': {},
                    'monthly_trend': []
                }
            
            total_participants = sum(p.get('total_persons', 0) for p in programs)
            
            # Program types distribution
            program_types = Counter(p.get('program_type', 'Unknown') for p in programs)
            
            # Location distribution
            locations = Counter(p.get('city', 'Unknown') for p in programs if p.get('city'))
            
            # Monthly trend (last 6 months)
            monthly_data = self._calculate_monthly_trend(programs)
            
            return {
                'total_programs': len(programs),
                'total_participants': total_participants,
                'avg_participants': total_participants // len(programs) if programs else 0,
                'program_types': dict(program_types.most_common(10)),
                'locations': dict(locations.most_common(10)),
                'monthly_trend': monthly_data
            }
        except Exception as e:
            print(f"Error in get_program_summary: {e}")
            return {}
    
    def get_toli_program_comparison(self):
        """Compare programs across different tolis"""
        try:
            tolis = self.db.get_all_tolis()
            comparison_data = []
            
            for toli in tolis:
                toli_id = str(toli.get('_id'))
                programs = self.db.get_programs_by_toli(toli_id)
                
                comparison_data.append({
                    'toli_name': toli.get('name', 'Unknown'),
                    'toli_no': toli.get('toli_no', 'N/A'),
                    'program_count': len(programs),
                    'total_participants': sum(p.get('total_persons', 0) for p in programs),
                    'status': toli.get('status', 'unknown')
                })
            
            # Sort by program count
            comparison_data.sort(key=lambda x: x['program_count'], reverse=True)
            
            return comparison_data
        except Exception as e:
            print(f"Error in get_toli_program_comparison: {e}")
            return []
    
    def get_program_type_analytics(self):
        """Detailed analytics for each program type"""
        try:
            programs = self.db.get_all_programs()
            type_analytics = {}
            
            for program in programs:
                ptype = program.get('program_type', 'Unknown')
                
                if ptype not in type_analytics:
                    type_analytics[ptype] = {
                        'count': 0,
                        'total_participants': 0,
                        'locations': set(),
                        'tolis': set()
                    }
                
                type_analytics[ptype]['count'] += 1
                type_analytics[ptype]['total_participants'] += program.get('total_persons', 0)
                
                if program.get('city'):
                    type_analytics[ptype]['locations'].add(program.get('city'))
                
                if program.get('toli_id'):
                    type_analytics[ptype]['tolis'].add(str(program.get('toli_id')))
            
            # Convert sets to counts
            for ptype in type_analytics:
                type_analytics[ptype]['unique_locations'] = len(type_analytics[ptype]['locations'])
                type_analytics[ptype]['unique_tolis'] = len(type_analytics[ptype]['tolis'])
                type_analytics[ptype]['avg_participants'] = (
                    type_analytics[ptype]['total_participants'] // type_analytics[ptype]['count']
                    if type_analytics[ptype]['count'] > 0 else 0
                )
                # Remove sets (not JSON serializable)
                del type_analytics[ptype]['locations']
                del type_analytics[ptype]['tolis']
            
            return type_analytics
        except Exception as e:
            print(f"Error in get_program_type_analytics: {e}")
            return {}
    
    def get_geographic_distribution(self):
        """Get geographic distribution of programs"""
        try:
            programs = self.db.get_all_programs()
            geo_data = {}
            
            for program in programs:
                state = program.get('state', 'Unknown')
                city = program.get('city', 'Unknown')
                
                if state not in geo_data:
                    geo_data[state] = {
                        'total_programs': 0,
                        'cities': {},
                        'total_participants': 0
                    }
                
                geo_data[state]['total_programs'] += 1
                geo_data[state]['total_participants'] += program.get('total_persons', 0)
                
                if city not in geo_data[state]['cities']:
                    geo_data[state]['cities'][city] = 0
                geo_data[state]['cities'][city] += 1
            
            return geo_data
        except Exception as e:
            print(f"Error in get_geographic_distribution: {e}")
            return {}
    
    def _calculate_monthly_trend(self, programs):
        """Calculate monthly program trend for last 6 months"""
        try:
            now = datetime.utcnow()
            monthly_counts = {}
            
            # Initialize last 6 months
            for i in range(6):
                month_date = now - timedelta(days=30 * i)
                month_key = month_date.strftime('%Y-%m')
                monthly_counts[month_key] = 0
            
            # Count programs per month
            for program in programs:
                created_at = program.get('created_at')
                if created_at:
                    if isinstance(created_at, str):
                        try:
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        except:
                            continue
                    
                    month_key = created_at.strftime('%Y-%m')
                    if month_key in monthly_counts:
                        monthly_counts[month_key] += 1
            
            # Convert to list format for charts
            trend_data = [
                {'month': month, 'count': count}
                for month, count in sorted(monthly_counts.items())
            ]
            
            return trend_data
        except Exception as e:
            print(f"Error in _calculate_monthly_trend: {e}")
            return []
    
    def get_one_month_analytics(self):
        """Get analytics for the 1-month internship period"""
        try:
            programs = self.db.get_all_programs()
            
            # Filter programs from last 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            recent_programs = []
            
            for program in programs:
                created_at = program.get('created_at')
                if created_at:
                    if isinstance(created_at, str):
                        try:
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        except:
                            continue
                    
                    if created_at >= cutoff_date:
                        recent_programs.append(program)
            
            # Weekly breakdown
            weekly_data = self._calculate_weekly_breakdown(recent_programs)
            
            # Daily activity
            daily_data = self._calculate_daily_activity(recent_programs)
            
            return {
                'total_programs_this_month': len(recent_programs),
                'total_participants_this_month': sum(p.get('total_persons', 0) for p in recent_programs),
                'weekly_breakdown': weekly_data,
                'daily_activity': daily_data,
                'program_types_this_month': dict(Counter(p.get('program_type', 'Unknown') for p in recent_programs))
            }
        except Exception as e:
            print(f"Error in get_one_month_analytics: {e}")
            return {}
    
    def _calculate_weekly_breakdown(self, programs):
        """Calculate weekly breakdown of programs"""
        weeks = {f'Week {i+1}': 0 for i in range(4)}
        
        for program in programs:
            created_at = program.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    try:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    except:
                        continue
                
                days_ago = (datetime.utcnow() - created_at).days
                week_num = min(days_ago // 7, 3)  # 0-3 for 4 weeks
                weeks[f'Week {week_num + 1}'] += 1
        
        return weeks
    
    def _calculate_daily_activity(self, programs):
        """Calculate daily activity for last 7 days"""
        daily_counts = {}
        
        for i in range(7):
            date = datetime.utcnow() - timedelta(days=i)
            date_key = date.strftime('%Y-%m-%d')
            daily_counts[date_key] = 0
        
        for program in programs:
            created_at = program.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    try:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    except:
                        continue
                
                date_key = created_at.strftime('%Y-%m-%d')
                if date_key in daily_counts:
                    daily_counts[date_key] += 1
        
        return daily_counts
