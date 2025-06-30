import json
from datetime import datetime

class Guid:
    """Represents the 'guid' part of the JSON data."""
    def __init__(self, rendered):
        self.rendered = rendered

    @classmethod
    def from_dict(cls, data):
        """Creates a Guid object from a dictionary."""
        return cls(rendered=data.get('rendered'))

class RenderedData:
    """Represents any object with a 'rendered' key."""
    def __init__(self, rendered):
        self.rendered = rendered

    @classmethod
    def from_dict(cls, data):
        """Creates a RenderedData object from a dictionary."""
        return cls(rendered=data.get('rendered'))

class Content(RenderedData):
    """Represents the 'content' part of the JSON data."""
    def __init__(self, rendered, protected):
        super().__init__(rendered)
        self.protected = protected

    @classmethod
    def from_dict(cls, data):
        """Creates a Content object from a dictionary."""
        return cls(
            rendered=data.get('rendered'),
            protected=data.get('protected')
        )

class Meta:
    """Represents the 'meta' part of the JSON data."""
    def __init__(self, data):
        # Initializes all meta properties from the provided dictionary
        for key, value in data.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, data):
        """Creates a Meta object from a dictionary."""
        return cls(data)

class YoastHeadJson:
    """Represents the 'yoast_head_json' part of the JSON data."""
    def __init__(self, data):
        # Initializes all yoast_head_json properties from the provided dictionary
        self.title = data.get('title')
        self.description = data.get('description')
        self.robots = data.get('robots')
        self.og_locale = data.get('og_locale')
        self.og_type = data.get('og_type')
        self.og_title = data.get('og_title')
        self.og_description = data.get('og_description')
        self.og_url = data.get('og_url')
        self.og_site_name = data.get('og_site_name')
        self.article_modified_time = data.get('article_modified_time')
        self.og_image = data.get('og_image')
        self.twitter_card = data.get('twitter_card')
        self.twitter_misc = data.get('twitter_misc')
        self.schema_data = data.get('schema')

    @classmethod
    def from_dict(cls, data):
        """Creates a YoastHeadJson object from a dictionary."""
        return cls(data)


class Product:
    """Represents the entire product JSON structure."""

    def __init__(self, data):
        """
        Initializes the Product object from a dictionary.
        """
        self.id = data.get('id')
        self.date = self._to_datetime(data.get('date'))
        self.date_gmt = self._to_datetime(data.get('date_gmt'))
        self.guid = Guid.from_dict(data.get('guid', {}))
        self.modified = self._to_datetime(data.get('modified'))
        self.modified_gmt = self._to_datetime(data.get('modified_gmt'))
        self.slug = data.get('slug')
        self.status = data.get('status')
        self.type = data.get('type')
        self.link = data.get('link')
        # self.title = RenderedData.from_dict(data.get('title', {}))
        self.title = data.get('title', {}).get('rendered', '')
        self.content = Content.from_dict(data.get('content', {}))
        self.featured_media = data.get('featured_media')
        self.template = data.get('template')
        self.meta = Meta.from_dict(data.get('meta', {}))
        self.certyfikat = data.get('certyfikat', [])
        self.maks_cisnienie = data.get('maks-cisnienie', [])
        self.maks_temperatura = data.get('maks-temperatura', [])
        self.maks_wydajnosc = data.get('maks-wydajnosc', [])
        self.material = data.get('material', [])
        self.producentmarka = data.get('producentmarka', [])
        self.sektor_przemyslu = data.get('sektor-przemyslu', [])
        self.tapflo_solutions = data.get('tapflo-solutions', [])
        self.typ_urzadzenia = data.get('typ-urzadzenia', [])
        self.class_list = data.get('class_list', [])
        self.acf = data.get('acf', {})
        self.yoast_head = data.get('yoast_head')
        self.yoast_head_json = YoastHeadJson.from_dict(data.get('yoast_head_json', {}))
        self.links = data.get('_links')

    def _to_datetime(self, date_string):
        """Converts an ISO 8601 string to a datetime object."""
        if date_string:
            return datetime.fromisoformat(date_string)
        return None

    @classmethod
    def from_json(cls, json_string):
        """Creates a Product object from a JSON string."""
        data = json.loads(json_string)
        return cls(data)

    def __repr__(self):
        return f"<Product(id={self.id}, title='{self.title.rendered}')>"

