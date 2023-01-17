class AbsoluteNote():
    def __init__(
        self,
        track_no: int = 0,
        pitch: int = 0,
        start_time: int = 0,
        duration: int = 0,
    ) -> None:
        """初始化 AbsoluteNote 绝对音符.

        Args:
            track_no (int, optional): 音轨编号. Defaults to 0.
            pitch (int, optional): 音高，midi 格式，中央 C 为 60. Defaults to 0.
            start_time (int, optional): 开始时刻，以毫秒为单位. Defaults to 0.
            duration (int, optional): 持续时长，以毫秒为单位. Defaults to 0.
        """
        self.track_no = track_no
        self.pitch = pitch
        self.start_time = start_time
        self.duration = duration
