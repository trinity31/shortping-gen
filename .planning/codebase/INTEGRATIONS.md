# External Integrations

**Analysis Date:** 2026-04-09

## APIs & External Services

**AI & Content Generation:**
- **Typecast AI** - TTS voice narration
  - SDK/Client: Web interface (https://typecast.ai)
  - Usage: Audio narration for video scripts
  - Cost: ₩500-1,000 per video (Korean voice support)
  - Integration: Manual upload of script text

- **Google Whisk AI** - AI image generation
  - SDK/Client: Web interface (https://labs.google/fx/tools/whisk)
  - Usage: Product-focused images for video cuts
  - Cost: Free (Google Labs)
  - Integration: Text-to-image prompts from `04_sources.md`

- **Runway Gen-3** - AI video generation (optional)
  - SDK/Client: Web interface (https://runwayml.com)
  - Usage: Hook videos, product demos (optional, premium features)
  - Cost: Subscription-based (varies)
  - Integration: Text prompts with cinematic parameters

- **Pika** - AI video generation alternative
  - SDK/Client: Web interface (alternative to Runway)
  - Usage: Similar to Runway Gen-3
  - Cost: Subscription-based (varies)
  - Integration: Alternative video generation source

**Video Content Sources:**
- **YouTube** - Reference analysis and publishing
  - SDK/Client: Web browser (https://www.youtube.com)
  - Usage: Reference video collection, channel trend analysis
  - Auth: User login (implicit)
  - Integration: Manual video analysis, manual upload to YouTube Studio

- **CapCut** - Video editing application
  - SDK/Client: Desktop application
  - Usage: Final video editing and assembly
  - Cost: Free (with watermark option)
  - Integration: Manual desktop workflow following `05_edit_guide.md`

**E-Commerce & Monetization:**
- **Coupang Partners** - Affiliate/commission links
  - SDK/Client: Web interface (https://partners.coupang.com)
  - Usage: Product purchase links for video descriptions
  - Auth: Coupang account required
  - Integration: Manual link generation, inserted into `업로드_정보.md`

**Referenced Product Sources:**
- **Coupang Store** - Product images/details
  - SDK/Client: Web browser (https://www.coupang.com)
  - Usage: Product image capture, specifications
  - Cost: Free (window shopping only)
  - Integration: Screenshots for source collection

- **Naver Store** - Product images/details (alternative)
  - SDK/Client: Web browser
  - Usage: Product image capture, specifications
  - Cost: Free
  - Integration: Screenshots for source collection

- **ItemScout** - Product trend analysis (optional)
  - SDK/Client: Web interface (https://www.itemscout.io)
  - Usage: Product demand research validation
  - Cost: Free tier available
  - Integration: Manual trend verification

## Data Storage

**No Traditional Database**

- **Workspace Files:** Markdown-based state management
  - Location: `workspace/{YYYY-MM-DD}_{product-name}/`
  - Files: 
    - `01_products.md` - Product research
    - `02_reference.md` - Reference analysis
    - `03_script.md` - Final script
    - `04_sources.md` - Source collection guide
    - `05_edit_guide.md` - CapCut editing guide
    - `업로드_정보.md` - Upload information

- **Project Configuration:** `.claude/` directory
  - `.claude/CLAUDE.md` - Project guidelines
  - `.claude/settings.json` - Harness configuration
  - `.claude/skills/{skill}/SKILL.md` - Skill specifications

## File Storage

- **Local File System Only** - No cloud storage integration
- **Desktop Environment:** CapCut project files and rendered videos
- **Manual Export:** Final MP4 files for YouTube upload

## Caching

- None - Pure AI workflow orchestration

## Authentication & Identity

**Implicit Authentication:**
- Claude API - Handled by Claude Code environment
- YouTube - User browser login
- Typecast - User account login
- Google Whisk - No auth required (free, public tool)
- Coupang Partners - User account login

**No OAuth/API Key Management:**
- All external integrations are manual web-based workflows
- No stored credentials in `.env` or configuration files

## Monitoring & Observability

**Error Tracking:** None

**Logs:**
- Markdown file outputs serve as workflow logs
- Each skill generates timestamped `*.md` files
- No centralized error tracking system
- Manual review of markdown outputs for validation

## CI/CD & Deployment

**Publishing Workflow:**
- **Target:** YouTube Shorts channel
- **Manual Steps:** 
  1. Video editing in CapCut (manual desktop work)
  2. Upload to YouTube Studio (manual upload)
  3. Select "Shorts" format
  4. Add description/title from `업로드_정보.md`
  5. Optional: Schedule publish time

**No Automated Deployment:**
- No GitHub Actions or CI pipeline
- No automatic publishing
- All video uploads manual via YouTube Studio

## Environment Configuration

**Required Access (No Secrets Management):**

- **For Trend Research:** YouTube channel access (for reference analysis)
- **For Script/Source Work:** Google Whisk access (free, no login)
- **For Voice Generation:** Typecast account + KRW balance
- **For Image Sources:** Coupang/Naver web access
- **For Publishing:** YouTube Studio access + Coupang Partners account

**No Environment Variables:**
- No `.env` files in codebase
- All external tool access via manual browser interaction
- Credentials managed outside Claude Code

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- **YouTube Upload:** Manual UI interaction (no webhook)
- **Typecast:** Download audio file manually (no webhook)
- **Coupang Partners:** Copy link manually to markdown (no webhook)

## Workflow Integration Points

**Step-by-Step Service Chain:**

1. **Step 1 (trend-researcher):** YouTube → analyze → `01_products.md`
2. **Step 2 (reference-analyzer):** YouTube → analyze → `02_reference.md`
3. **Step 3 (script-writer):** Claude AI → write → `03_script.md`
4. **Step 4 (source-collector):** Generate prompts → `04_sources.md`
   - Google Whisk (AI images)
   - Coupang (product images)
   - Direct filming (local)
5. **Step 5 (edit-guide):** Generate guide → `05_edit_guide.md`
6. **Step 6 (upload-manager):** Generate metadata → `업로드_정보.md`
   - Coupang Partners link generation

**Manual Production Steps:**
- Typecast: Upload script from `03_script.md` → download TTS audio
- Google Whisk: Use prompts from `04_sources.md` → download images
- CapCut: Follow `05_edit_guide.md` → render MP4
- YouTube Studio: Upload MP4, use `업로드_정보.md` for metadata

---

*Integration audit: 2026-04-09*
