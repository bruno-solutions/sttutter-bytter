import random

example_urls = [
    'https://youtu.be/Dc1-W4KsHvE',
    'https://youtu.be/oJL-lCzEXgI',
    'https://youtu.be/dQw4w9WgXcQ',
    'https://youtu.be/sZdbNMDH8hc',
    'https://youtu.be/YBSs3-RfLKk',
    'https://youtu.be/pOF_oo3EgnQ',
    'https://youtu.be/q3f9ZiH6Euw',
    'https://youtu.be/QDYRQX6FPQQ',
    'https://youtu.be/PARA6_ErZI0',
    'https://youtu.be/hOZgb0T7AM4'
]

random.seed()


def url(index=None):
    return example_urls[random.randrange(len(example_urls))] if index is None else example_urls[index % len(example_urls)]
