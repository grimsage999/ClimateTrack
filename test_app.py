"""
Simple test script to verify the refactored architecture works
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all critical imports"""
    try:
        print("Testing core imports...")
        from core.funding_event import FundingEvent, FundingEventCollection
        print("✓ Core funding event imports successful")
        
        from core.extractor import FundingDataExtractor
        print("✓ Core extractor imports successful")
        
        from core.processor import VCDealProcessor
        print("✓ Core processor imports successful")
        
        print("\nTesting data imports...")
        from data.data_manager import DataManager
        from data.vc_sample_data import create_focused_vc_sample_data
        print("✓ Data management imports successful")
        
        print("\nTesting source imports...")
        from sources.source_registry import FundingSourceRegistry
        print("✓ Source registry imports successful")
        
        print("\nTesting basic functionality...")
        # Test data manager
        dm = DataManager()
        print(f"✓ DataManager initialized with methods: {[m for m in dir(dm) if not m.startswith('_')]}")
        
        # Test sample data
        sample_data = create_focused_vc_sample_data()
        print(f"✓ Sample data created: {len(sample_data)} events")
        
        # Test funding event
        if sample_data:
            event = FundingEvent.from_dict(sample_data[0])
            print(f"✓ FundingEvent created: {event.startup_name}")
        
        print("\n🎉 All tests passed! Architecture is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()