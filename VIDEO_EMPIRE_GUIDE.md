# Video Empire: 15-20 Automated YouTube/TikTok Channels

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    CONTENT BRAIN                         │
│  Claude/OpenRouter → Script + Strategy + SEO            │
└──────────────┬──────────────────────────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌──────────────┐ ┌──────────────┐
│  VOICE GEN   │ │  VISUAL GEN  │
│  ElevenLabs  │ │  Fal.ai /    │
│  MCP Server  │ │  Pictory /   │
│              │ │  Shotstack   │
└──────┬───────┘ └──────┬───────┘
       │                │
       └───────┬────────┘
               ▼
┌──────────────────────────────────┐
│         VIDEO ASSEMBLY           │
│  FFmpeg / MoviePy / Remotion     │
│  short-video-maker MCP           │
└──────────────┬───────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌──────────────┐ ┌──────────────┐
│   YOUTUBE    │ │   TIKTOK     │
│  Data API    │ │  Uploader    │
│  + Scheduler │ │  + Scheduler │
└──────────────┘ └──────────────┘
```

---

## SECTION 1: MCP Servers to Install

### Tier 1 - MUST HAVE (Install These First)

#### 1. ElevenLabs MCP (Official) - Voice Generation
- **Repo:** https://github.com/elevenlabs/elevenlabs-mcp
- **Install:** `uvx elevenlabs-mcp` or add to claude_desktop_config.json
- **What it does:** Text-to-speech, voice cloning, multi-speaker dialogue, transcription
- **Free tier:** 10k characters/month (enough for ~5-10 short videos)
- **Paid:** $5/mo Starter (30k chars), $22/mo Creator (100k chars)
- **Best for:** Narration for ALL channels

#### 2. Fal.ai MCP Server - Image + Video + Music (600+ Models)
- **Repo:** https://github.com/raveenb/fal-mcp-server
- **Install:** `uvx --from fal-mcp-server fal-mcp`
- **What it does:** Text-to-image, video generation, music composition, audio, image enhancement
- **Models included:** Kling, Luma Ray2, FLUX, Stable Diffusion, and 600+ more
- **Free tier:** Fal.ai gives $10 free credits on signup
- **Best for:** Thumbnails, B-roll clips, background music, AI video segments

#### 3. Short Video Maker MCP - Complete Short-Form Pipeline
- **Repo:** https://github.com/gyoridavid/short-video-maker (962 stars)
- **What it does:** Creates complete short videos for TikTok/Reels/Shorts with captions, transitions, effects
- **Uses:** Remotion under the hood for rendering
- **Best for:** TikTok/Shorts assembly from script → finished video

#### 4. Pictory MCP Server - AI Video from Text
- **Docs:** https://pictory.ai/ai-video-script-generator-8
- **What it does:** Script → storyboard → rendered video with stock footage, captions, music
- **Key tools:** create-storyboard, render-video
- **Works with:** Claude Desktop natively via MCP
- **Best for:** Faceless YouTube videos (explainers, listicles, tutorials)

### Tier 2 - NICE TO HAVE

#### 5. Stability AI MCP - Image Generation
- **Repo:** https://github.com/tadasant/mcp-server-stability-ai
- **What it does:** Generate, edit, upscale images via Stability AI
- **Best for:** Thumbnails, custom artwork

#### 6. Video Agent MCP (h2a-dev) - Full Video Pipeline on Fal.ai
- **Repo:** https://github.com/h2a-dev/video-gen-mcp-monolithic
- **What it does:** Video from images (Kling 2.1, Hailuo), background music, voiceovers, assembly
- **Best for:** High-quality AI-generated video segments

#### 7. blacktop/mcp-tts - Multi-Provider TTS
- **Repo:** https://github.com/blacktop/mcp-tts
- **Install:** `go install github.com/blacktop/mcp-tts@latest`
- **What it does:** TTS via ElevenLabs, Google, OpenAI, macOS say
- **Best for:** Fallback TTS when ElevenLabs quota runs out

#### 8. FFmpeg Video-Audio MCP - Video + Audio Editing
- **Repo:** https://github.com/misbahsy/video-audio-mcp
- **Install:** `pip install video-audio-mcp`
- **What it does:** FFmpeg-powered video AND audio editing, format conversion, trimming, overlays, transitions
- **Best for:** Post-processing, format conversion, adding watermarks

#### 9. YouTube MCP Server - Upload + Analytics
- **Repo:** https://github.com/ZubeidHendricks/youtube-mcp-server
- **Install:** `npx -y @smithery/cli install @ZubeidHendricks/youtube --client claude`
- **What it does:** Full YouTube Data API - upload videos, manage content, analytics
- **Best for:** Automated YouTube uploads directly from Claude

#### 10. TikTok MCP - Content Analysis
- **Repo:** https://github.com/Seym0n/tiktok-mcp
- **What it does:** Analyze TikTok videos for virality factors, get subtitles/context
- **Best for:** Competitor research, trend analysis

#### 11. Google Veo2 MCP - Google Video Gen
- **Repo:** https://github.com/mario-andreschak/mcp-veo2
- **What it does:** Google's Veo2 text-to-video and image-to-video generation
- **Best for:** High-quality AI video clips

---

## SECTION 2: Video Generation APIs (For Custom Pipeline)

| API | Best For | Pricing | API? |
|-----|----------|---------|------|
| **Shotstack** | Programmatic video from JSON templates | $25/mo (50 renders) | REST API |
| **Creatomate** | Template-based video rendering | $18/mo (50 renders) | REST API |
| **JSON2Video** | JSON → video conversion | $15/mo | REST API |
| **Runway Gen-4** | AI video generation (text/image→video) | $15/mo (625 credits) | REST API |
| **HeyGen** | AI avatar talking head videos | $24/mo (3 min) | REST API |
| **Synthesia** | AI avatar + script → video | $22/mo | REST API |
| **D-ID** | Face animation, talking photos | $5.90/mo | REST API |
| **OpusClip** | Long video → multiple short clips | Annual Pro required | REST API (beta) |
| **Pika Labs** | Creative AI video generation | $10/mo | API coming |
| **InVideo AI** | Text → full video with stock footage | $25/mo | Web-based |

### Recommended Stack for Cost Efficiency:
1. **Shotstack or Creatomate** → Template videos (bulk production) ~$25/mo
2. **ElevenLabs** → All voiceovers ~$22/mo
3. **Fal.ai** → AI images/video clips ~$10-30/mo
4. **FFmpeg + MoviePy** → Assembly & post-processing (FREE)

**Total: ~$60-80/month for 15-20 channels**

---

## SECTION 3: Free OpenRouter Models by Task

### For Script Writing
| Model | ID | Context | Why |
|-------|----|---------|-----|
| **Llama 3.1 405B** | `meta-llama/llama-3.1-405b-instruct:free` | 131K | Best free model for long-form writing |
| **DeepSeek R1 0528** | `deepseek/deepseek-r1-0528:free` | 164K | Excellent reasoning for research scripts |
| **Gemini 2.0 Flash** | `google/gemini-2.0-flash-exp:free` | 1M | Huge context for processing source material |

### For SEO / Titles / Descriptions / Tags
| Model | ID | Context | Why |
|-------|----|---------|-----|
| **Grok 4.1 Fast** | `x-ai/grok-4.1-fast:free` | - | Good at SEO/marketing tasks |
| **Gemini 2.5 Flash** | `google/gemini-2.5-flash:free` | - | Fast, good for bulk metadata generation |
| **GLM-4.5-Air** | `zhipu/glm-4.5-air:free` | 131K | Strong multilingual for intl channels |

### For Coding (Pipeline Automation)
| Model | ID | Context | Why |
|-------|----|---------|-----|
| **Devstral 2** | `mistral/devstral-2:free` | 262K | Purpose-built for coding, agentic |
| **MiMo-V2-Flash** | `xiaomi/mimo-v2-flash:free` | 262K | Excellent at code generation |
| **Qwen3-Coder** | `qwen/qwen3-coder:free` | 262K | Strong code model with long context |

### For Image Analysis (Thumbnails, Competitor Research)
| Model | ID | Context | Why |
|-------|----|---------|-----|
| **Gemma 3 27B** | `google/gemma-3-27b-it:free` | 131K | Multimodal, can analyze images |
| **Nemotron Nano VL** | `nvidia/nemotron-nano-vl:free` | 128K | Vision + language model |
| **Qwen 2.5 VL 7B** | `qwen/qwen-2.5-vl-7b-instruct:free` | 33K | Vision model for image understanding |

### Smart Router (Auto-Selects Best Free Model)
| Router | ID | When |
|--------|----|------|
| **Free Models Router** | `openrouter/free` | When you don't care which model, just want free |

---

## SECTION 4: Channel Architecture (15-20 Channels)

### Recommended Niche Distribution

**YouTube Long-Form (8 channels):**
1. AI News & Tutorials (tech)
2. Business/Finance Tips (high CPM)
3. Health & Wellness (evergreen)
4. True Crime / Mystery Stories (high retention)
5. History / Documentaries (evergreen)
6. Top 10 / List Videos (low effort, high volume)
7. Motivational / Self-Improvement (large audience)
8. Science Explained (educational)

**YouTube Shorts + TikTok (8 channels, cross-post):**
9. Quick AI Tips (tech shorts)
10. Money Facts / Finance (high CPM shorts)
11. Psychology Facts (viral potential)
12. Scary Stories / Horror (high retention)
13. Life Hacks / DIY (mass appeal)
14. Sports Highlights + Commentary
15. Cooking / Recipe Shorts
16. Satisfying / ASMR Compilations

**Experimental (2-4 channels):**
17-20. Test new niches, repost best performers, foreign language versions

### Content Cadence Per Channel
- YouTube Long-Form: 3 videos/week = ~24 videos/week total
- YouTube Shorts: 1/day per channel = ~56 shorts/week total
- TikTok: Cross-post all shorts = ~56 TikToks/week total

**Total: ~136 pieces of content per week**

---

## SECTION 5: Automation Pipeline

### Daily Workflow (Automated)

```
6:00 AM  - Cron: Trend research (OpenRouter → trending topics per niche)
6:30 AM  - Cron: Script generation (OpenRouter → 20+ scripts)
7:00 AM  - Cron: Voice generation (ElevenLabs API → audio files)
7:30 AM  - Cron: Visual generation (Fal.ai / Pictory → video segments)
8:00 AM  - Cron: Assembly (FFmpeg/Remotion → final videos)
9:00 AM  - Cron: Thumbnail generation (Fal.ai → FLUX images)
9:30 AM  - Cron: SEO metadata (OpenRouter → titles, descriptions, tags)
10:00 AM - Cron: Upload to YouTube (YouTube Data API v3)
10:30 AM - Cron: Upload to TikTok (tiktok-uploader library)
11:00 AM - Cron: Analytics check (YouTube Analytics API → performance report)
```

### Tech Stack

```python
# Core Pipeline
pipeline/
├── config/
│   ├── channels.yaml          # All 20 channel configs
│   ├── niches.yaml            # Niche-specific prompts
│   └── schedules.yaml         # Upload schedules
├── research/
│   ├── trend_scraper.py       # Google Trends, Reddit, Twitter
│   └── competitor_analyzer.py # Analyze top channels in niche
├── content/
│   ├── script_writer.py       # OpenRouter → scripts
│   ├── seo_optimizer.py       # Titles, descriptions, tags
│   └── thumbnail_gen.py       # Fal.ai FLUX → thumbnails
├── production/
│   ├── voice_gen.py           # ElevenLabs API
│   ├── visual_gen.py          # Fal.ai / Pictory / Shotstack
│   ├── assembler.py           # FFmpeg / MoviePy
│   └── subtitle_gen.py        # Whisper → SRT → burn in
├── distribution/
│   ├── youtube_uploader.py    # YouTube Data API v3
│   ├── tiktok_uploader.py     # tiktok-uploader library
│   └── scheduler.py           # Optimal upload times
├── analytics/
│   ├── performance.py         # Track views, CTR, retention
│   └── optimizer.py           # A/B test thumbnails/titles
└── main.py                    # Orchestrator (cron or n8n)
```

### YouTube Upload (Python)
```python
# Uses google-api-python-client
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

youtube = build('youtube', 'v3', credentials=credentials)
request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": "10 AI Tools That Will Replace Your Job",
            "description": "...",
            "tags": ["ai", "technology", "automation"],
            "categoryId": "28"  # Science & Tech
        },
        "status": {
            "privacyStatus": "public",
            "publishAt": "2026-02-15T10:00:00Z",  # Scheduled
            "selfDeclaredMadeForKids": False
        }
    },
    media_body=MediaFileUpload("video.mp4")
)
response = request.execute()
```

### TikTok Upload (Python)
```python
# Uses tiktok-uploader (wkaisertexas)
# pip install tiktok-uploader
from tiktok_uploader.upload import upload_video

upload_video(
    filename="short.mp4",
    description="AI is changing everything #ai #tech #future",
    cookies="cookies.txt",
    schedule=None  # or datetime for scheduled
)
```

---

## SECTION 6: Cost Breakdown (Monthly)

| Item | Cost | Notes |
|------|------|-------|
| ElevenLabs Creator | $22/mo | 100k chars (~50 videos worth of narration) |
| Fal.ai | $20-30/mo | Images, video clips, music |
| Shotstack or Creatomate | $25/mo | Template-based video rendering |
| YouTube API | FREE | 10,000 quota units/day |
| TikTok Upload | FREE | Browser automation |
| OpenRouter (free models) | FREE | Script writing, SEO |
| VPS (your existing server) | FREE | Already have it |
| FFmpeg + MoviePy | FREE | Open source |
| **TOTAL** | **~$70-80/mo** | |

### Revenue Potential (Conservative, Month 6+)
- 8 YouTube channels × $200-500/mo AdSense = $1,600-4,000/mo
- 8 Shorts/TikTok channels × $50-200/mo = $400-1,600/mo
- Affiliate links in descriptions × 20 channels = $500-2,000/mo
- **Total potential: $2,500-7,600/mo**

---

## SECTION 7: Quick Start (What to Do Right Now)

### Step 1: Install MCP Servers
```bash
# ElevenLabs (voice)
pip install elevenlabs-mcp

# Fal.ai (images, video, music - 600+ models)
pip install fal-mcp-server

# Short Video Maker (TikTok/Shorts assembly)
git clone https://github.com/gyoridavid/short-video-maker
cd short-video-maker && npm install
```

### Step 2: Get API Keys
- ElevenLabs: https://elevenlabs.io (free 10k chars)
- Fal.ai: https://fal.ai (free $10 credits)
- YouTube Data API: https://console.cloud.google.com
- Shotstack: https://shotstack.io (free trial)

### Step 3: Create Google Cloud Project
- Enable YouTube Data API v3
- Create OAuth 2.0 credentials
- Set up service account for automation

### Step 4: Build the Pipeline
- Start with ONE channel, automate it fully
- Scale to 5, then 10, then 20
- Each new channel = copy config + change niche prompts

### Step 5: Create Channel Accounts
- Use Google Workspace for brand accounts ($7/user/mo)
- Or create brand channels under one Google account (free, up to 100)
- TikTok: one phone number per account (use virtual numbers)

---

## SECTION 8: Python Libraries Reference

### Video Creation & Editing
| Library | Install | Best For |
|---------|---------|----------|
| MoviePy | `pip install moviepy` | Programmatic video editing, compositing, text overlays |
| ffmpeg-python | `pip install ffmpeg-python` | Low-level FFmpeg control, large file processing |
| Pillow | `pip install Pillow` | Thumbnail generation, image compositing |

### YouTube Upload
| Library | Install | Best For |
|---------|---------|----------|
| google-api-python-client | `pip install google-api-python-client google-auth-oauthlib` | Official, full-featured, resumable uploads |
| youtube-upload (CLI) | `pip install youtube-upload` | Quick CLI uploads |

### TikTok Upload
| Library | Install | Best For |
|---------|---------|----------|
| tiktok-uploader | `pip install tiktok-uploader` | Browser automation, cookie auth (wkaisertexas) |
| tiktokautouploader | `pip install tiktokautouploader` | Fastest, multi-account, auto captcha (v4.5+) |
| TikTok-Api | `pip install TikTokApi` | READ-ONLY analytics/scraping (cannot upload) |

**Note:** TikTok has no official upload API. All upload libraries use browser automation and can break with updates. `tiktokautouploader` is most actively maintained as of 2026.
