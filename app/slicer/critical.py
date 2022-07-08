class CriticalTimeIndexes:
    """
    Instantiated to store and convert critical time indexes into intervals
    """

    def __init__(self):
        self.cti = []
        self.interval = []

    def append(self, cti):
        """
        Appends a critical time to the list
        """
        self.cti.append(cti)

    def intervals(self):
        """
        Build critical intervals from the critical time indexes
        """
        for cti in self.cti:
            self.interval.append([cti[0], cti[1]])
