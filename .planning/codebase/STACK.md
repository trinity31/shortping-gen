# Technology Stack

**Analysis Date:** 2026-04-09

## Languages

**Primary:**
- Markdown - Documentation and workflow specifications
- YAML - Configuration files for Claude skills

## Runtime

**Environment:**
- Claude AI (Claude Max plan for orchestration and sub-agent processing)
- No traditional runtime (JavaScript, Python, Java) required

**Execution Model:**
- Claude Code environments spawned per skill
- Context transfer via Markdown files (workspace/*.md)
- No package manager required for core orchestration

## Frameworks

**Orchestration:**
- Claude Code harness (`.claude/` structure)
- Multi-agent skill system with specialized roles

**Sub-systems:**
- None - Pure AI workflow orchestration

## Key Dependencies

**External Services:**
- **Typecast TTS** - Voice narration generation (₩500-1,000 per video)
- **Google Whisk AI** - AI image generation (free tier)
- **Runway Gen-3** - AI video generation (optional, paid)
- **Pika** - AI video generation alternative (optional, paid)
- **YouTube** - Publishing platform
- **CapCut** - Desktop video editing (manual step)
- **Coupang Partners** - Monetization/affiliate links

**Human Tools:**
- CapCut Desktop App - Video editing application
- Web browsers - YouTube, Google Whisk, Typecast, Coupang Partners access

## Configuration

**Environment:**
- `.claude/settings.json` - Harness configuration
- `.claude/settings.local.json` - Local overrides (if present)
- `.claude/CLAUDE.md` - Project development guidelines

**Skills Configuration:**
- `.claude/skills/{skill-name}/SKILL.md` - Individual skill specifications

**Workspace:**
- `workspace/{YYYY-MM-DD}_{product-name}/` - Video project folders
- All work state stored in Markdown files (no database)

## Platform Requirements

**Development:**
- Claude Code access (Anthropic Claude API)
- File system for workspace management
- Browser access for external tools (YouTube, Typecast, Google Whisk, CapCut, Coupang)

**Production:**
- YouTube Channel (for publishing)
- Typecast account (for TTS production)
- Optional: Runway or Pika account (for advanced video generation)
- Optional: Google Whisk account (free, browser-based)
- Coupang Partners account (for monetization)

## Cost Structure

**Per Video:**
- Claude API calls: ₩0 (covered by Claude Max plan)
- Typecast TTS: ₩500-1,000
- Google Whisk images: ₩0 (free)
- AI video generation: Variable (optional)
- **Total: ₩500-1,500 per video**

**Comparison:**
- Legacy ShortFlow API approach: ₩5,000-15,000 per video
- Current harness: 70-90% cost reduction

## No Build System

- No npm, pip, cargo, or maven required
- No compiled artifacts
- Pure AI workflow orchestration
- Markdown-based context passing

---

*Stack analysis: 2026-04-09*
