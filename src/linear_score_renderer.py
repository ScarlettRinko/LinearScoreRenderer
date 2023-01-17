from assets.linear_score import LinearScore

def midi_to_wav(filename, outname):
    import subprocess
    line = 'fluidsynth\\bin\\fluidsynth.exe -ni soundfont.sf2 %s -F %s -g 1' % (filename, outname)
    ex = subprocess.Popen(line, shell=True)
    ex.communicate()
    ex.wait()

if __name__ == '__main__':
    with open('src/assets/template/flower_dance.txt') as f:
        sc = f.read()
    LinearScore(sc).midi_file.save('output.mid')
    midi_to_wav('output.mid', 'output.wav')
