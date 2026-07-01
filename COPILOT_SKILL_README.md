# AdIntelligence Copilot Skill

This repository has been configured as a **Copilot Skill** that you can add to your GitHub Copilot workspace.

## What is a Copilot Skill?

A Copilot Skill is a reusable, deployable AI capability that integrates with GitHub Copilot in your workspace. Once added, you can invoke it like:
- **AI Meeting Notes** 
- **TeamsMaestro**
- **AdIntelligence** ← This one

## What AdIntelligence Does

Analyzes ad presence across Google and Facebook for any domain:
- ✅ Scrapes Google Ads Transparency Center
- ✅ Scrapes Facebook Ad Library
- ✅ Detects if ads are agency-managed or in-house
- ✅ Scans website tech stack (CMS, analytics, ad platforms, etc.)
- ✅ Downloads ad creatives and screenshots
- ✅ Generates comprehensive JSON reports

## How to Add This Skill to Your Copilot Workspace

### Option 1: Via GitHub UI (Recommended)
1. Go to your **GitHub Copilot Workspace settings**
2. Navigate to **Skills & Extensions**
3. Click **+ Add Skill**
4. Search for or paste: `https://github.com/scharles7040/ad-tool`
5. Select **AdIntelligence** from the list
6. Click **Install** → **Confirm**

### Option 2: Via Copilot Command
In your Copilot chat, type:
```
/add-skill scharles7040/ad-tool#AdIntelligence
```

### Option 3: Via Manifest (Advanced)
Add to your workspace manifest:
```yaml
skills:
  - name: AdIntelligence
    repo: scharles7040/ad-tool
    entrypoint: core.api:analyze_domain
```

## Using the Skill

Once installed, invoke it in Copilot chat:

**Example 1: Analyze a domain**
```
@AdIntelligence Analyze ads for nike.com
```

**Example 2: Custom parameters**
```
@AdIntelligence Check amazon.com for ads, max 100 Google ads, skip tech scan
```

**Example 3: Competitive analysis**
```
@AdIntelligence What ads is Microsoft running? Who's managing them?
```

### Sample Output
```json
{
  "domain": "nike.com",
  "brand_name": "Nike",
  "google_ads": {
    "count": 47,
    "advertiser_name": "Nike, Inc.",
    "ads": [...]
  },
  "facebook_ads": {
    "count": 23,
    "ads": [...]
  },
  "technologies": {
    "ad_platforms": ["Google Analytics", "Facebook Pixel"],
    "cms": ["WordPress"],
    "analytics": ["Segment"]
  },
  "agency_detection": {
    "google": {
      "is_agency": false,
      "confidence": "high",
      "reason": "Advertiser name matches brand exactly"
    },
    "facebook": {
      "is_agency": true,
      "confidence": "medium",
      "reason": "Paid for by entity different from brand"
    }
  }
}
```

## Architecture

```
core/api.py              ← Copilot entry point
├── domain_extractor.py  ← Parse domain/brand from URL
├── google_scraper.py    ← Query Google Ads Transparency
├── facebook_scraper.py  ← Query Facebook Ad Library
├── agency_detector.py   ← Detect agency vs. in-house
├── tech_scanner.py      ← Scan website technologies
└── screenshot_manager.py ← Download ad images

.github/copilot-skill.yaml ← Skill manifest & configuration
```

## Requirements

- **Python 3.10+**
- **Playwright** (browser automation)
- **Streamlit** (for UI, optional for skill)
- **requests**, **tldextract**, **Pillow**, **webtech**

All dependencies are in `requirements.txt`.

## Configuration

Edit `.github/copilot-skill.yaml` to:
- Change default parameters (max ads, etc.)
- Adjust timeouts or caching behavior
- Add new capabilities or triggers
- Customize display in Copilot workspace

## Deployment

### Deploy to Streamlit Cloud (Optional)
If you want the web UI available alongside the skill:
```bash
streamlit run app.py
```

### Deploy Skill Only (Recommended)
The skill is automatically deployed via GitHub when you:
1. Push to the `main` branch
2. GitHub Actions validates `.github/copilot-skill.yaml`
3. Skill becomes available in Copilot marketplace

## Troubleshooting

**"Skill not found"**
- Ensure repo is public
- Check that `.github/copilot-skill.yaml` is valid YAML
- Verify `core/api.py` has `analyze_domain()` function

**"Timeout errors"**
- Increase `timeout` in `copilot-skill.yaml` (default 300s)
- Reduce `max_google_ads` or `max_facebook_ads`

**"Permission denied"**
- Skill may need API credentials for Google/Facebook
- Check workspace settings → Connected Services

## Next Steps

1. ✅ Skill configuration created
2. ⏳ Push branch to GitHub (`git push origin copilot-skill-setup`)
3. ⏳ Open a Pull Request and merge to `main`
4. ⏳ Add to your Copilot workspace (see "How to Add" above)
5. ⏳ Start using it in chat!

## Support

- **Documentation**: See `README.md` for Streamlit app docs
- **Issues**: Open an issue on GitHub
- **Questions**: Check Copilot workspace docs

---

**Version**: 1.0.0  
**Last Updated**: 2026-07-01
