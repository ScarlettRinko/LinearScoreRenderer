class RelativeNote():
    def __init__(
        self,
        track_no: int = 0,
        solfa: int = 0,
        start_beat: int = 0,
        note_value: int = 0,
    ) -> None:
        """初始化 RelativeNote 相对音符.

        Args:
            track_no (int, optional): 音轨编号. Defaults to 0.
            solfa (int, optional): 唱名，与主音相差的半音数. Defaults to 0.
            start_beat (int, optional): 开始时刻的拍数. Defaults to 0.
            note_value (int, optional): 持续拍数. Defaults to 0.
        """
        self.track_no = track_no
        self.solfa = solfa
        self.start_beat = start_beat
        self.note_value = note_value
