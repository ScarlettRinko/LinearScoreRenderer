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
        curr_track_no: int = 0
        multitrack_stack = []
        # 逐字扫描线性乐谱
        for i in range(len(self.score)):
            c = self.score[i]
            if c == '(':
                curr_track_no += 1
                if i == 0 or self.score[i-1] != ')':
                    multitrack_stack.append(1)
                else:
                    multitrack_stack[-1] += 1
            elif c == ')':
                try:
                    c_next = self.score[i + 1]
                except IndexError:
                    c_next = ''
                if c_next != '(':
                    curr_track_no -= multitrack_stack.pop()
            elif c in '01234567':
                self.relative_notes.append(RelativeNote(curr_track_no, SOLFEGE_PITCH[int(c)], None, 0))
            elif c in '.,#b':
                self.relative_notes[-1].solfa += NOTATION_PITCH[c]
            elif c in "-~=+*^'":
                self.relative_notes[-1].note_value += NOTATION_BEATS[c]
            else:
                pass
        for note in self.relative_notes:
            if note.note_value == 0:
                note.note_value = 0.5
        # 填补音符开始拍数
        n = len(self.relative_notes)
        pitch = [0]
        for i in range(n):
            gap = self.relative_notes[i].track_no - self.relative_notes[i-1].track_no if i != 0 else 0
            if gap > 0:
                pitch.append(pitch[-1])
            if gap < 0:
                for _ in range(-gap):
                    pitch.pop()
            self.relative_notes[i].start_beat = pitch[-1]
            pitch[-1] += self.relative_notes[i].note_value
        # 修正多轨音符的开始拍数
        for i in range(n):
            curr_track_no = self.relative_notes[i].track_no
            next_track_length = 0
            next_track_end = i
            for j in range(i+1, n):
                if self.relative_notes[j].track_no <= curr_track_no:
                    next_track_end = j
                    break
                if j == n - 1:
                    next_track_end = n
                if self.relative_notes[j].track_no == curr_track_no + 1:
                    next_track_length += self.relative_notes[j].note_value
            for j in range(i+1, next_track_end):
                self.relative_notes[j].start_beat -= next_track_length

    def _get_absolute_notes(self) -> None:
        ms_per_beat = 60 / self.param.bpm * 1000
        for note in self.relative_notes:
            self.absolute_notes.append(AbsoluteNote(
                note.track_no,
                note.solfa + self.param.tonic,
                int(note.start_beat * ms_per_beat),
                int(note.note_value * ms_per_beat)
            ))
