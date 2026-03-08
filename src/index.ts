#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import * as fs from "node:fs/promises";
import * as path from "node:path";
import {
  isVideoFile,
  getVideoMetadata,
  formatFileSize,
  formatDuration,
  resolveAndValidatePath,
  runFfmpeg,
  isFfmpegAvailable,
  isFfprobeAvailable,
  VIDEO_EXTENSIONS,
} from "./utils.js";

const server = new McpServer({
  name: "ad-videos",
  version: "1.0.0",
});

// ── Tool: video_list ──────────────────────────────────────────────────────────
server.tool(
  "video_list",
  "List video files in a directory. Returns file names, sizes, and basic info. Supports recursive scanning and filtering by extension.",
  {
    directory: z.string().describe("Absolute path to the directory to scan"),
    recursive: z
      .boolean()
      .optional()
      .default(false)
      .describe("Whether to scan subdirectories recursively"),
    extension: z
      .string()
      .optional()
      .describe(
        'Filter by specific extension (e.g. "mp4", "mov"). Omit to include all video types.'
      ),
  },
  async ({ directory, recursive, extension }) => {
    const resolved = await resolveAndValidatePath(directory);
    const stat = await fs.stat(resolved);
    if (!stat.isDirectory()) {
      return {
        content: [
          { type: "text", text: `Error: "${resolved}" is not a directory.` },
        ],
      };
    }

    const videos: { name: string; path: string; size: number }[] = [];

    async function scan(dir: string) {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory() && recursive) {
          await scan(fullPath);
        } else if (entry.isFile() && isVideoFile(entry.name)) {
          if (
            extension &&
            path.extname(entry.name).slice(1).toLowerCase() !==
              extension.toLowerCase()
          ) {
            continue;
          }
          const fileStat = await fs.stat(fullPath);
          videos.push({
            name: entry.name,
            path: fullPath,
            size: fileStat.size,
          });
        }
      }
    }

    await scan(resolved);

    if (videos.length === 0) {
      return {
        content: [
          {
            type: "text",
            text: `No video files found in "${resolved}"${recursive ? " (recursive)" : ""}.`,
          },
        ],
      };
    }

    const lines = videos.map(
      (v) => `- ${v.name} (${formatFileSize(v.size)}) — ${v.path}`
    );
    return {
      content: [
        {
          type: "text",
          text: `Found ${videos.length} video file(s) in "${resolved}":\n\n${lines.join("\n")}`,
        },
      ],
    };
  }
);

// ── Tool: video_info ──────────────────────────────────────────────────────────
server.tool(
  "video_info",
  "Get detailed metadata for a video file including duration, resolution, codecs, bitrate, and file details. Requires ffprobe for full metadata; returns basic file info if ffprobe is unavailable.",
  {
    file_path: z
      .string()
      .describe("Absolute path to the video file to inspect"),
  },
  async ({ file_path }) => {
    const meta = await getVideoMetadata(file_path);

    const parts: string[] = [
      `**File:** ${meta.fileName}`,
      `**Path:** ${meta.filePath}`,
      `**Size:** ${formatFileSize(meta.fileSize)}`,
      `**Format:** ${meta.format}`,
    ];

    if (meta.duration !== null) {
      parts.push(`**Duration:** ${formatDuration(meta.duration)}`);
    }
    if (meta.width !== null && meta.height !== null) {
      parts.push(`**Resolution:** ${meta.width}x${meta.height}`);
    }
    if (meta.videoCodec) parts.push(`**Video Codec:** ${meta.videoCodec}`);
    if (meta.audioCodec) parts.push(`**Audio Codec:** ${meta.audioCodec}`);
    if (meta.bitrate !== null) {
      parts.push(
        `**Bitrate:** ${(meta.bitrate / 1000).toFixed(0)} kbps`
      );
    }
    if (meta.frameRate) parts.push(`**Frame Rate:** ${meta.frameRate}`);
    parts.push(`**Created:** ${meta.createdAt}`);
    parts.push(`**Modified:** ${meta.modifiedAt}`);

    return {
      content: [{ type: "text", text: parts.join("\n") }],
    };
  }
);

// ── Tool: video_search ────────────────────────────────────────────────────────
server.tool(
  "video_search",
  "Search for video files by name pattern in a directory. Supports glob-like matching with case-insensitive substring search.",
  {
    directory: z.string().describe("Absolute path to the directory to search"),
    query: z.string().describe("Search string to match against file names (case-insensitive substring match)"),
    recursive: z
      .boolean()
      .optional()
      .default(true)
      .describe("Whether to search subdirectories recursively"),
  },
  async ({ directory, query, recursive }) => {
    const resolved = await resolveAndValidatePath(directory);
    const queryLower = query.toLowerCase();
    const matches: string[] = [];

    async function scan(dir: string) {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory() && recursive) {
          await scan(fullPath);
        } else if (
          entry.isFile() &&
          isVideoFile(entry.name) &&
          entry.name.toLowerCase().includes(queryLower)
        ) {
          matches.push(fullPath);
        }
      }
    }

    await scan(resolved);

    if (matches.length === 0) {
      return {
        content: [
          {
            type: "text",
            text: `No video files matching "${query}" found in "${resolved}".`,
          },
        ],
      };
    }

    return {
      content: [
        {
          type: "text",
          text: `Found ${matches.length} video(s) matching "${query}":\n\n${matches.map((m) => `- ${m}`).join("\n")}`,
        },
      ],
    };
  }
);

// ── Tool: video_thumbnail ─────────────────────────────────────────────────────
server.tool(
  "video_thumbnail",
  "Extract a thumbnail image from a video at a specified timestamp. Requires ffmpeg. Outputs a JPEG image.",
  {
    file_path: z.string().describe("Absolute path to the video file"),
    timestamp: z
      .string()
      .optional()
      .default("00:00:01")
      .describe('Timestamp to capture (HH:MM:SS format). Defaults to "00:00:01".'),
    output_path: z
      .string()
      .describe("Absolute path for the output JPEG thumbnail"),
  },
  async ({ file_path, timestamp, output_path }) => {
    const inputResolved = await resolveAndValidatePath(file_path);
    const outputResolved = path.resolve(output_path);

    await runFfmpeg([
      "-y",
      "-i",
      inputResolved,
      "-ss",
      timestamp,
      "-frames:v",
      "1",
      "-q:v",
      "2",
      outputResolved,
    ]);

    const stat = await fs.stat(outputResolved);
    return {
      content: [
        {
          type: "text",
          text: `Thumbnail saved to "${outputResolved}" (${formatFileSize(stat.size)}) at timestamp ${timestamp}.`,
        },
      ],
    };
  }
);

// ── Tool: video_trim ──────────────────────────────────────────────────────────
server.tool(
  "video_trim",
  "Trim a video to a specific time range. Requires ffmpeg. Uses stream copy for fast, lossless trimming by default.",
  {
    file_path: z.string().describe("Absolute path to the source video file"),
    start: z.string().describe("Start timestamp in HH:MM:SS format"),
    end: z.string().describe("End timestamp in HH:MM:SS format"),
    output_path: z.string().describe("Absolute path for the output trimmed video"),
    reencode: z
      .boolean()
      .optional()
      .default(false)
      .describe("Set to true to re-encode for frame-accurate trimming (slower but more precise)"),
  },
  async ({ file_path, start, end, output_path, reencode }) => {
    const inputResolved = await resolveAndValidatePath(file_path);
    const outputResolved = path.resolve(output_path);

    const args = ["-y", "-i", inputResolved, "-ss", start, "-to", end];
    if (!reencode) {
      args.push("-c", "copy");
    }
    args.push(outputResolved);

    await runFfmpeg(args);

    const stat = await fs.stat(outputResolved);
    return {
      content: [
        {
          type: "text",
          text: `Video trimmed from ${start} to ${end}. Output saved to "${outputResolved}" (${formatFileSize(stat.size)}).`,
        },
      ],
    };
  }
);

// ── Tool: video_convert ───────────────────────────────────────────────────────
server.tool(
  "video_convert",
  "Convert a video file to a different format. Requires ffmpeg. Common conversions: MP4, WebM, MOV, AVI, MKV.",
  {
    file_path: z.string().describe("Absolute path to the source video file"),
    output_path: z
      .string()
      .describe(
        "Absolute path for the converted output file. The output format is determined by the file extension."
      ),
    video_codec: z
      .string()
      .optional()
      .describe(
        'Video codec to use (e.g. "libx264", "libx265", "libvpx-vp9"). Omit for format default.'
      ),
    audio_codec: z
      .string()
      .optional()
      .describe(
        'Audio codec to use (e.g. "aac", "libopus", "mp3"). Omit for format default.'
      ),
    crf: z
      .number()
      .optional()
      .describe(
        "Constant Rate Factor for quality (0-51 for x264/x265, lower = better quality). Typical values: 18-28."
      ),
  },
  async ({ file_path, output_path, video_codec, audio_codec, crf }) => {
    const inputResolved = await resolveAndValidatePath(file_path);
    const outputResolved = path.resolve(output_path);

    const args = ["-y", "-i", inputResolved];
    if (video_codec) args.push("-c:v", video_codec);
    if (audio_codec) args.push("-c:a", audio_codec);
    if (crf !== undefined) args.push("-crf", String(crf));
    args.push(outputResolved);

    await runFfmpeg(args);

    const stat = await fs.stat(outputResolved);
    return {
      content: [
        {
          type: "text",
          text: `Video converted successfully. Output: "${outputResolved}" (${formatFileSize(stat.size)}).`,
        },
      ],
    };
  }
);

// ── Tool: video_resize ────────────────────────────────────────────────────────
server.tool(
  "video_resize",
  "Resize a video to a target resolution. Requires ffmpeg. Maintains aspect ratio when only width or height is specified.",
  {
    file_path: z.string().describe("Absolute path to the source video file"),
    output_path: z.string().describe("Absolute path for the resized output video"),
    width: z
      .number()
      .optional()
      .describe("Target width in pixels. Use -1 to auto-calculate from height while preserving aspect ratio."),
    height: z
      .number()
      .optional()
      .describe("Target height in pixels. Use -1 to auto-calculate from width while preserving aspect ratio."),
  },
  async ({ file_path, output_path, width, height }) => {
    if (width === undefined && height === undefined) {
      return {
        content: [
          {
            type: "text",
            text: "Error: At least one of width or height must be specified.",
          },
        ],
      };
    }

    const inputResolved = await resolveAndValidatePath(file_path);
    const outputResolved = path.resolve(output_path);

    const w = width ?? -1;
    const h = height ?? -1;
    // Ensure even dimensions for codec compatibility
    const scale = `scale=${w}:${h}:force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:ceil(ih/2)*2`;

    await runFfmpeg([
      "-y",
      "-i",
      inputResolved,
      "-vf",
      scale,
      outputResolved,
    ]);

    const stat = await fs.stat(outputResolved);
    return {
      content: [
        {
          type: "text",
          text: `Video resized to ${w === -1 ? "auto" : w}x${h === -1 ? "auto" : h}. Output: "${outputResolved}" (${formatFileSize(stat.size)}).`,
        },
      ],
    };
  }
);

// ── Tool: video_extract_audio ─────────────────────────────────────────────────
server.tool(
  "video_extract_audio",
  "Extract the audio track from a video file. Requires ffmpeg. Outputs common audio formats like MP3, AAC, WAV, or FLAC.",
  {
    file_path: z.string().describe("Absolute path to the source video file"),
    output_path: z
      .string()
      .describe(
        "Absolute path for the output audio file. Format determined by extension (e.g. .mp3, .aac, .wav)."
      ),
    audio_codec: z
      .string()
      .optional()
      .describe('Audio codec (e.g. "libmp3lame", "aac", "pcm_s16le", "flac"). Omit for format default.'),
  },
  async ({ file_path, output_path, audio_codec }) => {
    const inputResolved = await resolveAndValidatePath(file_path);
    const outputResolved = path.resolve(output_path);

    const args = ["-y", "-i", inputResolved, "-vn"];
    if (audio_codec) args.push("-c:a", audio_codec);
    args.push(outputResolved);

    await runFfmpeg(args);

    const stat = await fs.stat(outputResolved);
    return {
      content: [
        {
          type: "text",
          text: `Audio extracted to "${outputResolved}" (${formatFileSize(stat.size)}).`,
        },
      ],
    };
  }
);

// ── Tool: video_concat ────────────────────────────────────────────────────────
server.tool(
  "video_concat",
  "Concatenate multiple video files into one. Requires ffmpeg. All input videos should have the same codec and resolution for best results with stream copy.",
  {
    file_paths: z
      .array(z.string())
      .min(2)
      .describe("Array of absolute paths to video files, in the order they should appear"),
    output_path: z.string().describe("Absolute path for the concatenated output video"),
    reencode: z
      .boolean()
      .optional()
      .default(false)
      .describe("Set to true to re-encode (required if inputs have different codecs or resolutions)"),
  },
  async ({ file_paths, output_path, reencode }) => {
    const resolvedInputs = await Promise.all(
      file_paths.map((fp) => resolveAndValidatePath(fp))
    );
    const outputResolved = path.resolve(output_path);

    // Write a temporary concat file list
    const listPath = outputResolved + ".concat_list.txt";
    const listContent = resolvedInputs
      .map((fp) => `file '${fp.replace(/'/g, "'\\''")}'`)
      .join("\n");
    await fs.writeFile(listPath, listContent, "utf-8");

    try {
      const args = [
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        listPath,
      ];
      if (!reencode) {
        args.push("-c", "copy");
      }
      args.push(outputResolved);

      await runFfmpeg(args);

      const stat = await fs.stat(outputResolved);
      return {
        content: [
          {
            type: "text",
            text: `${resolvedInputs.length} videos concatenated. Output: "${outputResolved}" (${formatFileSize(stat.size)}).`,
          },
        ],
      };
    } finally {
      await fs.unlink(listPath).catch(() => {});
    }
  }
);

// ── Tool: video_capabilities ──────────────────────────────────────────────────
server.tool(
  "video_capabilities",
  "Check which video processing capabilities are available on this system (ffmpeg, ffprobe). Useful for understanding which tools will have full functionality.",
  {},
  async () => {
    const [ffmpeg, ffprobe] = await Promise.all([
      isFfmpegAvailable(),
      isFfprobeAvailable(),
    ]);

    const lines = [
      `**ffmpeg:** ${ffmpeg ? "Available" : "Not found — video processing tools (trim, convert, resize, thumbnail, extract audio, concat) will not work"}`,
      `**ffprobe:** ${ffprobe ? "Available" : "Not found — video_info will return basic file info only (no duration, resolution, codecs)"}`,
      "",
      `**Supported video extensions:** ${[...VIDEO_EXTENSIONS].join(", ")}`,
    ];

    return {
      content: [{ type: "text", text: lines.join("\n") }],
    };
  }
);

// ── Nano Banana Prompt Library ─────────────────────────────────────────────────

/** Resolve the prompts directory relative to this file. */
function getPromptsDir(): string {
  const thisDir = new URL(".", import.meta.url).pathname;
  return path.resolve(thisDir, "..", "prompts");
}

interface PromptEntry {
  id: number;
  content: string;
  title: string;
  description: string;
  sourceMedia: string[];
  needReferenceImages: boolean;
}

interface ManifestCategory {
  slug: string;
  title: string;
  file: string;
  count: number;
}

interface Manifest {
  updatedAt: string;
  totalPrompts: number;
  categories: ManifestCategory[];
}

// ── Tool: prompt_categories ───────────────────────────────────────────────────
server.tool(
  "prompt_categories",
  "List all available image prompt categories from the Nano Banana Pro library (10,000+ prompts). Returns category names, slugs, and prompt counts. Use this first to find the right category for your needs.",
  {},
  async () => {
    const manifestPath = path.join(getPromptsDir(), "manifest.json");
    const raw = await fs.readFile(manifestPath, "utf-8");
    const manifest: Manifest = JSON.parse(raw);

    const lines = manifest.categories.map(
      (c) => `- **${c.title}** (${c.slug}) — ${c.count} prompts`
    );

    return {
      content: [
        {
          type: "text",
          text: `Nano Banana Pro Prompt Library — ${manifest.totalPrompts} total prompts\nLast updated: ${manifest.updatedAt}\n\n**Categories:**\n${lines.join("\n")}`,
        },
      ],
    };
  }
);

// ── Tool: prompt_search ───────────────────────────────────────────────────────
server.tool(
  "prompt_search",
  "Search the Nano Banana Pro prompt library for image generation prompts matching a keyword. Searches across prompt titles, descriptions, and content. Returns up to 5 matching prompts with sample image URLs. Great for finding prompts for video thumbnails, ad creatives, social media visuals, and more.",
  {
    query: z
      .string()
      .describe("Search keyword(s) to find matching prompts (case-insensitive)"),
    category: z
      .string()
      .optional()
      .describe(
        'Category slug to search in (e.g. "youtube-thumbnail", "product-marketing"). Omit to search all categories.'
      ),
    limit: z
      .number()
      .optional()
      .default(5)
      .describe("Maximum number of results to return (default 5, max 10)"),
  },
  async ({ query, category, limit }) => {
    const promptsDir = getPromptsDir();
    const manifestPath = path.join(promptsDir, "manifest.json");
    const raw = await fs.readFile(manifestPath, "utf-8");
    const manifest: Manifest = JSON.parse(raw);

    const maxResults = Math.min(limit, 10);
    const queryLower = query.toLowerCase();
    const matches: PromptEntry[] = [];

    const categoriesToSearch = category
      ? manifest.categories.filter((c) => c.slug === category)
      : manifest.categories;

    if (category && categoriesToSearch.length === 0) {
      return {
        content: [
          {
            type: "text",
            text: `Category "${category}" not found. Use prompt_categories to see available categories.`,
          },
        ],
      };
    }

    for (const cat of categoriesToSearch) {
      if (matches.length >= maxResults) break;

      const filePath = path.join(promptsDir, cat.file);
      try {
        const data = await fs.readFile(filePath, "utf-8");
        const prompts: PromptEntry[] = JSON.parse(data);

        for (const p of prompts) {
          if (matches.length >= maxResults) break;
          const searchText =
            `${p.title} ${p.description} ${p.content}`.toLowerCase();
          if (searchText.includes(queryLower)) {
            matches.push(p);
          }
        }
      } catch {
        // Skip unreadable category files
      }
    }

    if (matches.length === 0) {
      return {
        content: [
          {
            type: "text",
            text: `No prompts matching "${query}" found${category ? ` in category "${category}"` : ""}. Try different keywords or browse categories with prompt_categories.`,
          },
        ],
      };
    }

    const results = matches.map((p, i) => {
      const truncated =
        p.content.length > 100 ? p.content.slice(0, 100) + "..." : p.content;
      const image =
        p.sourceMedia.length > 0
          ? `\n**Sample:** ${p.sourceMedia[0]}`
          : "";
      const refImg = p.needReferenceImages
        ? "\n**Requires reference image:** Yes"
        : "";
      return `### ${i + 1}. ${p.title}\n**Description:** ${p.description}\n**Prompt preview:**\n> ${truncated}\n[View full prompt](https://youmind.com/nano-banana-pro-prompts?id=${p.id})${image}${refImg}`;
    });

    return {
      content: [
        {
          type: "text",
          text: `Found ${matches.length} prompt(s) matching "${query}":\n\n${results.join("\n\n---\n\n")}\n\n---\nPrompts curated from the open community by [YouMind.com](https://youmind.com)`,
        },
      ],
    };
  }
);

// ── Tool: prompt_get ──────────────────────────────────────────────────────────
server.tool(
  "prompt_get",
  "Get a specific prompt by ID from the Nano Banana Pro library. Returns the full prompt text, sample image URL, and metadata. Use after prompt_search to get the complete prompt for image generation.",
  {
    id: z.number().describe("The prompt ID to retrieve"),
  },
  async ({ id }) => {
    const promptsDir = getPromptsDir();
    const manifestPath = path.join(promptsDir, "manifest.json");
    const raw = await fs.readFile(manifestPath, "utf-8");
    const manifest: Manifest = JSON.parse(raw);

    for (const cat of manifest.categories) {
      const filePath = path.join(promptsDir, cat.file);
      try {
        const data = await fs.readFile(filePath, "utf-8");
        const prompts: PromptEntry[] = JSON.parse(data);
        const found = prompts.find((p) => p.id === id);
        if (found) {
          const image =
            found.sourceMedia.length > 0
              ? `\n\n**Sample image:** ${found.sourceMedia[0]}`
              : "";
          const refImg = found.needReferenceImages
            ? "\n**Requires reference image:** Yes"
            : "";
          return {
            content: [
              {
                type: "text",
                text: `### ${found.title}\n\n**Category:** ${cat.title}\n**Description:** ${found.description}\n\n**Full prompt:**\n\`\`\`\n${found.content}\n\`\`\`${image}${refImg}\n\n[View on YouMind](https://youmind.com/nano-banana-pro-prompts?id=${found.id})\n\n---\nPrompts curated from the open community by [YouMind.com](https://youmind.com)`,
              },
            ],
          };
        }
      } catch {
        // Skip unreadable files
      }
    }

    return {
      content: [
        {
          type: "text",
          text: `Prompt with ID ${id} not found. Use prompt_search to find prompts.`,
        },
      ],
    };
  }
);

// ── Start server ──────────────────────────────────────────────────────────────
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error("Server failed to start:", error);
  process.exit(1);
});
