import re

from mido import Message, MidiFile, MidiTrack

from assets.absolute_note import AbsoluteNote
from assets.score_parameters import ScoreParameters
from assets.note_line import NoteLine

class LinearScore():
    def __init__(self, score: str) -> None:
        self.score = score
        self.track_notes: list[AbsoluteNote] = []
        self.midi_file: MidiFile = MidiFile()
        self._analyze_score()
        self._get_midi()

    def _analyze_score(self) -> None:
        param = ScoreParameters()
        st_time = 0
        pitch: list[AbsoluteNote] = []
        lines = ''
        sc_split = self.score.split('\n')
        param_by_line = [LinearScore.analyze_param(line) for line in sc_split] + [ScoreParameters(True)]
        # 逐行解析
        for i in range(len(sc_split)):
            if param_by_line[i].is_changed:
                param = param_by_line[i]
            else:
                lines += sc_split[i]
                if param_by_line[i + 1].is_changed:
                    pit = NoteLine(lines, param).absolute_notes
                    for note in pit:
                        note.start_time += st_time
                    st_time = pit[-1].start_time + pit[-1].duration
                    pitch += pit
                    lines = ''
        pitch = [note for note in pitch if 0 <= note.pitch <= 127]
        n_track = max([note.track_no for note in pitch]) + 1
        self.track_notes = [[note for note in pitch if note.track_no == i] for i in range(n_track)]

    def _get_midi(self) -> None:
        for tr in self.track_notes:
            track = MidiTrack()
            self.midi_file.tracks.append(track)
            track.append(Message('program_change', channel=0, program=0, time=0))
            time = 0
            for note in tr:
                track.append(Message('note_on', note=note.pitch, velocity=64, time=note.start_time-time, channel=0))
                track.append(Message('note_off', note=note.pitch, velocity=64, time=note.duration, channel=0))
                time = note.start_time + note.duration

    # 分析参数行
    @staticmethod
    def analyze_param(paramline, origin_param: ScoreParameters = ScoreParameters()):
        origin_param.is_changed = False
        mat = re.search('1=[CDEFGAB][#b.,]*', paramline) # 调号
        if mat is not None:
            key_sign = mat.group()
            solfa_to_c = (ord(key_sign[2]) - ord('C')) % 7 + 1
            tmp_score = NoteLine(str(solfa_to_c) + key_sign[3:])
            origin_param.tonic = tmp_score.absolute_notes[0].pitch
            origin_param.is_changed = True
        mat = re.search('(\d*)bpm', paramline) # bpm
        if mat is not None: 
            origin_param.bpm = int(mat.group(1))
            origin_param.is_changed = True
        return ScoreParameters(origin_param.is_changed, origin_param.tonic, origin_param.bpm)
