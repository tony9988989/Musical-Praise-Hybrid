# zcs 模块包
# 作者：zcs
# 功能：实现 GetMelody（初始种群生成）和 Mutations（变异操作）

from .melody import (
    # 主要函数
    Get_Melody,
    melody_mutation,
    
    # 单独的变异函数
    mut_transpose,
    mut_inversion,
    mut_retrograde,
    mut_change_pitch,
    mut_change_rhythm,
    mut_split_note,
    mut_merge_notes,
    
    # 辅助函数
    generate_random_melody,
    validate_melody,
    print_melody_info,
    
    # 常量
    PITCH_MIN,
    PITCH_MAX,
    BEAT_UNIT,
    VALID_BEATS,
    mutation_strategies,
)

__all__ = [
    'Get_Melody',
    'melody_mutation',
    'mut_transpose',
    'mut_inversion',
    'mut_retrograde',
    'mut_change_pitch',
    'mut_change_rhythm',
    'mut_split_note',
    'mut_merge_notes',
    'generate_random_melody',
    'validate_melody',
    'print_melody_info',
    'PITCH_MIN',
    'PITCH_MAX',
    'BEAT_UNIT',
    'VALID_BEATS',
    'mutation_strategies',
]
