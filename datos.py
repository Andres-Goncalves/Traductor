from dataclasses import dataclass, field

@dataclass(kw_only=True)
class Palabra:
    x0: int
    y0: int
    x1: int
    y1: int
    tamaño_letras: int = 0
    confianza: float
    Palabra_original: str = ""

@dataclass(kw_only=True)
class Linea:
    x0: int
    y0: int
    x1: int
    y1: int
    parrafo_original: int
    identificador_de_division: int
    tamaño_letras: int = 0
    linea_original: str = ""
    linea_traducida: str = ""
    palabras_linea_original: list[Palabra] = field(default_factory=list)

@dataclass(kw_only=True)
class Parrafo:
    x0: int
    y0: int
    x1: int
    y1: int
    tamaño_letras: int = 0
    parrafo_original: list[str] = field(default_factory=list)
    lineas_parrafo_original: list[Linea] = field(default_factory=list)
    parrafo_traducido: list[str] = field(default_factory=list)
    sub_parrafos: list[list[Linea]] = field(default_factory=list)