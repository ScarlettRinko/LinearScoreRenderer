from assets.absolute_note import AbsoluteNote
from assets.constants import NOTATION_BEATS, NOTATION_PITCH, SOLFEGE_PITCH
from assets.relative_note import RelativeNote
from assets.score_parameters import ScoreParameters


class NoteLine():
    """音符行"""
    def __init__(self, score: str, param: ScoreParameters = ScoreParameters()) -> None:
        self.score = score
        self.param = param
        self.relative_notes: list[RelativeNote] = []
        self.absolute_notes: list[AbsoluteNote] = []
        self._get_relative_notes()
        self._get_absolute_notes()

    def _get_relative_notes(self) -> None:
        """返回编码后的音符列表"""
        last_note_beat: list[int] = [0] # 每个音轨最后一个音的结束拍数
        self.relative_notes: list[RelativeNote] = []
        note_ended = False
        brackets_layer = 0
        brackets_score = ''
        # 逐字扫描线性乐谱
        for c in self.score:
            def end_note():
                """终止当前音符，音符时值为零则置为 0.5。"""
                nonlocal last_note_beat, note_ended
                if note_ended:
                    return
                note_ended = True
                if len(self.relative_notes) > 0:
                    if self.relative_notes[-1].note_value == 0:
                        self.relative_notes[-1].note_value = 0.5
                    last_note_beat[0] += self.relative_notes[-1].note_value
            # 多轨括号
            if c == '(':
                end_note()
                brackets_layer += 1
            elif c == ')':
                brackets_layer -= 1
                if brackets_layer == 0:
                    # 递归处理括号
                    bracket_notes = NoteLine(brackets_score[1:]).relative_notes
                    bracket_total_value = bracket_notes[-1].start_beat + bracket_notes[-1].note_value
                    bracket_tracks = {}.fromkeys([note.track_no for note in bracket_notes])
                    n_bracket_tracks = len(bracket_tracks)
                    # 列举可用的音轨
                    available_track_no = []
                    for i in range(len(last_note_beat)):
                        if last_note_beat[i] <= last_note_beat[0] - bracket_total_value:
                            available_track_no.append(i)
                    # 判断是否需要新建音轨
                    if (n_track_to_append := n_bracket_tracks - len(available_track_no)) > 0:
                        n_track = len(last_note_beat)
                        available_track_no.extend(list(range(n_track, n_track + n_track_to_append)))
                        last_note_beat.extend([0] * n_track_to_append)
                    available_track_no = available_track_no[:n_bracket_tracks]
                    for i in available_track_no:
                        last_note_beat[i] = last_note_beat[0]
                    # 创建递归内音轨编号与递归外音轨编号的映射
                    for i, k in enumerate(bracket_tracks.keys()):
                        bracket_tracks[k] = available_track_no[i]
                    # 将递归内音符添加至递归外音符列表
                    for note in bracket_notes:
                        note.track_no = bracket_tracks[note.track_no]
                        note.start_beat = last_note_beat[0] - bracket_total_value + note.start_beat
                        self.relative_notes.append(note)
                    brackets_score = ''
            if brackets_layer > 0:
                brackets_score += c
                continue
            # 记录音高和时值
            if c in '01234567':
                end_note()
                self.relative_notes.append(RelativeNote(0, SOLFEGE_PITCH[int(c)], last_note_beat[0], 0))
                note_ended = False
            elif c in '.,#b':
                self.relative_notes[-1].solfa += NOTATION_PITCH[c]
            elif c in "-~=+*^'":
                self.relative_notes[-1].note_value += NOTATION_BEATS[c]
            # 小节线
            elif c in '/':
                pass
            # 忽略其它字符
            else:
                ...
        end_note()

    def _get_absolute_notes(self) -> None:
        ms_per_beat = 60 / self.param.bpm * 1000
        for note in self.relative_notes:
            self.absolute_notes.append(AbsoluteNote(
                note.track_no,
                note.solfa + self.param.tonic,
                int(note.start_beat * ms_per_beat),
                int(note.note_value * ms_per_beat)
            ))
