import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def migrate_data():
    print("🚀 Starting data migration to MongoDB Atlas...")
    
    # Connect to local MongoDB
    try:
        local_client = MongoClient('mongodb://localhost:27017/')
        local_db = local_client['disha_db']
        print("✅ Connected to local MongoDB")
    except Exception as e:
        print(f"❌ Failed to connect to local MongoDB: {e}")
        return

    # Connect to MongoDB Atlas
    try:
        atlas_uri = os.getenv('MONGODB_URI')
        atlas_client = MongoClient(atlas_uri)
        atlas_db = atlas_client['disha_db']
        print("✅ Connected to MongoDB Atlas")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB Atlas: {e}")
        return

    # Collections to migrate
    collections = ['users', 'tolis', 'programs', 'resources', 'messages', 'newsletters', 'reports']
    
    migrated_count = 0
    
    for collection_name in collections:
        try:
            print(f"\n📦 Migrating {collection_name}...")
            
            # Get data from local
            local_data = list(local_db[collection_name].find())
            
            if local_data:
                # Clear existing data in Atlas (optional - remove if you want to keep existing data)
                atlas_db[collection_name].delete_many({})
                
                # Insert data to Atlas
                result = atlas_db[collection_name].insert_many(local_data)
                print(f"✅ Migrated {len(result.inserted_ids)} documents from {collection_name}")
                migrated_count += len(result.inserted_ids)
            else:
                print(f"ℹ️ No data found in {collection_name}")
                
        except Exception as e:
            print(f"❌ Error migrating {collection_name}: {e}")
    
    print(f"\n🎉 Migration completed! Total documents migrated: {migrated_count}")
    
    # Verify migration
    print("\n🔍 Verifying migration...")
    for collection_name in collections:
        local_count = local_db[collection_name].count_documents({})
        atlas_count = atlas_db[collection_name].count_documents({})
        print(f"   {collection_name}: Local={local_count}, Atlas={atlas_count}")
    
    # Close connections
    local_client.close()
    atlas_client.close()
    print("\n✅ Migration verification complete!")

if __name__ == "__main__":
    migrate_data()