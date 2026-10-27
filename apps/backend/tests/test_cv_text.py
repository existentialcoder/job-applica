import io

from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from src.services.cv_text import column_split, cv_text


def _line(y: float, x0: float, words: int, width: float = 40) -> list[dict]:
    return [{'x0': x0 + i * (width + 5), 'x1': x0 + i * (width + 5) + width, 'top': y} for i in range(words)]


def test_two_columns_split_in_the_gutter():
    # A narrow sidebar (words end at x 105) next to a main column (from x 200), like a contact-sidebar CV.
    words = [w for y in range(30) for w in _line(y * 20, 20, 2) + _line(y * 20, 200, 8)]
    split = column_split(words, 595)
    assert split is not None and 105 <= split <= 200


def test_single_column_is_left_alone():
    # Full-width lines whose word boundaries shift from line to line, as in real prose.
    words = [w for y in range(40) for w in _line(y * 20, 20 + (y * 7) % 30, 12)]
    assert column_split(words, 595) is None


def test_too_little_text_is_left_alone():
    assert column_split(_line(0, 20, 5), 595) is None


def test_docx_link_labels_keep_their_urls():
    doc = Document()
    paragraph = doc.add_paragraph()
    rel_id = doc.part.relate_to('https://github.com/someone', RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    link = OxmlElement('w:hyperlink')
    link.set(qn('r:id'), rel_id)
    run = OxmlElement('w:r')
    text = OxmlElement('w:t')
    text.text = 'GitHub'
    run.append(text)
    link.append(run)
    paragraph._p.append(link)
    buffer = io.BytesIO()
    doc.save(buffer)

    assert 'https://github.com/someone' in cv_text(None, buffer.getvalue())
