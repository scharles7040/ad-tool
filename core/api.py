"""API wrapper for AdIntelligence Copilot skill.

Exposes core ad analysis functionality as a stateless API that can be called
by Copilot without requiring the Streamlit UI.
"""

import json
from datetime import datetime
from typing import Dict, Optional, Any

from core.domain_extractor import extract
from core.google_scraper import scrape_google_ads
from core.facebook_scraper import scrape_facebook_ads
from core.screenshot_manager import download_ad_images
from core.agency_detector import detect_agency, analyze_all_ads
from core.tech_scanner import scan_website_tech


def analyze_domain(
    domain: str,
    max_google_ads: int = 50,
    max_facebook_ads: int = 30,
    scan_tech_stack: bool = True,
) -> Dict[str, Any]:
    """
    Analyze ad presence and technology stack for a domain.

    This is the main entry point for the Copilot skill. It orchestrates
    the complete analysis pipeline and returns structured results.

    Args:
        domain: Website URL or domain (e.g., "nike.com", "https://example.com")
        max_google_ads: Maximum Google ads to retrieve (5-200, default 50)
        max_facebook_ads: Maximum Facebook ads to retrieve (5-100, default 30)
        scan_tech_stack: Whether to scan website technologies (default True)

    Returns:
        Dictionary containing:
        - domain: Extracted domain
        - brand_name: Brand name detected
        - google_ads: Google ads data with metadata
        - facebook_ads: Facebook ads data
        - technologies: Tech stack detection results
        - agency_detection: Agency vs. in-house analysis
        - generated_at: ISO timestamp
        - status: "success" or "error"
    """
    result = {
        "status": "success",
        "generated_at": datetime.now().isoformat(),
        "domain": None,
        "brand_name": None,
        "google_ads": None,
        "facebook_ads": None,
        "technologies": None,
        "agency_detection": {"google": None, "facebook": None},
        "error": None,
    }

    try:
        # Extract domain and brand
        info = extract(domain)
        result["domain"] = info["domain"]
        result["brand_name"] = info["brand_name"]
        domain = info["domain"]
        brand = info["brand_name"]

        # Google Ads
        try:
            google_result = scrape_google_ads(domain, max_ads=max_google_ads)
            result["google_ads"] = _serialize_result(google_result)

            # Download images for Google ads
            if google_result.get("ads"):
                download_ad_images(google_result["ads"], domain)
                analyze_all_ads(google_result["ads"], brand, source="google")

                # Agency detection
                google_agency = detect_agency(
                    advertiser_name=google_result.get("advertiser_name"),
                    brand_name=brand,
                )
                result["agency_detection"]["google"] = google_agency
        except Exception as e:
            result["google_ads"] = {
                "ads": [],
                "error": f"Google ads scrape failed: {str(e)}",
            }

        # Facebook Ads
        try:
            google_adv_name = (
                result.get("google_ads", {}).get("advertiser_name") if result["google_ads"] else None
            )
            facebook_result = scrape_facebook_ads(
                brand_name=brand,
                domain=domain,
                max_ads=max_facebook_ads,
                google_advertiser_name=google_adv_name,
            )
            result["facebook_ads"] = _serialize_result(facebook_result)

            # Agency detection
            if facebook_result.get("ads"):
                analyze_all_ads(facebook_result["ads"], brand, source="facebook")
                first_ad = facebook_result["ads"][0]
                facebook_agency = detect_agency(
                    advertiser_name=first_ad.get("page_name"),
                    brand_name=brand,
                    paid_for_by=first_ad.get("paid_for_by"),
                )
                result["agency_detection"]["facebook"] = facebook_agency
        except Exception as e:
            result["facebook_ads"] = {
                "ads": [],
                "error": f"Facebook ads scrape failed: {str(e)}",
            }

        # Tech Stack
        if scan_tech_stack:
            try:
                tech_result = scan_website_tech(url=f"https://{domain}")
                result["technologies"] = tech_result
            except Exception as e:
                result["technologies"] = {
                    "techs": [],
                    "error": f"Tech scan failed: {str(e)}",
                }

        return result

    except Exception as e:
        result["status"] = "error"
        result["error"] = f"Analysis failed: {str(e)}"
        return result


def _serialize_result(result: Optional[Dict]) -> Optional[Dict]:
    """Make result JSON-serializable by removing bytes fields."""
    if not result:
        return result

    out = dict(result)
    cleaned_ads = []

    for ad in out.get("ads", []):
        # Remove binary data
        ad_copy = {k: v for k, v in ad.items() if not isinstance(v, bytes)}
        ad_copy.pop("thumbnail_bytes", None)
        ad_copy.pop("local_image_path", None)
        ad_copy.pop("screenshot_bytes", None)
        cleaned_ads.append(ad_copy)

    out["ads"] = cleaned_ads
    return out


def get_skill_info() -> Dict[str, Any]:
    """Return metadata about this skill for Copilot."""
    return {
        "name": "AdIntelligence",
        "version": "1.0.0",
        "description": "Analyze ads and tech stack for any domain",
        "author": "Ad Tool Team",
        "capabilities": [
            "scrape_google_ads",
            "scrape_facebook_ads",
            "detect_agency",
            "scan_tech_stack",
        ],
        "inputs": [
            {
                "name": "domain",
                "type": "string",
                "required": True,
                "description": "Website URL or domain",
            },
            {
                "name": "max_google_ads",
                "type": "integer",
                "required": False,
                "default": 50,
            },
            {
                "name": "max_facebook_ads",
                "type": "integer",
                "required": False,
                "default": 30,
            },
            {
                "name": "scan_tech_stack",
                "type": "boolean",
                "required": False,
                "default": True,
            },
        ],
    }
