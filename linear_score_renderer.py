import re
from mido import Message, MidiFile, MidiTrack

SOLFEGE_PITCH = [-1000, 0, 2, 4, 5, 7, 9, 11] # 唱名对应的半音
NOTATION_PITCH = {'.': 12, ',': -12, '#': 1, 'b': -1} # 音高相关记号
NOTATION_BEATS = {'-': 1, '~': 1.5, '=': 2, '+': 4, '*': 0.5, '^': 0.25, "'": 0.125} # 拍数相关记号

# 相对乐谱，格式: [音轨, 唱名, 开始拍数, 持续拍数]
def GetRel(score):
    solfa = []
    track = 0
    for c in score:
        if c == '(': track += 1
        if c == ')': track -= 1
        try: solfa.append([track, SOLFEGE_PITCH[int(c)], None, 0])
        except: pass
        try: solfa[-1][1] += NOTATION_PITCH[c]
        except KeyError: pass
        try: solfa[-1][3] += NOTATION_BEATS[c]
        except KeyError: pass
    for note in solfa:
        if note[3] == 0: note[3] = 0.5

    # 填补音符开始拍数
    n = len(solfa)
    pitch = [0]
    for i in range(n):
        gap = solfa[i][0] - solfa[i-1][0] if i != 0 else 0
        if gap > 0: pitch.append(pitch[-1])
        if gap < 0:
            for _ in range(-gap): pitch.pop()
        solfa[i][2] = pitch[-1]
        pitch[-1] += solfa[i][3]
    
    # 修正多轨音符的开始拍数
    for i in range(n):
        track = solfa[i][0]
        next_track_length = 0
        next_track_end = i
        for j in range(i+1, n):
            if solfa[j][0] <= track:
                next_track_end = j
                break
            if j == n-1: next_track_end = n
            if solfa[j][0] == track + 1: next_track_length += solfa[j][3]
        for j in range(i+1, next_track_end): solfa[j][2] -= next_track_length
    return solfa

# 绝对乐谱，格式: [音轨, 音高, 开始时间, 持续时间]
def GetAbs(rel, param):
    mspb = 60 / param['bpm'] * 1000
    return [[track, solfa + param['tonic'], int(st_beats * mspb), int(beats * mspb)]
             for track, solfa, st_beats, beats in rel]

# 分析参数行
def GetParam(paramline):
    param = {}
    try: # 调号
        key_sign = re.search('1=[CDEFGAB][#b.,]*', paramline).group()
        param['tonic'] = 60 + GetRel(str((ord(key_sign[2]) - ord('C')) % 7 + 1) + key_sign[3:])[0][1]
    except AttributeError: pass
    try: # bpm
        param['bpm'] = eval(re.search('(\d*)bpm', paramline).group(1))
    except AttributeError: pass
    return param

def ScoreToMidi(sc, filename):
    param = GetParam('1=C 120bpm')
    st_time = 0
    pitch = []
    lines = ''
    sc_split = sc.split('\n')
    is_param = [GetParam(line) != {} for line in sc_split] + [True]

    for i in range(len(sc_split)):
        if is_param[i]:
            new_param = GetParam(sc_split[i])
            for key, value in new_param.items():
                param[key] = value
        else:
            lines += sc_split[i]
            if is_param[i+1]:
                pit = GetAbs(GetRel(lines), param)
                pit = [[tr, pit, st + st_time, time] for tr, pit, st, time in pit]
                st_time = pit[-1][2] + pit[-1][3]
                pitch += pit
                lines = ''

    pitch = [[tr, pit, st, time] for tr, pit, st, time in pitch if 0 <= pit <= 127]
    n_track = max([track for track, _, _, _ in pitch]) + 1
    track_note = [[note for note in pitch if note[0] == i] for i in range(n_track)]

    mid = MidiFile()
    for tr in track_note:
        track = MidiTrack()
        mid.tracks.append(track)
        track.append(Message('program_change', channel=0, program=0, time=0))
        time = 0
        for note in tr:
            track.append(Message('note_on', note=note[1], velocity=64, time=note[2]-time, channel=0))
            track.append(Message('note_off', note=note[1], velocity=64, time=note[3], channel=0))
            time = note[2] + note[3]
    mid.save(filename)

def MidiToWav(filename, outname):
    import subprocess
    line = 'fluidsynth\\bin\\fluidsynth.exe -ni soundfont.sf2 %s -F %s -g 1' % (filename, outname)
    ex = subprocess.Popen(line, shell=True)
    ex.communicate()
    ex.wait()

if __name__ == '__main__':
    sc = '''1=D
5-345-34(1+(3+(5+)))
55,6,7,1234(7,+(2+(5+)))
3-123-3,4,(6,+(1+(3+)))
5,6,5,4,5,3,4,5,(5,+(7,+(3+)))
4,-6,5,4,-3,2,(4,+(6,+(1+)))
3,2,1,2,3,4,5,6,(3,+(5,+(1+)))
4,-6,5,6,-7,1(4,+(6,+(1+)))
5,6,7,12345(5,+(7,+(2+)))'''
    ScoreToMidi(sc, 'canon.mid')
    MidiToWav('canon.mid', 'canon.wav')
