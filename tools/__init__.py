import pickle
import base64


from math import ceil

from tools.emoji import Emoji


def create_progress_text(
    divisible: int,
    divider: int,
    *,
    progress_element: str = Emoji.GREEN_BIG_SQUARE,
    remaining_element: str = Emoji.GREY_BIG_SQUARE,
    length_widget: int = 10,
    show_digits: bool = True,
):
    if divisible > divider:
        percent = 100
        progress = progress_element * length_widget
    else:
        float_fraction = divisible / divider * length_widget
        percent = ceil(float_fraction * 10)
        fraction = ceil(float_fraction)
        grey_progress = (length_widget - fraction) * remaining_element
        green_progress = fraction * progress_element
        progress = green_progress + grey_progress

    if show_digits:
        return f"{progress} {percent}%"
    return progress


class SerializableMixin:
    async def serialize(self):
        return base64.b64encode(pickle.dumps(self)).decode()


async def deserialize(sequence: str):
    return pickle.loads(base64.b64decode(sequence.encode()))
