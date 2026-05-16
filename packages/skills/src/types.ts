export interface SkillManifestEntry {
  name: string;
  description: string;
  version: string;
  capability: string;
  sha256: string;
  license: string;
  trust_level: "bundled" | "community";
}

export interface SkillManifest {
  skills: SkillManifestEntry[];
}
