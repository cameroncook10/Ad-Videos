import { execFile } from "node:child_process";
import { promisify } from "node:util";
import * as fs from "node:fs/promises";
import * as path from "node:path";

const execFileAsync = promisify(execFile);

/** Supported video file extensions. */
export const VIDEO_EXTENSIONS = new Set([
  ".mp4",
  ".avi",
  ".mov",
  ".mkv",
  ".webm",
  ".flv",
  ".wmv",
  ".m4v",
  ".mpg",
  ".mpeg",
  ".3gp",
  ".ts",
  ".mts",
]);

/** Check if a file path points to a video file based on extension. */
export function isVideoFile(filePath: string): boolean {
  const ext = path.extname(filePath).toLowerCase();
  return VIDEO_EXTENSIONS.has(ext);
}

/** Resolve and validate a path, ensuring it exists and is within allowed bounds. */
export async function resolveAndValidatePath(
  filePath: string,
  baseDir?: string
): Promise<string> {
  const resolved = path.resolve(filePath);
  if (baseDir) {
    const resolvedBase = path.resolve(baseDir);
    if (!resolved.startsWith(resolvedBase)) {
      throw new Error(
        `Path "${resolved}" is outside the allowed base directory "${resolvedBase}"`
      );
    }
  }
  return resolved;
}

/** Check if ffprobe is available on the system. */
export async function isFfprobeAvailable(): Promise<boolean> {
  try {
    await execFileAsync("ffprobe", ["-version"]);
    return true;
  } catch {
    return false;
  }
}

/** Check if ffmpeg is available on the system. */
export async function isFfmpegAvailable(): Promise<boolean> {
  try {
    await execFileAsync("ffmpeg", ["-version"]);
    return true;
  } catch {
    return false;
  }
}

export interface VideoMetadata {
  filePath: string;
  fileName: string;
  fileSize: number;
  format: string;
  duration: number | null;
  width: number | null;
  height: number | null;
  videoCodec: string | null;
  audioCodec: string | null;
  bitrate: number | null;
  frameRate: string | null;
  createdAt: string;
  modifiedAt: string;
}

/** Get video metadata using ffprobe. */
export async function getVideoMetadata(
  filePath: string
): Promise<VideoMetadata> {
  const resolved = await resolveAndValidatePath(filePath);
  const stat = await fs.stat(resolved);

  if (!stat.isFile()) {
    throw new Error(`"${resolved}" is not a file`);
  }

  const baseMeta: VideoMetadata = {
    filePath: resolved,
    fileName: path.basename(resolved),
    fileSize: stat.size,
    format: path.extname(resolved).slice(1).toLowerCase(),
    duration: null,
    width: null,
    height: null,
    videoCodec: null,
    audioCodec: null,
    bitrate: null,
    frameRate: null,
    createdAt: stat.birthtime.toISOString(),
    modifiedAt: stat.mtime.toISOString(),
  };

  if (!(await isFfprobeAvailable())) {
    return baseMeta;
  }

  try {
    const { stdout } = await execFileAsync("ffprobe", [
      "-v",
      "quiet",
      "-print_format",
      "json",
      "-show_format",
      "-show_streams",
      resolved,
    ]);

    const probe = JSON.parse(stdout);
    const videoStream = probe.streams?.find(
      (s: { codec_type: string }) => s.codec_type === "video"
    );
    const audioStream = probe.streams?.find(
      (s: { codec_type: string }) => s.codec_type === "audio"
    );

    return {
      ...baseMeta,
      duration: probe.format?.duration
        ? parseFloat(probe.format.duration)
        : null,
      width: videoStream?.width ?? null,
      height: videoStream?.height ?? null,
      videoCodec: videoStream?.codec_name ?? null,
      audioCodec: audioStream?.codec_name ?? null,
      bitrate: probe.format?.bit_rate
        ? parseInt(probe.format.bit_rate, 10)
        : null,
      frameRate: videoStream?.r_frame_rate ?? null,
    };
  } catch {
    return baseMeta;
  }
}

/** Format file size to a human-readable string. */
export function formatFileSize(bytes: number): string {
  const units = ["B", "KB", "MB", "GB", "TB"];
  let size = bytes;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  return `${size.toFixed(2)} ${units[unitIndex]}`;
}

/** Format duration in seconds to HH:MM:SS. */
export function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return [h, m, s].map((v) => String(v).padStart(2, "0")).join(":");
}

/** Run an ffmpeg command with given arguments. */
export async function runFfmpeg(
  args: string[]
): Promise<{ stdout: string; stderr: string }> {
  if (!(await isFfmpegAvailable())) {
    throw new Error(
      "ffmpeg is not installed or not in PATH. Install ffmpeg to use video processing features."
    );
  }
  return execFileAsync("ffmpeg", args, { maxBuffer: 10 * 1024 * 1024 });
}
