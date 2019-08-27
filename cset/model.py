from dataclasses import dataclass
from typing import Optional


@dataclass
class Paper:
    title: str
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    _text: Optional[str] = None
    text_attr = ('title', 'abstract', 'keywords')

    @property
    def text(self):
        if self._text is not None:
            return self._text
        attr_text = [getattr(self, attr)for attr in self.text_attr]
        self._text = '. '.join((s for s in attr_text if s is not None))
        return self._text

