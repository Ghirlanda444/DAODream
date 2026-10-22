"""Mabari coats: the colours BP_Mabari gives each dog through custom primitive data (M_Mabari, see
mabari_build.body.py): name -> (coat colour, brindle 0-1, no kaddis 0/1). The hero's dog is fawn; the
war dogs of Howe's men take one of the others, picked from their tag so the same dog always looks the same."""
COATS = {
    "fawn": ((0.42, 0.27, 0.14), 0.0, 0.0),        # the hero's mabari: light brown
    "black": ((0.0, 0.0, 0.0), 0.0, 0.0),          # the wolf's dark coat, darkened (all zero)
    "brindle": ((0.16, 0.10, 0.055), 1.0, 0.0),
    "red": ((0.30, 0.12, 0.055), 0.2, 0.0),
    "grey": ((0.15, 0.155, 0.16), 0.3, 0.0),
    "tan": ((0.34, 0.24, 0.14), 0.5, 0.0),
    "black_unpainted": ((0.0, 0.0, 0.0), 0.0, 1.0),
}
ENEMY = ["black", "brindle", "red", "grey", "tan", "black_unpainted"]
