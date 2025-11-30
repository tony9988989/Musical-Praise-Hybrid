# test_melody.py
# 完整测试脚本，验证 zcs/melody 模块的所有功能

import sys
import os
import random

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置随机种子以便复现
random.seed(42)

# 首先需要初始化 DEAP creator（模拟 demo.py 的环境）
from deap import base, creator
from Settings import Melody

# 创建 DEAP 类型（与 demo.py 相同）
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Melody", Melody, fitness=creator.FitnessMax)

# 现在导入我们的模块
from melody import (
    Get_Melody, 
    melody_mutation,
    generate_random_melody,
    validate_melody,
    print_melody_info,
    mut_transpose,
    mut_inversion,
    mut_retrograde,
    mut_change_pitch,
    mut_change_rhythm,
    mut_split_note,
    mut_merge_notes,
    PITCH_MIN, PITCH_MAX,
    valid_notes
)

def test_get_melody():
    """测试初始种群生成"""
    print("\n" + "=" * 60)
    print("测试 1: Get_Melody() - 初始种群生成")
    print("=" * 60)
    
    # 生成多个旋律
    melodies = [Get_Melody() for _ in range(5)]
    
    all_valid = True
    for i, m in enumerate(melodies):
        valid, msg = validate_melody(m)
        status = "✓" if valid else "✗"
        print(f"  旋律 {i+1}: {len(m.pitch):2d} 个音符, 总时值 = {sum(m.beat)}, {status} {msg}")
        if not valid:
            all_valid = False
    
    print(f"\n  结果: {'全部通过 ✓' if all_valid else '存在错误 ✗'}")
    return all_valid


def test_mutation_transpose():
    """测试移调变异"""
    print("\n" + "=" * 60)
    print("测试 2: mut_transpose() - 移调变异")
    print("=" * 60)
    
    m = Get_Melody()
    original_pitch = m.pitch.copy()
    
    print(f"  原始音高: {[valid_notes[p] for p in original_pitch[:5]]}...")
    
    # 上移 3 个半音
    mut_transpose(m, semitones=3)
    print(f"  上移3半音: {[valid_notes[p] for p in m.pitch[:5]]}...")
    
    # 验证
    valid, msg = validate_melody(m)
    print(f"  验证: {msg}")
    return valid


def test_mutation_inversion():
    """测试倒影变异"""
    print("\n" + "=" * 60)
    print("测试 3: mut_inversion() - 倒影变异")
    print("=" * 60)
    
    m = Get_Melody()
    original_pitch = m.pitch.copy()
    axis = original_pitch[0]
    
    print(f"  原始音高: {[valid_notes[p] for p in original_pitch[:5]]}...")
    print(f"  轴心音: {valid_notes[axis]}")
    
    mut_inversion(m)
    print(f"  倒影后: {[valid_notes[p] for p in m.pitch[:5]]}...")
    
    # 验证倒影关系
    print(f"  验证倒影: 第2个音与轴心的关系")
    if len(original_pitch) > 1:
        orig_interval = original_pitch[1] - axis
        new_interval = m.pitch[1] - axis
        print(f"    原始: {orig_interval:+d} 半音, 倒影: {new_interval:+d} 半音")
    
    valid, msg = validate_melody(m)
    print(f"  验证: {msg}")
    return valid


def test_mutation_retrograde():
    """测试逆行变异"""
    print("\n" + "=" * 60)
    print("测试 4: mut_retrograde() - 逆行变异")
    print("=" * 60)
    
    m = Get_Melody()
    original_pitch = m.pitch.copy()
    original_beat = m.beat.copy()
    
    print(f"  原始音高: {[valid_notes[p] for p in original_pitch[:5]]}...")
    print(f"  原始时值: {original_beat[:5]}...")
    
    mut_retrograde(m)
    print(f"  逆行后音高: {[valid_notes[p] for p in m.pitch[:5]]}...")
    print(f"  逆行后时值: {m.beat[:5]}...")
    
    # 验证逆行
    is_reversed = (m.pitch == original_pitch[::-1] and m.beat == original_beat[::-1])
    print(f"  逆行验证: {'正确 ✓' if is_reversed else '错误 ✗'}")
    
    valid, msg = validate_melody(m)
    print(f"  旋律验证: {msg}")
    return valid and is_reversed


def test_mutation_split_merge():
    """测试音符分裂和合并"""
    print("\n" + "=" * 60)
    print("测试 5: mut_split_note() & mut_merge_notes()")
    print("=" * 60)
    
    m = Get_Melody()
    original_count = len(m.pitch)
    original_total_beat = sum(m.beat)
    
    print(f"  原始: {original_count} 个音符, 总时值 = {original_total_beat}")
    
    # 分裂
    mut_split_note(m)
    after_split = len(m.pitch)
    print(f"  分裂后: {after_split} 个音符, 总时值 = {sum(m.beat)}")
    
    # 合并
    mut_merge_notes(m)
    after_merge = len(m.pitch)
    print(f"  合并后: {after_merge} 个音符, 总时值 = {sum(m.beat)}")
    
    valid, msg = validate_melody(m)
    print(f"  验证: {msg}")
    
    # 总时值应该不变
    time_preserved = (sum(m.beat) == original_total_beat)
    print(f"  时值守恒: {'正确 ✓' if time_preserved else '错误 ✗'}")
    
    return valid and time_preserved


def test_melody_mutation():
    """测试主变异函数"""
    print("\n" + "=" * 60)
    print("测试 6: melody_mutation() - 主变异函数")
    print("=" * 60)
    
    all_valid = True
    
    for i in range(10):
        m = Get_Melody()
        result = melody_mutation(m)
        
        # 检查返回格式
        if not isinstance(result, tuple) or len(result) != 1:
            print(f"  第 {i+1} 次: 返回格式错误 ✗")
            all_valid = False
            continue
        
        mutated = result[0]
        valid, msg = validate_melody(mutated)
        if not valid:
            print(f"  第 {i+1} 次: {msg} ✗")
            all_valid = False
    
    print(f"  10 次随机变异: {'全部通过 ✓' if all_valid else '存在错误 ✗'}")
    return all_valid


def run_all_tests():
    """运行所有测试"""
    print("\n" + "#" * 60)
    print("#" + " " * 20 + "ZCS Melody 完整测试" + " " * 19 + "#")
    print("#" * 60)
    
    results = []
    
    results.append(("Get_Melody", test_get_melody()))
    results.append(("mut_transpose", test_mutation_transpose()))
    results.append(("mut_inversion", test_mutation_inversion()))
    results.append(("mut_retrograde", test_mutation_retrograde()))
    results.append(("Split & Merge", test_mutation_split_merge()))
    results.append(("melody_mutation", test_melody_mutation()))
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {name:25s}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 所有测试通过！模块可以安全使用。")
    else:
        print("⚠️ 部分测试失败，请检查代码。")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
