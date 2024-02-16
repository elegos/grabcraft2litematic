from dataclasses import dataclass


@dataclass(frozen=True)
class Coordinates:
    y: int
    x: int
    z: int

    def __str__(self) -> str:
        return f'Coordinates{{x = {self.x}, y = {self.y}, z = {self.z}}}'


@dataclass
class GenericDefinition:
    title: str
    author: str
    blocks: dict[Coordinates, dict]

def get_max_size(coords: list[Coordinates]) -> Coordinates:
    x = 0
    y = 0
    z = 0

    for coord in coords:
        x = max(x, coord.x)
        y = max(y, coord.y)
        z = max(z, coord.z)

    return Coordinates(x=x, y=y, z=z)