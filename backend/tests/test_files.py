from app.shared.files import safe_name


def test_safe_name_removes_paths_and_unsafe_characters():
    assert safe_name("../../mi noticia (final).png") == "mi_noticia_final_.png"
    assert "/" not in safe_name("carpeta/archivo.pdf")
