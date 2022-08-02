import random

random.seed()


def source(index=None):
    example_sources = [
        "https://youtu.be/Dc1-W4KsHvE",
        "https://youtu.be/oJL-lCzEXgI",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://youtu.be/sZdbNMDH8hc",
        "https://youtu.be/YBSs3-RfLKk",
        "https://youtu.be/pOF_oo3EgnQ",
        "https://youtu.be/q3f9ZiH6Euw",
        "https://youtu.be/QDYRQX6FPQQ",
        "https://youtu.be/PARA6_ErZI0",
        "https://youtu.be/hOZgb0T7AM4",
        "file:///C:/Users/Public/Desktop/bytter/source/Zombo com/Zombo.com.wav",
        "https://youtu.be/oa6crdQIAcI"  # Jordan Peterson
    ]

    return example_sources[random.randrange(len(example_sources))] if index is None else example_sources[index % len(example_sources)]
