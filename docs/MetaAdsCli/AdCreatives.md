# Ad Creatives


This guide covers how to create and manage ad creatives with Ads CLI, including link ads, video ads, photo posts, and Dynamic Creative Optimization.

## About ad creatives

An ad creative is an independent object that can be reused across multiple ads. The workflow for Ads CLI is:

1. Create an ad creative with `meta ads creative create`
2. Reference the ad creative when creating an ad with `meta ads ad create --creative-id <CREATIVE_ID>`

Every ad creative requires a `--page-id` -- the Facebook Business Page that acts as the ad's identity. Find your Business Page IDs with:

```
meta ads page list
```

See [Find your IDs](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/tutorials-and-recipes#find-your-ids) for more information on finding any IDs needed for Ads CLI.

## Standard ad creatives

### Link ads

A link ad includes an image, headline, body text, and a destination URL. This is the most common ad format.

```
meta ads creative create --name "Summer Sale" \
  --page-id <PAGE_ID> \
  --image ./banner.jpg \
  --body "50% off everything!" \
  --title "Shop Now" \
  --link-url https://example.com/sale \
  --description "Limited time offer" \
  --call-to-action SHOP_NOW
```

### Video ads

A video ad includes a video file, optional thumbnail image, headline, and destination URL.

```
meta ads creative create --name "Video Promo" \
  --page-id <PAGE_ID> \
  --video ./promo.mp4 \
  --body "Watch our new collection" \
  --title "New Arrivals" \
  --link-url https://example.com/new
```

### Photo posts

A photo post on your Business Page. Created when no `--link-url` is provided.

```
meta ads creative create --name "Page Post" \
  --page-id <PAGE_ID> \
  --image ./photo.jpg \
  --body "Check out our latest product!"
```

### How the format is determined

- `--video` provided → Video ad
- `--link-url` provided (no video) → Link ad
- Neither video nor link URL → Photo post

### Supported media formats

**Images:** .jpg, .jpeg, .png, .gif, .bmp, .webp

**Videos:** .mp4, .mov, .avi, .mkv, .wmv

Ads CLI uploads media files automatically when you create or update an ad creative.

### Call-to-action types

Use with the `--call-to-action` option:

`APPLY_NOW`, `BOOK_TRAVEL`, `BUY_NOW`, `CONTACT_US`, `DOWNLOAD`, `GET_OFFER`, `GET_QUOTE`, `LEARN_MORE`, `NO_BUTTON`, `OPEN_LINK`, `SHOP_NOW`, `SIGN_UP`, `SUBSCRIBE`, `WATCH_MORE`

### Instagram placements

To run ads on Instagram, pass an Instagram account ID:

```
meta ads creative create --name "Insta Ad" \
  --page-id <PAGE_ID> \
  --instagram-actor-id <INSTAGRAM_ACCOUNT_ID> \
  --image ./banner.jpg \
  --body "Shop our collection" \
  --link-url https://example.com
```

## Dynamic Creative Optimization

Dynamic Creative Optimization lets you provide multiple variations of images, headlines, body text, descriptions, and call-to-action buttons. Meta automatically tests combinations and optimizes delivery toward the best-performing variants.

### Requirements

- `--link-url` for the destination URL
- At least one `--images` or `--videos` asset
- Plural flags (`--images`, `--titles`, `--bodies`) instead of the standard single-asset flags (`--image`, `--video`, `--body`, `--title`)

### Create an ad creative

Use the plural flags (`--images`, `--titles`, `--bodies`, and others) and repeat each flag for additional variants:

```
meta ads creative create --name "DCO Test" \
  --page-id <PAGE_ID> \
  --link-url https://example.com \
  --images ./img1.jpg --images ./img2.jpg --images ./img3.jpg \
  --titles "Shop Now" --titles "Learn More" \
  --bodies "50% off everything!" --bodies "Free shipping today!" \
  --descriptions "Limited time offer" --descriptions "While supplies last" \
  --call-to-actions SHOP_NOW --call-to-actions LEARN_MORE
```

### Use with videos

```
meta ads creative create --name "Video DCO" \
  --page-id <PAGE_ID> \
  --link-url https://example.com \
  --videos ./vid1.mp4 --videos ./vid2.mp4 \
  --titles "New Arrivals" --titles "Watch Now" \
  --bodies "Check out our new collection" --bodies "See what's trending"
```

### Limits

| Asset Type | Maximum |
|------------|---------|
| Images | 10 |
| Videos | 10 |
| Titles | 5 |
| Bodies | 5 |
| Descriptions | 5 |
| Call-to-actions | 5 |

## Update ad creatives

Update specific fields of an existing ad creative. Ads CLI changes only the fields you specify:

```
# Update text
meta ads creative update <CREATIVE_ID> --body "New ad copy" --title "New Headline"

# Replace the image
meta ads creative update <CREATIVE_ID> --image ./new-banner.jpg

# Replace the video
meta ads creative update <CREATIVE_ID> --video ./new-video.mp4

# Change status
meta ads creative update <CREATIVE_ID> --status PAUSED
```

Available update options: `--name`, `--body`, `--title`, `--link-url`, `--description`, `--call-to-action`, `--image`, `--video`, `--instagram-actor-id`, `--status`

**Note:** The API prevents updating some fields after creation.

If an update fails, create a new ad creative instead.

## Delete ad creatives

**Note:** You cannot delete ad creatives that active ads use. Pause or delete the associated ads first.

```
meta ads creative delete <CREATIVE_ID>
meta ads creative delete <CREATIVE_ID> --force    # Skip confirmation
```

## Full workflow example

```
# 1. Find your Business Page ID
meta ads page list

# 2. Create an ad creative
meta ads creative create --name "Launch Ad" \
  --page-id <PAGE_ID> \
  --image ./launch-banner.jpg \
  --body "Our new product is here!" \
  --title "Just Launched" \
  --link-url https://example.com/launch \
  --call-to-action SHOP_NOW

# 3. Create an ad with the returned ad creative ID
meta ads ad create <AD_SET_ID> --name "Launch Ad - US" --creative-id <CREATIVE_ID>

# 4. Activate the ad with the returned ad ID
meta ads ad update <AD_ID> --status ACTIVE
```
