import re
from math import ceil
from typing import Optional

from assets.chord_typing import ChordFamily, ChordInterval, ChordType
from assets.constants import (CHORD_FAMILIES, CHORD_FAMILY_NOTES,
                              CHORD_INDEX_TO_PITCH, CHORD_INTERVAL_TO_INDEX,
                              CHORD_TYPES, RE_PATTERN_CHORD_SUFFIX,
                              SOLFEGE_PITCH)
from assets.relative_note import RelativeNote


class Chord:
    """基于三度音堆叠的和弦类。
    其本质是在维护一个长度为 7 的列表 [根音, 三音, 五音, 七音, 九音, 十一音, 十三音, 十五音]，每个元素位置上的数值代表它们的升降半音情况。"""
    def __init__(
        self,
        family: ChordFamily = 'M',
        type: ChordType = 3
    ) -> None:
        self.notes: dict[int, int] = CHORD_FAMILY_NOTES[family].copy()
        if type == 3:
            self.notes[3] = None
        if type in [9, 11, 13]:
            self.add(9)
        if type in [11, 13]:
            self.add(11)
        if type == 13:
            self.add(13)

    def add(self, interval: ChordInterval) -> None:
        """添加某一纯（大）音程的音"""
        self.notes[CHORD_INTERVAL_TO_INDEX[interval]] = 0

    def sharp(self, interval: ChordInterval) -> None:
        """（添加并）将某一音程的音升半音"""
        self.notes[CHORD_INTERVAL_TO_INDEX[interval]] = 1

    def flat(self, interval: ChordInterval) -> None:
        """（添加并）将某一音程的音降半音"""
        self.notes[CHORD_INTERVAL_TO_INDEX[interval]] = -1
    
    def omit(self, interval: ChordInterval) -> None:
        """删除某一个音程的音"""
        self.notes[CHORD_INTERVAL_TO_INDEX[interval]] = None
    
    def sus(self, second: bool = False) -> None:
        """将三音替换为纯四度音（second 为 False）或大二度音（second 为 True）"""
        self.notes[1] = -2 if second else 1

    def get_notes(self, root_note: int = 0, on: int = None) -> list[int]:
        """指定一个根音音高和低音音高，然后返回和弦所有音的音高"""
        ret: list[int] = []
        for i, k in enumerate(self.notes):
            if k is not None:
                ret.append(root_note + CHORD_INDEX_TO_PITCH[i] + k)
        if on == None:
            on = root_note
        if on not in ret:
            ret.append(on)
        highest: int = max(ret)
        for i, k in enumerate(ret):
            if k < on:
                ret[i] += ceil((highest - k) / 12) * 12
        return ret

    @staticmethod
    def from_score(score: str, start_beat: int, note_value: int) -> list[RelativeNote]:
        """将和弦名称转换为 RelativeNote。每一个音符的音轨编号从 0 开始按顺序编码。"""
        def degree_to_solfa(degree: str) -> int:
            solfa = SOLFEGE_PITCH[int(degree[0])]
            if len(degree) > 1:
                if degree[1] == '#':
                    solfa += 1
                elif degree[1] == 'b':
                    solfa -= 1
            return solfa
        family, type_ = '', 3
        # 分离八度
        octave_delta = -1 # 默认和弦比旋律低八度
        while score[-1] in ',.':
            if score[-1] == '.':
                octave_delta += 1
            elif score[-1] == ',':
                octave_delta -= 1
            score = score[:-1]
        # 分离转位
        on: Optional[int] = None
        if '/' in score:
            score, on_str = score.split('/', 2)
            on = degree_to_solfa(on_str)
        # 分离根音
        root_str, score = score[0], score[1:]
        if score != '' and score[0] in '#b':
            root_str, score = root_str + score[0], score[1:]
        root: int = degree_to_solfa(root_str)
        # 分离和弦家族
        for f in CHORD_FAMILIES:
            if score.startswith(f):
                family, score = f, score[len(f):]
                break
        # 分离和弦类型
        for k, v in CHORD_TYPES.items():
            if score.startswith(k):
                type_, score = v, score[len(k):]
                break
        # 处理后缀
        suffixes: list[str] = re.findall(RE_PATTERN_CHORD_SUFFIX, score)
        chord = Chord(family, type_)
        for s in suffixes:
            if s.startswith('add'):
                chord.add(int(s[3:]))
            elif s.startswith('omit'):
                chord.omit(int(s[4:]))
            elif s == 'sus':
                chord.sus()
            elif s == 'sus2':
                chord.sus(second=True)
            elif s.startswith('#'):
                chord.sharp(int(s[1:]))
            elif s.startswith('b'):
                chord.flat(int(s[1:]))
            else:
                pass
        ret: list[RelativeNote] = []
        for i, solfa in enumerate(chord.get_notes(root, on)):
            ret.append(RelativeNote(i, solfa + octave_delta * 12, start_beat, note_value))
        return ret
