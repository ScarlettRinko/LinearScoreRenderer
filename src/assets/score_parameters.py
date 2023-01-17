class ScoreParameters():
    def __init__(
        self,
        is_changed: bool = False,
        tonic: int = 60,
        bpm: int = 120
    ) -> None:
        """初始化 ScoreParameters 乐谱参数.

        Args:
            is_changed (bool, optional): 是否有更改. Defaults to False.
            tonic (int, optional): 主音音高，midi 格式，中央 C 为 60. Defaults to 60.
            bpm (int, optional): 每分钟拍数. Defaults to 120.
        """
        self.is_changed = is_changed
        self.tonic = tonic
        self.bpm = bpm
