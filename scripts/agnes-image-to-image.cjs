#!/usr/bin/env node

/**
 * Agnes AI Image-to-Image Generation Script
 *
 * Modified to accept a file path for the image to avoid command line length limits.
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

// ... (existing code, add file handling)

// Supported size tiers and their aspect ratios
const SIZE_TIERS = {
  '1K': { width: 1024, height: 1024, ratios: ['1:1', '3:4', '4:3', '16:9', '9:16', '2:3', '3:2', '21:9'] },
  '2K': { width: 1536, height: 1536, ratios: ['1:1', '3:4', '4:3', '16:9', '9:16', '2:3', '3:2', '21:9'] },
  '3K': { width: 2048, height: 2048, ratios: ['1:1', '3:4', '4:3', '16:9', '9:16', '2:3', '3:2', '21:9'] },
  '4K': { width: 4096, height: 4096, ratios: ['1:1', '3:4', '4:3', '16:9', '9:16', '2:3', '3:2', '21:9'] }
};

/**
 * Parse command line arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const config = {
    apiKey: process.env.AGNES_API_KEY,
    image: null,
    prompt: '',
    size: '1024x1024',
    ratio: '1:1',
    model: 'agnes-image-2.1-flash',
    out: null
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--image':
      case '-i':
        const input = args[++i];
        if (fs.existsSync(input)) {
           const ext = path.extname(input).replace('.', '');
           const base64 = fs.readFileSync(input).toString('base64');
           config.image = `data:image/${ext};base64,${base64}`;
        } else {
           config.image = input;
        }
        break;
      case '--out':
      case '-o':
        config.out = args[++i];
        break;
      case '--prompt':
      case '-p':
        config.prompt = args[++i];
        break;
      case '--size':
      case '-s':
        config.size = args[++i];
        break;
      case '--ratio':
      case '-r':
        config.ratio = args[++i];
        break;
      case '--model':
      case '-m':
        config.model = args[++i];
        break;
      case '--help':
      case '-h':
        printUsage();
        process.exit(0);
        break;
    }
  }

  return config;
}

/**
 * Print usage information
 */
function printUsage() {
  console.log(`
Agnes AI Image-to-Image Generator

Usage: node agnes-image-to-image.js [options]

Options:
  -i, --image <data-uri>    Base64 data URI of input image (required)
  -p, --prompt <text>       Prompt describing the transformation (required)
  -s, --size <dimensions>   Output size in format "WIDTHxHEIGHT" (default: 1024x1024)
  -r, --ratio <ratio>       Aspect ratio (default: 1:1)
                             Options: 1:1, 3:4, 4:3, 16:9, 9:16, 2:3, 3:2, 21:9
  -m, --model <model>       Model to use (default: agnes-image-2.1-flash)
  -o, --out <file>          Write the result image to this file instead of
                             printing base64 to stdout (default: stdout)

Environment Variables:
  AGNES_API_KEY             Your Agnes AI API key (required)

Examples:
  node agnes-image-to-image.js \\
    --image "data:image/png;base64,iVBORw0KG..." \\
    --prompt "Make the object orange" \\
    --size "1024x768" \\
    --ratio "3:4"

  node agnes-image-to-image.js \\
    --image "$(cat input.png | base64 -w 0)" \\
    --prompt "Transform this image" \\
    --ratio "16:9"
  `);
}

/**
 * Validate configuration
 */
function validateConfig(config) {
  const errors = [];

  if (!config.apiKey) {
    errors.push('AGNES_API_KEY environment variable is required');
  }

  if (!config.image) {
    errors.push('--image parameter is required');
  }

  if (!config.prompt) {
    errors.push('--prompt parameter is required');
  }

  if (!config.size || !config.size.includes('x')) {
    errors.push('--size must be in format "WIDTHxHEIGHT" (e.g., "1024x768")');
  }

  if (!config.ratio || !SIZE_TIERS['1K'].ratios.includes(config.ratio)) {
    errors.push(`--ratio must be one of: ${SIZE_TIERS['1K'].ratios.join(', ')}`);
  }

  return errors;
}

/**
 * Calculate dimensions based on size and ratio
 */
function calculateDimensions(size, ratio) {
  const [width, height] = size.split('x').map(Number);
  const [rW, rH] = ratio.split(':').map(Number);
  const ratioValue = rW / rH;

  if (width / height > ratioValue) {
    // Width is too wide, adjust height
    return { width, height: Math.round(width / ratioValue) };
  } else {
    // Height is too tall, adjust width
    return { width: Math.round(height * ratioValue), height };
  }
}

/**
 * Convert data URI to base64 string
 */
function dataUriToBase64(dataUri) {
  if (!dataUri) return null;

  const match = dataUri.match(/^data:([a-zA-Z0-9]+\/[a-zA-Z0-9-.+]+);base64,(.+)$/);
  if (!match) {
    throw new Error('Invalid data URI format. Expected format: data:image/png;base64,...');
  }

  return match[2];
}

/**
 * Make HTTP/HTTPS request
 */
function makeRequest(options, data) {
  return new Promise((resolve, reject) => {
    const client = options.protocol === 'https:' ? https : http;
    const req = client.request(options, (res) => {
      let body = '';

      res.on('data', (chunk) => {
        body += chunk;
      });

      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            const json = JSON.parse(body);
            resolve(json);
          } catch (e) {
            reject(new Error(`Failed to parse response: ${body}`));
          }
        } else {
          reject(new Error(`API request failed with status ${res.statusCode}: ${body}`));
        }
      });
    });

    req.on('error', (error) => {
      reject(new Error(`Request error: ${error.message}`));
    });

    req.write(JSON.stringify(data));
    req.end();
  });
}

/**
 * Generate image transformation
 */
async function generateImage(config) {
  try {
    // Validate configuration
    const errors = validateConfig(config);
    if (errors.length > 0) {
      throw new Error(errors.join('\n'));
    }

    // Convert data URI to base64
    const base64Image = dataUriToBase64(config.image);

    // Prepare request payload
    const payload = {
      model: config.model,
      prompt: config.prompt,
      size: config.size,
      extra_body: {
        image: [`data:image/png;base64,${base64Image}`],
        response_format: 'b64_json'
      }
    };

    // Make API request
    const response = await makeRequest({
      hostname: 'apihub.agnes-ai.com',
      port: 443,
      path: '/v1/images/generations',
      method: 'POST',
      protocol: 'https:',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${config.apiKey}`,
        'Content-Length': JSON.stringify(payload).length
      }
    }, payload);

    // Check for errors in response
    if (response.error) {
      throw new Error(`API error: ${response.error.message || JSON.stringify(response.error)}`);
    }

    // Extract base64 image from response
    if (!response.data || !response.data[0] || !response.data[0].b64_json) {
      throw new Error('Invalid response format: missing b64_json');
    }

    return response.data[0].b64_json;

  } catch (error) {
    throw new Error(`Image generation failed: ${error.message}`);
  }
}

/**
 * Save base64 image to file
 */
function saveBase64Image(base64Data, outputPath) {
  const fs = require('fs');
  fs.writeFileSync(outputPath, Buffer.from(base64Data, 'base64'));
  console.log(`Image saved to: ${outputPath}`);
}

/**
 * Main function
 */
async function main() {
  try {
    const config = parseArgs();
    const base64Output = await generateImage(config);

    if (config.out) {
      // Write result to disk (parent dirs created if missing)
      const outPath = path.resolve(config.out);
      fs.mkdirSync(path.dirname(outPath), { recursive: true });
      saveBase64Image(base64Output, outPath);
    } else {
      // Output base64 image to stdout
      console.log(base64Output);
    }

  } catch (error) {
    console.error(`Error: ${error.message}`);
    if (process.argv.includes('--help') || process.argv.includes('-h')) {
      printUsage();
    }
    process.exit(1);
  }
}

// Run the script
if (require.main === module) {
  main();
}

// Export functions for programmatic use
module.exports = {
  generateImage,
  parseArgs,
  validateConfig,
  calculateDimensions,
  dataUriToBase64,
  saveBase64Image,
  SIZE_TIERS
};
