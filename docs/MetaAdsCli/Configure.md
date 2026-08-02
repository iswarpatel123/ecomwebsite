# Configuration


This guide covers how Ads CLI resolves configuration settings, including environment variables, `.env` files, and the config directory.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ACCESS_TOKEN` | Yes | System user access token that you generate in the Meta Business Suite |
| `AD_ACCOUNT_ID` | Yes (for most commands) | Your Meta ad account ID |
| `BUSINESS_ID` | No | Default business ID (for catalog/dataset commands) |

## Configuration precedence

Ads CLI resolves settings in this order (highest priority first):

1. Command-line flags (for example, `--ad-account-id`)
2. Environment variables
3. Project-level `.env` file
4. User-level config (`~/.config/meta/`)

## Use a .env file

To prevent setting the environment variables for each session, you can add a `.env` file in the directory where you are running Ads CLI:

```
cat > .env << 'DOTENV'
ACCESS_TOKEN='<ACCESS_TOKEN>'
AD_ACCOUNT_ID='<AD_ACCOUNT_ID>'
BUSINESS_ID='<BUSINESS_ID>'
DOTENV
```

**Note:** Environment variables set in your shell take precedence over `.env` values.

## Config directory

Ads CLI stores configuration in an [XDG-compliant](https://specifications.freedesktop.org/basedir-spec/latest/) directory:

```
~/.config/meta/
```

You can override the base directory by setting the `XDG_CONFIG_HOME` environment variable.
