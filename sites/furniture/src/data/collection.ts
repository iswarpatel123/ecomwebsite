import type { CollectionGridItem } from "@repo/storefront-patterns";

const PDP_HREF = "/";
const VIDEO = "/assets/koala/videos/koala-video.mp4";

const swatches = [
  { name: "Australia 01 (Pantone)", src: "/assets/koala/img-038-0aefc6d3.png" },
  { name: "Morning Fog", src: "/assets/koala/img-042-2708913a.png" },
  { name: "Cinnamon Sky", src: "/assets/koala/img-043-69613acc.png" },
  { name: "Moonlit Silver", src: "/assets/koala/img-044-30301667.png" },
  { name: "Forest Dawn", src: "/assets/koala/img-045-37067ca1.png" },
  { name: "Silver Sand", src: "/assets/koala/img-046-a2cdf5a7.png" },
  { name: "Coastal Moss", src: "/assets/koala/img-047-b5b8d9d4.png" },
  { name: "Suffolk Sandstone", src: "/assets/koala/img-048-96d3c8a7.png" },
];

/** Bangalow-style collection mock using existing PDP media. */
export const collectionItems: CollectionGridItem[] = [
  {
    type: "product",
    id: "bangalow-modular",
    product: {
      href: PDP_HREF,
      title: "Bangalow Modular Sofa",
      subtitle: "2 Sections • 12 Sizes",
      images: [
        { src: "/assets/koala/img-000-dark-grey.png", alt: "Bangalow Modular Sofa in dark grey" },
        { src: "/assets/koala/img-001-8d40340b.png", alt: "Bangalow Modular Sofa lifestyle" },
        { src: "/assets/koala/img-005-9c1f89ac.png", alt: "Bangalow Modular Sofa studio view" },
      ],
      rating: 5,
      reviewCount: 842,
      price: "$1,290",
      compareAtPrice: "$1,490",
      saveLabel: "SAVE $200",
      swatches,
    },
  },
  {
    type: "product",
    id: "bangalow-3-seater",
    product: {
      href: PDP_HREF,
      title: "Bangalow 3 Seater Sofa",
      subtitle: "3 Seater with Chaise",
      images: [
        { src: "/assets/koala/img-001-8d40340b.png", alt: "Bangalow 3 Seater Sofa" },
        { src: "/assets/koala/img-002-4cf4af0e.png", alt: "Bangalow 3 Seater as a bed" },
      ],
      rating: 5,
      reviewCount: 516,
      price: "$1,090",
      compareAtPrice: "$1,290",
      saveLabel: "SAVE $200",
      swatches: swatches.slice(0, 6),
    },
  },
  {
    type: "promo",
    id: "promo-covers",
    promo: {
      title: "Removable & washable covers",
      imageSrc: "/assets/koala/img-024-df90a771.png",
      imageAlt: "Sofa covers demonstration",
      videoSrc: VIDEO,
      ctaLabel: "Shop now",
      ctaHref: PDP_HREF,
    },
  },
  {
    type: "product",
    id: "bangalow-corner",
    product: {
      href: PDP_HREF,
      title: "Bangalow Corner Sofa",
      subtitle: "L-Shape • 8 Configurations",
      images: [
        { src: "/assets/koala/img-003-55b0da30.png", alt: "Bangalow Corner Sofa detail" },
        { src: "/assets/koala/img-004-31bb2a9f.png", alt: "Bangalow Corner Sofa in living room" },
      ],
      rating: 4.9,
      reviewCount: 391,
      price: "$1,690",
      compareAtPrice: "$1,990",
      saveLabel: "SAVE $300",
      swatches: swatches.slice(1, 7),
    },
  },
  {
    type: "quote",
    id: "quote-jamie",
    quote: {
      rating: 5,
      quote: "Amazing couch! Great quality, super comfy, and the covers zip off for washing.",
      author: "Jamie T.",
    },
  },
  {
    type: "promo",
    id: "promo-modular",
    promo: {
      title: "True modularity",
      imageSrc: "/assets/koala/img-025-f928d801.png",
      imageAlt: "Friends assembling a modular sofa",
      videoSrc: VIDEO,
      ctaLabel: "Shop now",
      ctaHref: PDP_HREF,
    },
  },
  {
    type: "product",
    id: "bangalow-ottoman",
    product: {
      href: PDP_HREF,
      title: "Bangalow Ottoman",
      subtitle: "Add-on Module",
      images: [
        { src: "/assets/koala/img-006-553b3ba8.png", alt: "Bangalow Ottoman" },
        { src: "/assets/koala/img-007-c460d576.png", alt: "Bangalow Ottoman alternate view" },
      ],
      rating: 4.8,
      reviewCount: 204,
      price: "$390",
      compareAtPrice: "$450",
      saveLabel: "SAVE $60",
      swatches: swatches.slice(0, 5),
    },
  },
  {
    type: "promo",
    id: "promo-fabric",
    promo: {
      title: "Luxe fabric",
      imageSrc: "/assets/koala/img-028-1ccf9fab.png",
      imageAlt: "Close up of sofa fabric colours",
      videoSrc: VIDEO,
      ctaLabel: "Shop now",
      ctaHref: PDP_HREF,
    },
  },
  {
    type: "product",
    id: "bangalow-loveseat",
    product: {
      href: PDP_HREF,
      title: "Bangalow Loveseat",
      subtitle: "2 Seater • Compact",
      images: [
        { src: "/assets/koala/img-008-9b032ead.png", alt: "Bangalow Loveseat" },
        { src: "/assets/koala/img-000-72dadcb6.png", alt: "Bangalow Loveseat front view" },
      ],
      rating: 5,
      reviewCount: 178,
      price: "$890",
      compareAtPrice: "$1,090",
      saveLabel: "SAVE $200",
      swatches: swatches.slice(2, 8),
    },
  },
  {
    type: "trust",
    id: "trust-policies",
    trust: {
      items: [
        {
          id: "returns",
          label: "120 Day Free Returns",
          iconSrc: "/assets/koala/img-040-cf67cad6.svg",
          iconAlt: "",
        },
        {
          id: "delivery",
          label: "Fast delivery",
          iconSrc: "/assets/koala/img-039-4432bd64.svg",
          iconAlt: "",
        },
        {
          id: "warranty",
          label: "5-Year Warranty",
          iconSrc: "/assets/koala/img-041-563a3c24.svg",
          iconAlt: "",
        },
      ],
      ctaLabel: "Show more",
      ctaHref: "#faq",
    },
  },
  {
    type: "product",
    id: "bangalow-chaise",
    product: {
      href: PDP_HREF,
      title: "Bangalow Chaise Sofa",
      subtitle: "Left or Right Chaise",
      images: [
        { src: "/assets/koala/img-015-179c25f4.png", alt: "Bangalow Chaise Sofa" },
        { src: "/assets/koala/img-019-ca3174c0.png", alt: "Bangalow Chaise Sofa alternate" },
      ],
      rating: 4.9,
      reviewCount: 267,
      price: "$1,490",
      compareAtPrice: "$1,790",
      saveLabel: "SAVE $300",
      swatches,
    },
  },
  {
    type: "product",
    id: "wanda-sofa-bed",
    product: {
      href: PDP_HREF,
      title: "Wanda Sofa Bed",
      subtitle: "Sofa + Queen Bed",
      images: [
        { src: "/assets/koala/img-002-4cf4af0e.png", alt: "Wanda Sofa Bed" },
        { src: "/assets/koala/img-004-31bb2a9f.png", alt: "Wanda Sofa Bed lifestyle" },
      ],
      rating: 4.8,
      reviewCount: 2085,
      price: "$999",
      compareAtPrice: "$1,199",
      saveLabel: "SAVE $200",
      swatches: swatches.slice(0, 6),
    },
  },
];

export const collectionTitle = "Bangalow Modular Sofas";
