# test_subgraphs.py
"""
测试子图集成
"""
from __future__ import annotations
from coach.schemas import CoachState
from coach.graph import build_graph

def test_graph_build():
    """
    测试图构建是否成功
    """
    print("Testing graph build...")
    try:
        graph = build_graph()
        print("✅ Graph build successful!")
        return True
    except Exception as e:
        print(f"❌ Graph build failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_initial_state():
    """
    测试初始状态
    """
    print("Testing initial state...")
    try:
        # 从schemas导入Problem类
        from coach.schemas import Problem
        
        # 创建初始状态
        initial_state = CoachState(
            problem=Problem(
                statement="Test problem",
                raw_text="""# Test Problem
                Given a number, return its square.
                
                Input:
                5
                Output:
                25
                
                Input:
                10
                Output:
                100
                """
            )
        )
        print("✅ Initial state created successfully!")
        print(f"Initial phase: {initial_state.phase}")
        return True
    except Exception as e:
        print(f"❌ Initial state creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    运行所有测试
    """
    print("Running subgraph integration tests...\n")
    
    test1 = test_graph_build()
    print()
    test2 = test_initial_state()
    
    print("\nTest Results:")
    print(f"Graph build: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Initial state: {'✅ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print("\n🎉 All tests passed! The subgraph integration is successful.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()