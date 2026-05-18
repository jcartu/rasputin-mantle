import { mkdir, readdir, readFile, rm, stat, writeFile } from "node:fs/promises";
import { join, relative } from "node:path";

const root = new URL("..", import.meta.url).pathname;
const extensionDir = join(root, "dist", "extension");
const distDir = join(root, "dist");
const CRC_TABLE = createCrcTable();

await copyStaticFiles();
await writeZip(join(distDir, "extension-chrome.zip"), extensionDir);
await writeZip(join(distDir, "extension-edge.zip"), extensionDir);

async function copyStaticFiles() {
  await mkdir(join(extensionDir, "assets", "icons"), { recursive: true });
  await writeFile(join(extensionDir, "manifest.json"), await readFile(join(root, "manifest.json")));
  await writeFile(join(extensionDir, "options.html"), await readFile(join(root, "src", "options.html")));
  await writeFile(join(extensionDir, "sidepanel.html"), await readFile(join(root, "src", "sidepanel.html")));

  const iconNames = await readdir(join(root, "assets", "icons"));
  await Promise.all(
    iconNames.map(async (iconName) => {
      await writeFile(join(extensionDir, "assets", "icons", iconName), await readFile(join(root, "assets", "icons", iconName)));
    }),
  );
}

async function writeZip(outputPath, sourceDir) {
  const files = await listFiles(sourceDir);
  const localParts = [];
  const centralParts = [];
  let offset = 0;

  for (const filePath of files) {
    const data = await readFile(filePath);
    const name = relative(sourceDir, filePath).replace(/\\/g, "/");
    const encodedName = Buffer.from(name);
    const crc = crc32(data);
    const localHeader = makeLocalHeader(encodedName, crc, data.length);
    localParts.push(localHeader, data);
    centralParts.push(makeCentralHeader(encodedName, crc, data.length, offset));
    offset += localHeader.length + data.length;
  }

  const centralSize = centralParts.reduce((total, part) => total + part.length, 0);
  const end = makeEndOfCentralDirectory(files.length, centralSize, offset);
  await writeFile(outputPath, Buffer.concat([...localParts, ...centralParts, end]));
}

async function listFiles(dir) {
  const entries = await readdir(dir);
  const files = [];
  for (const entry of entries) {
    const path = join(dir, entry);
    const info = await stat(path);
    if (info.isDirectory()) {
      files.push(...(await listFiles(path)));
    } else {
      files.push(path);
    }
  }
  return files.sort();
}

function makeLocalHeader(name, crc, size) {
  const header = Buffer.alloc(30 + name.length);
  header.writeUInt32LE(0x04034b50, 0);
  header.writeUInt16LE(20, 4);
  header.writeUInt16LE(0x0800, 6);
  header.writeUInt16LE(0, 8);
  header.writeUInt16LE(0, 10);
  header.writeUInt16LE(0, 12);
  header.writeUInt32LE(crc, 14);
  header.writeUInt32LE(size, 18);
  header.writeUInt32LE(size, 22);
  header.writeUInt16LE(name.length, 26);
  header.writeUInt16LE(0, 28);
  name.copy(header, 30);
  return header;
}

function makeCentralHeader(name, crc, size, offset) {
  const header = Buffer.alloc(46 + name.length);
  header.writeUInt32LE(0x02014b50, 0);
  header.writeUInt16LE(20, 4);
  header.writeUInt16LE(20, 6);
  header.writeUInt16LE(0x0800, 8);
  header.writeUInt16LE(0, 10);
  header.writeUInt16LE(0, 12);
  header.writeUInt16LE(0, 14);
  header.writeUInt32LE(crc, 16);
  header.writeUInt32LE(size, 20);
  header.writeUInt32LE(size, 24);
  header.writeUInt16LE(name.length, 28);
  header.writeUInt16LE(0, 30);
  header.writeUInt16LE(0, 32);
  header.writeUInt16LE(0, 34);
  header.writeUInt16LE(0, 36);
  header.writeUInt32LE(0, 38);
  header.writeUInt32LE(offset, 42);
  name.copy(header, 46);
  return header;
}

function makeEndOfCentralDirectory(count, size, offset) {
  const header = Buffer.alloc(22);
  header.writeUInt32LE(0x06054b50, 0);
  header.writeUInt16LE(0, 4);
  header.writeUInt16LE(0, 6);
  header.writeUInt16LE(count, 8);
  header.writeUInt16LE(count, 10);
  header.writeUInt32LE(size, 12);
  header.writeUInt32LE(offset, 16);
  header.writeUInt16LE(0, 20);
  return header;
}

function crc32(buffer) {
  let crc = 0xffffffff;
  for (const byte of buffer) {
    crc = (crc >>> 8) ^ CRC_TABLE[(crc ^ byte) & 0xff];
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function createCrcTable() {
  const table = new Uint32Array(256);
  for (let index = 0; index < 256; index += 1) {
    let value = index;
    for (let bit = 0; bit < 8; bit += 1) {
      value = value & 1 ? 0xedb88320 ^ (value >>> 1) : value >>> 1;
    }
    table[index] = value >>> 0;
  }
  return table;
}
