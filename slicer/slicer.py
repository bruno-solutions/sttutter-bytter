"""Slicer homonymous submodule."""

import pydub



class Slicer:
    """The primary object of the slicer module."""
    def __init__(self, base_seg, count):
        self.base_seg = base_seg
        self.count = count

        self.data = None
        self.convert_data()

        self.intervals = []
        self.clips = []

    @classmethod
    def invoke_slicers(cls, slicer_methods):
        """
        A method invoker that wraps and registers a
        custom slicer method in pydub's effects list.
        """

        if isinstance(slicer_methods, dict):
            for named_method in slicer_methods.items():
                cls.invoke_slicers(named_method)

        elif isinstance(slicer_methods, tuple):
            name, method = slicer_methods

            print(f"registering: name: {name}, method: {method}")

            @pydub.utils.register_pydub_effect(name)
            def slicer_method_wrap(seg, count, *args, **kwargs):
                return getattr(cls(seg, count), method)(*args, **kwargs).\
                    execute_slicing().clips

        else: raise TypeError

    def convert_data(self):
        """Data loader and converter pending implementation."""

    def execute_slicing(self):
        """Execute slicing"""
        for interval in self.intervals:
            self.clips.append(
                self.base_seg[interval[0]:interval[1]]
            )

        return self

    def random_slice(self):
        """Create slices at random."""
        # access self.data

        # NOT EVEN RANDOM PLACEHOLDER
        self.intervals += [
            (5000, 15000),
            (10000, 20000),
            (30000, 40000),
            (20000, 21000)
        ]

        return self
