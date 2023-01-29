from assets.linear_score import LinearScore

def midi_to_wav(filename, outname):
    import subprocess
    line = 'fluidsynth\\bin\\fluidsynth.exe -ni soundfont.sf2 %s -F %s -g 1' % (filename, outname)
    ex = subprocess.Popen(line, shell=True)
    ex.communicate()
    ex.wait()

if __name__ == '__main__':
    with open('template/orchid_pavilion.txt') as f:
        sc = f.read()
    linsc = LinearScore(sc)

    print('=== Score ===')
    for tr in linsc.track_notes:
        print(f'--- Track {tr[0].track_no} ---')
        for note in tr:
            print(f'pitch={note.pitch}, st={note.start_time}, dura={note.duration}')
    print('=== End ===')

    LinearScore(sc).midi_file.save('output.mid')
    midi_to_wav('output.mid', 'output.wav')
