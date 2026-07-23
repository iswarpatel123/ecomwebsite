"""Small JSON-friendly models used by the clone workflow.

The original service used Pydantic models because it was exposed through
FastAPI.  The standalone tooling uses dataclasses instead, keeping imports
lightweight and making extraction documents easy for agents to inspect.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ElementRect:
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0
    top: float = 0
    right: float = 0
    bottom: float = 0
    left: float = 0


@dataclass
class ElementStyles:
    display: Optional[str] = None
    position: Optional[str] = None
    float_: Optional[str] = None
    flex_direction: Optional[str] = None
    flex_wrap: Optional[str] = None
    justify_content: Optional[str] = None
    align_items: Optional[str] = None
    gap: Optional[str] = None
    grid_template_columns: Optional[str] = None
    grid_template_rows: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    margin: Optional[str] = None
    padding: Optional[str] = None
    background_color: Optional[str] = None
    background_image: Optional[str] = None
    color: Optional[str] = None
    border: Optional[str] = None
    border_radius: Optional[str] = None
    box_shadow: Optional[str] = None
    opacity: Optional[str] = None
    overflow: Optional[str] = None
    visibility: Optional[str] = None
    font_family: Optional[str] = None
    font_size: Optional[str] = None
    font_weight: Optional[str] = None
    line_height: Optional[str] = None
    text_align: Optional[str] = None
    transform: Optional[str] = None


@dataclass
class ElementInfo:
    tag: str
    rect: ElementRect = field(default_factory=ElementRect)
    styles: ElementStyles = field(default_factory=ElementStyles)
    id: Optional[str] = None
    classes: List[str] = field(default_factory=list)
    text_content: Optional[str] = None
    inner_html_length: int = 0
    raw_html_length: int = 0
    attributes: Dict[str, str] = field(default_factory=dict)
    is_visible: bool = True
    is_interactive: bool = False
    children: List["ElementInfo"] = field(default_factory=list)
    children_count: int = 0
    xpath: Optional[str] = None
    selector: Optional[str] = None


@dataclass
class AssetInfo:
    url: str
    type: str
    size: Optional[int] = None
    # Where the asset is used on the page (critical for contracts).
    selector: Optional[str] = None
    xpath: Optional[str] = None
    alt: Optional[str] = None
    role: Optional[str] = None
    width: Optional[float] = None
    height: Optional[float] = None
    top: Optional[float] = None
    left: Optional[float] = None
    section_hint: Optional[str] = None
    is_visible: Optional[bool] = None
    is_primary: Optional[bool] = None  # large / above-the-fold hero-like


@dataclass
class PageAssets:
    images: List[AssetInfo] = field(default_factory=list)
    scripts: List[AssetInfo] = field(default_factory=list)
    stylesheets: List[AssetInfo] = field(default_factory=list)
    fonts: List[AssetInfo] = field(default_factory=list)
    # url -> list of usage sites (selector, alt, rect) for contract generation
    image_usages: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "images": [asdict(item) for item in self.images],
            "scripts": [asdict(item) for item in self.scripts],
            "stylesheets": [asdict(item) for item in self.stylesheets],
            "fonts": [asdict(item) for item in self.fonts],
            "image_usages": self.image_usages,
            "total_images": self.total_images,
            "total_scripts": self.total_scripts,
            "total_stylesheets": self.total_stylesheets,
            "total_fonts": self.total_fonts,
        }

    @property
    def total_images(self) -> int:
        return len(self.images)

    @property
    def total_scripts(self) -> int:
        return len(self.scripts)

    @property
    def total_stylesheets(self) -> int:
        return len(self.stylesheets)

    @property
    def total_fonts(self) -> int:
        return len(self.fonts)


@dataclass
class PageMetadata:
    url: str
    title: str
    viewport_width: int
    viewport_height: int
    page_width: int
    page_height: int
    total_elements: int
    max_depth: int
    load_time_ms: int


@dataclass
class StyleSummary:
    colors: Dict[str, int] = field(default_factory=dict)
    background_colors: Dict[str, int] = field(default_factory=dict)
    font_families: Dict[str, int] = field(default_factory=dict)
    font_sizes: Dict[str, int] = field(default_factory=dict)
    margins: Dict[str, int] = field(default_factory=dict)
    paddings: Dict[str, int] = field(default_factory=dict)
    display_types: Dict[str, int] = field(default_factory=dict)
    position_types: Dict[str, int] = field(default_factory=dict)


@dataclass
class StylesheetContent:
    url: str
    content: str
    is_inline: bool = False


@dataclass
class CSSData:
    stylesheets: List[StylesheetContent] = field(default_factory=list)
    variables: List[Dict[str, str]] = field(default_factory=list)
    media_queries: Dict[str, str] = field(default_factory=dict)


@dataclass
class InteractionState:
    selector: str
    state: str
    styles: Dict[str, str] = field(default_factory=dict)


@dataclass
class InteractionData:
    hover_states: List[InteractionState] = field(default_factory=list)
    focus_states: List[InteractionState] = field(default_factory=list)


@dataclass
class ExtractionResult:
    success: bool
    message: str
    metadata: Optional[PageMetadata] = None
    dom_tree: Optional[ElementInfo] = None
    style_summary: Optional[StyleSummary] = None
    assets: Optional[PageAssets] = None
    raw_html: Optional[str] = None
    css_data: Optional[CSSData] = None
    interaction_data: Optional[InteractionData] = None
    screenshot_path: Optional[str] = None
    full_page_screenshot_path: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-compatible extraction document."""
        value = asdict(self)
        if self.assets is not None:
            value["assets"] = self.assets.to_dict()
        return value
