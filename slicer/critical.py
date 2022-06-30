class CriticalTimeIndexes:
    """Saves, mixes, and convert critical time indexes into intervals."""
    def __init__(self):
        self.host = None
        # self.cti = {}
        # self.interval = {}
        self.cti = []
        self.interval = []

    @staticmethod
    def abs_derivative(data):
        """Get the absolute value of the rate of change of each point."""
        raise SyntaxError("Not implemented.")

    def append(self, item):
        """Appends a critical time to the list of CTIs."""
        self.cti.append(item)

    def intervals(self):
        """Generate critical intervals from the critical time indexes."""
        for i in range(0, len(self.cti)):
            self.interval.append([self.cti[i][0], self.cti[i][1]])

    def get_start_point(self, x, arr):
        """
        A binary search to find the nearby point of the target x in array arr
        input:
            x: target number
            arr: target array
        output:
            [low, mid, high]
            if any of these points is not exist in the range of 0-1, -1 will be returned.
            Otherwise an index will be returned.
        """
        if len(arr) == 0:
            return -1

        low = 0
        mid = 0
        high = len(arr) - 1
        is_found = False

        while low <= high:

            mid = (high + low) // 2

            if arr[mid] < x:
                low = mid + 1

            elif arr[mid] > x:
                high = mid - 1

            else:
                is_found = True
                break

        high += 1

        if is_found:  # x is exist on the arr
            if x == arr[low] or x - arr[low] > 0.1:
                low = -1
            if x == arr[high] or arr[high] - x > 0.1:
                high = -1
        else:  # x is not exist on the arr
            if low != 0 and x - arr[low - 1] > 0.1:
                low = -1
            if high == len(arr) or arr[high + 1] - x > 0.1:
                high = -1
            mid = -1

        return low, mid, high